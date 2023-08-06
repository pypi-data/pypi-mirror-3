# -*- coding: utf-8 -*-
#
# Copyright (C) 2010-2012 W. Trevor King <wking@drexel.edu>
#
# This file is part of Hooke.
#
# Hooke is free software: you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# Hooke is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Hooke.  If not, see <http://www.gnu.org/licenses/>.

"""The ``polymer_fit`` module proviews :class:`PolymerFitPlugin` and
serveral associated :class:`hooke.command.Command`\s for Fitting
velocity-clamp data to various polymer models (WLC, FJC, etc.).
"""

import copy
from Queue import Queue
import logging
import StringIO
import sys

import numpy
from scipy.optimize import newton

from ..command import Command, Argument, Success, Failure
from ..config import Setting
from ..curve import Data
from ..util.callback import is_iterable
from ..util.fit import PoorFit, ModelFitter
from ..util.peak import Peak
from ..util.quickhull import qhull, points_inside_hull
from ..util.si import join_data_label, split_data_label
from . import Plugin, argument_to_setting
from .curve import ColumnAccessCommand, ColumnAddingCommand


kB = 1.3806503e-23  # Joules/Kelvin


def coth(z):
    """Hyperbolic cotangent.

    Examples
    --------
    >>> coth(1.19967874)  # doctest: +ELLIPSIS
    1.199678...

    Notes
    -----
    From `MathWorld`_

    .. math::
      \coth(z) \equiv \frac{\exp(z) + \exp(-z)}{\exp(z) - \exp(-z)}
         = \frac{1}{\tanh(z)}

    .. _MathWorld:
      http://mathworld.wolfram.com/HyperbolicCotangent.html
    """
    return 1.0/numpy.tanh(z)

def arccoth(z):
    """Inverse hyperbolic cotangent.

    Examples
    --------
    >>> arccoth(1.19967874)  # doctest: +ELLIPSIS
    1.199678...
    >>> arccoth(coth(numpy.pi))  # doctest: +ELLIPSIS
    3.1415...

    Notes
    -----
    Inverting from the :func:`definition <coth>`.

    .. math::
      z \equiv \atanh\left( \frac{1}{\coth(z)} \right)
    """
    return numpy.arctanh(1.0/z)

def Langevin(z):
    """Langevin function.

    Examples
    --------
    >>> Langevin(numpy.pi)  # doctest: +ELLIPSIS
    0.685...

    Notes
    -----
    From `Wikipedia`_ or Hatfield [#]_

    .. math::
      L(z) \equiv \coth(z) - \frac{1}{z}

    .. _Wikipedia:
      http://en.wikipedia.org/wiki/Brillouin_and_Langevin_functions#Langevin_Function

    .. [#]: J.W. Hatfield and S.R. Quake
      "Dynamic Properties of an Extended Polymer in Solution."
      Phys. Rev. Lett. 1999.
      doi: `10.1103/PhysRevLett.82.3548 <http://dx.doi.org/10.1103/PhysRevLett.82.3548>`
    """
    return coth(z) - 1.0/z

def inverse_Langevin(z, extreme=1.0 - 1e-8):
    """Inverse Langevin function.

    Parameters
    ----------
    z : float or array_like
        object whose inverse Langevin will be returned
    extreme : float
        value (close to one) for which we assume the inverse is +/-
        infinity.  This avoids problems with Newton-Raphson
        convergence in regions with low slope.

    Examples
    --------
    >>> inverse_Langevin(Langevin(numpy.pi))  # doctest: +ELLIPSIS
    3.14159...
    >>> inverse_Langevin(Langevin(numpy.array([1,2,3])))  # doctest: +ELLIPSIS
    array([ 1.,  2.,  3.])

    Notes
    -----
    We approximate the inverse Langevin via Newton's method
    (:func:`scipy.optimize.newton`).  For the starting point, we take
    the first three terms from the Taylor series (from `Wikipedia`_).

    .. math::
      L^{-1}(z) = 3z + \frac{9}{5}z^3 + \frac{297}{175}z^5 + \dots

    .. _Wikipedia:
      http://en.wikipedia.org/wiki/Brillouin_and_Langevin_functions#Langevin_Function
    """
    if is_iterable(z):
        ret = numpy.ndarray(shape=z.shape, dtype=z.dtype)
        for i,z_i in enumerate(z):
            ret[i] = inverse_Langevin(z_i)
        return ret
    if z > extreme:
        return numpy.inf
    elif z < -extreme:
        return -numpy.inf
    # Catch stdout since sometimes the newton function prints exit
    # messages to stdout, e.g. "Tolerance of %s reached".
    stdout = sys.stdout
    tmp_stdout = StringIO.StringIO()
    sys.stdout = tmp_stdout
    ret = newton(func=lambda x: Langevin(x)-z,
                  x0=3*z + 9./5.*z**3 + 297./175.*z**5,)
    sys.stdout = stdout
    output = tmp_stdout.getvalue()
    return ret

def FJC_fn(x_data, T, L, a):
    """The freely jointed chain model.

    Parameters
    ----------
    x_data : array_like
        x values for which the WLC tension should be calculated.
    T : float
        temperature in Kelvin.
    L : float
        contour length in meters.
    a : float
        Kuhn length in meters.

    Returns
    -------
    f_data : array
        `F(x_data)`.

    Examples
    --------
    >>> FJC_fn(numpy.array([1e-9, 5e-9, 10e-9], dtype=numpy.float),
    ...        T=300, L=15e-9, a=2.5e-10) # doctest: +ELLIPSIS
    array([  3.322...-12,   1.78...e-11,   4.889...e-11])

    Notes
    -----
    The freely jointed chain model is

    .. math::
      F(x) = \frac{k_B T}{a} L^{-1}\left( \frac{x}{L} \right)

    where :math:`L^{-1}` is the :func:`inverse_Langevin`, :math:`a` is
    the Kuhn length, and :math:`L` is the contour length [#]_.  For
    the inverse formulation (:math:`x(F)`), see Ray and Akhremitchev [#]_.


    .. [#]: J.W. Hatfield and S.R. Quake
      "Dynamic Properties of an Extended Polymer in Solution."
      Phys. Rev. Lett. 1999.
      doi: `10.1103/PhysRevLett.82.3548 <http://dx.doi.org/10.1103/PhysRevLett.82.3548>`

    .. [#] C. Ray and B.B. Akhremitchev.
      `"Fitting Force Curves by the Extended Freely Jointed Chain Model" <http://www.chem.duke.edu/~boris/research/force_spectroscopy/fit_efjc.pdf>`
    """
    return kB*T / a * inverse_Langevin(x_data/L)

class FJC (ModelFitter):
    """Fit the data to a freely jointed chain.

    Examples
    --------
    Generate some example data

    >>> T = 300  # Kelvin
    >>> L = 35e-9  # meters
    >>> a = 2.5e-10  # meters
    >>> x_data = numpy.linspace(10e-9, 30e-9, num=20)
    >>> d_data = FJC_fn(x_data, T=T, L=L, a=a)

    Fit the example data with a two-parameter fit (`L` and `a`).

    >>> info = {
    ...     'temperature (K)': T,
    ...     'x data (m)': x_data,
    ...     }
    >>> model = FJC(d_data, info=info, rescale=True)
    >>> outqueue = Queue()
    >>> L,a = model.fit(outqueue=outqueue)
    >>> fit_info = outqueue.get(block=False)
    >>> print L
    3.5e-08
    >>> print a
    2.5e-10

    Fit the example data with a one-parameter fit (`L`).  We introduce
    some error in our fixed Kuhn length for fun.

    >>> info['Kuhn length (m)'] = 2*a
    >>> model = FJC(d_data, info=info, rescale=True)
    >>> L, = model.fit(outqueue=outqueue)
    >>> fit_info = outqueue.get(block=False)
    >>> print L  # doctest: +ELLIPSIS
    3.199...e-08
    """
    def Lp(self, L):
        """To avoid invalid values of `L`, we reparametrize with `Lp`.

        Parameters
        ----------
        L : float
            contour length in meters

        Returns
        -------
        Lp : float
            rescaled version of `L`.

        Examples
        --------
        >>> x_data = numpy.linspace(1e-9, 20e-9, num=10)
        >>> model = FJC(data=x_data, info={'x data (m)':x_data})
        >>> model.Lp(20e-9)  # doctest: +ELLIPSIS
        -inf
        >>> model.Lp(19e-9)  # doctest: +ELLIPSIS
        nan
        >>> model.Lp(21e-9)  # doctest: +ELLIPSIS
        -2.99...
        >>> model.Lp(100e-9)  # doctest: +ELLIPSIS
        1.386...

        Notes
        -----
        The rescaling is designed to limit `L` to values strictly
        greater than the maximum `x` data value, so we use

        .. math::
            L = [\exp(L_p))+1] * x_\text{max}

        which has the inverse

        .. math::
            L_p = \ln(L/x_\text{max}-1)

        This will obviously effect the interpretation of the fit's covariance matrix.
        """
        x_max = self.info['x data (m)'].max()
        return numpy.log(L/x_max - 1)

    def L(self, Lp):
        """Inverse of :meth:`Lp`.

        Parameters
        ----------
        Lp : float
            rescaled version of `L`

        Returns
        -------
        L : float
            contour length in meters

        Examples
        --------
        >>> x_data = numpy.linspace(1e-9, 20e-9, num=10)
        >>> model = FJC(data=x_data, info={'x data (m)':x_data})
        >>> model.L(model.Lp(21e-9))  # doctest: +ELLIPSIS
        2.100...e-08
        >>> model.L(model.Lp(100e-9))  # doctest: +ELLIPSIS
        9.999...e-08
        """
        x_max = self.info['x data (m)'].max()
        return (numpy.exp(Lp)+1)*x_max

    def model(self, params):
        """Extract the relavant arguments and use :func:`FJC_fn`.

        Parameters
        ----------
        params : list of floats
            `[Lp, a]`, where the presence of `a` is optional.
        """
        # setup convenient aliases
        T = self.info['temperature (K)']
        x_data = self.info['x data (m)']
        L = self.L(params[0])
        if len(params) > 1:
            a = abs(params[1])
        else:
            a = self.info['Kuhn length (m)']
        # compute model data
        self._model_data[:] = FJC_fn(x_data, T, L, a)
        return self._model_data

    def fit(self, *args, **kwargs):
        params = super(FJC, self).fit(*args, **kwargs)
        params[0] = self.L(params[0])  # convert Lp -> L
        if len(params) > 1:
            params[1] = abs(params[1])  # take the absolute value of `a`
        return params

    def guess_initial_params(self, outqueue=None):
        """Guess initial fitting parameters.

        Returns
        -------
        Lp : float
            A guess at the reparameterized contour length in meters.
        a : float (optional)
            A guess at the Kuhn length in meters.  If `.info` has a
            setting for `'Kuhn length (m)'`, `a` is not returned.
        """
        x_max = self.info['x data (m)'].max()
        a_given = 'Kuhn length (m)' in self.info
        if a_given:
            a = self.info['Kuhn length (m)']
        else:
            a = x_max / 10.0
        L = 1.5 * x_max
        Lp = self.Lp(L)
        if a_given:
            return [Lp]
        return [Lp, a]


def inverse_FJC_PEG_fn(F_data, T=300, N=1, k=150., Lp=3.58e-10, Lh=2.8e-10, dG=3., a=7e-10):
    """Inverse poly(ethylene-glycol) adjusted extended FJC model.

    Examples
    --------
    >>> kwargs = {'T':300.0, 'N':1, 'k':150.0, 'Lp':3.58e-10, 'Lh':2.8e-10,
    ...           'dG':3.0, 'a':7e-10}
    >>> inverse_FJC_PEG_fn(F_data=200e-12, **kwargs)  # doctest: +ELLIPSIS
    3.487...e-10

    Notes
    -----
    The function is that proposed by F. Oesterhelt, et al. [#]_.

    .. math::
      x(F) = N_\text{S} \cdot \left[
        \left(
            \frac{L_\text{planar}}{
                  \exp\left(-\Delta G/k_B T\right) + 1}
            + \frac{L_\text{helical}}{
                  \exp\left(+\Delta G/k_B T\right) + 1}
          \right) \cdot \left(
            \coth\left(\frac{Fa}{k_B T}\right)
            - \frac{k_B T}{Fa}
          \right)
        + \frac{F}{K_\text{S}}

    where :math:`N_\text{S}` is the number of segments,
    :math:`K_\text{S}` is the segment elasticicty,
    :math:`L_\text{planar}` is the ttt contour length,
    :math:`L_\text{helical}` is the ttg contour length,
    :math:`\Delta G` is the Gibbs free energy difference
     :math:`G_\text{planar}-G_\text{helical}`,
    :math:`a` is the Kuhn length,
    and :math:`F` is the chain tension.

    .. [#]: F. Oesterhelt, M. Rief, and H.E. Gaub.
      "Single molecule force spectroscopy by AFM indicates helical
      structure of poly(ethylene-glycol) in water."
      New Journal of Physics. 1999.
      doi: `10.1088/1367-2630/1/1/006 <http://dx.doi.org/10.1088/1367-2630/1/1/006>`
      (section 4.2)
    """
    kBT = kB * T
    g = (dG - F_data*(Lp-Lh)) / kBT
    z = F_data*a/kBT
    return N * ((Lp/(numpy.exp(-g)+1) + Lh/(numpy.exp(+g)+1)) * (coth(z)-1./z)
                + F_data/k)

def FJC_PEG_fn(x_data, T, N, k, Lp, Lh, dG, a):
    """Poly(ethylene-glycol) adjusted extended FJC model.

    Parameters
    ----------
    z : float or array_like
        object whose inverse Langevin will be returned
    extreme : float
        value (close to one) for which we assume the inverse is +/-
        infinity.  This avoids problems with Newton-Raphson
        convergence in regions with low slope.

    Examples
    --------
    >>> kwargs = {'T':300.0, 'N':1, 'k':150.0, 'Lp':3.58e-10, 'Lh':2.8e-10,
    ...           'dG':3.0, 'a':7e-10}
    >>> FJC_PEG_fn(inverse_FJC_PEG_fn(1e-11, **kwargs), **kwargs)  # doctest: +ELLIPSIS
    9.999...e-12
    >>> FJC_PEG_fn(inverse_FJC_PEG_fn(3.4e-10, **kwargs), **kwargs)  # doctest: +ELLIPSIS
    3.400...e-10
    >>> FJC_PEG_fn(numpy.array([1e-10,2e-10,3e-10]), **kwargs)  # doctest: +ELLIPSIS
    array([  5.207...e-12,   1.257...e-11,   3.636...e-11])
    >>> kwargs['N'] = 123
    >>> FJC_PEG_fn(numpy.array([1e-8,2e-8,3e-8]), **kwargs)  # doctest: +ELLIPSIS
    array([  4.160...e-12,   9.302...e-12,   1.830...e-11])

    Notes
    -----
    We approximate the PEG adjusted eFJC via Newton's method
    (:func:`scipy.optimize.newton`).  For the starting point, we use
    the standard FJC function with an averaged contour length.
    """
    kwargs = {'T':T, 'N':N, 'k':k, 'Lp':Lp, 'Lh':Lh, 'dG':dG, 'a':a}
    if is_iterable(x_data):
        ret = numpy.ndarray(shape=x_data.shape, dtype=x_data.dtype)
        for i,x in enumerate(x_data):
            ret[i] = FJC_PEG_fn(x, **kwargs)
        return ret
    if x_data == 0:
        return 0
    # Approximate with the simple FJC_fn()
    guess = numpy.inf
    L = N*max(Lp, Lh)
    while guess == numpy.inf:
        guess = FJC_fn(x_data, T=T, L=L, a=a)
        L *= 2.0

    fn = lambda f: inverse_FJC_PEG_fn(guess*abs(f), **kwargs) - x_data
    ret = guess*abs(newton(func=fn, x0=1.0))
    return ret

class FJC_PEG (ModelFitter):
    """Fit the data to an poly(ethylene-glycol) adjusted extended FJC.

    Examples
    -------- 
    Generate some example data

    >>> kwargs = {'T':300.0, 'N':123, 'k':150.0, 'Lp':3.58e-10, 'Lh':2.8e-10,
    ...           'dG':3.0, 'a':7e-10}
    >>> x_data = numpy.linspace(10e-9, 30e-9, num=20)
    >>> d_data = FJC_PEG_fn(x_data, **kwargs)

    Fit the example data with a two-parameter fit (`N` and `a`).

    >>> info = {
    ...     'temperature (K)': kwargs['T'],
    ...     'x data (m)': x_data,
    ...     'section elasticity (N/m)': kwargs['k'],
    ...     'planar section length (m)': kwargs['Lp'],
    ...     'helical section length (m)': kwargs['Lh'],
    ...     'Gibbs free energy difference (Gp - Gh) (kBT)': kwargs['dG'],
    ...     }
    >>> model = FJC_PEG(d_data, info=info, rescale=True)
    >>> outqueue = Queue()
    >>> N,a = model.fit(outqueue=outqueue)
    >>> fit_info = outqueue.get(block=False)
    >>> print N
    123.0
    >>> print a
    7e-10

    Fit the example data with a one-parameter fit (`N`).  We introduce
    some error in our fixed Kuhn length for fun.

    >>> info['Kuhn length (m)'] = 2*kwargs['a']
    >>> model = FJC_PEG(d_data, info=info, rescale=True)
    >>> N, = model.fit(outqueue=outqueue)
    >>> fit_info = outqueue.get(block=False)
    >>> print N  # doctest: +ELLIPSIS
    96.931...
    """
    def Lr(self, L):
        """To avoid invalid values of `L`, we reparametrize with `Lr`.

        Parameters
        ----------
        L : float
            contour length in meters

        Returns
        -------
        Lr : float
            rescaled version of `L`.

        Examples
        --------
        >>> x_data = numpy.linspace(1e-9, 20e-9, num=10)
        >>> model = FJC_PEG(data=x_data, info={'x data (m)':x_data})
        >>> model.Lr(20e-9)  # doctest: +ELLIPSIS
        0.0
        >>> model.Lr(19e-9)  # doctest: +ELLIPSIS
        -0.0512...
        >>> model.Lr(21e-9)  # doctest: +ELLIPSIS
        0.0487...
        >>> model.Lr(100e-9)  # doctest: +ELLIPSIS
        1.609...

        Notes
        -----
        The rescaling is designed to limit `L` to values strictly
        greater than zero, so we use

        .. math::
            L = \exp(L_p) * x_\text{max}

        which has the inverse

        .. math::
            L_p = \ln(L/x_\text{max})

        This will obviously effect the interpretation of the fit's covariance matrix.
        """
        x_max = self.info['x data (m)'].max()
        return numpy.log(L/x_max)

    def L(self, Lr):
        """Inverse of :meth:`Lr`.

        Parameters
        ----------
        Lr : float
            rescaled version of `L`

        Returns
        -------
        L : float
            contour length in meters

        Examples
        --------
        >>> x_data = numpy.linspace(1e-9, 20e-9, num=10)
        >>> model = FJC_PEG(data=x_data, info={'x data (m)':x_data})
        >>> model.L(model.Lr(21e-9))  # doctest: +ELLIPSIS
        2.100...e-08
        >>> model.L(model.Lr(100e-9))  # doctest: +ELLIPSIS
        9.999...e-08
        """
        x_max = self.info['x data (m)'].max()
        return numpy.exp(Lr)*x_max

    def _kwargs(self):
        return {
            'T': self.info['temperature (K)'],
            'k': self.info['section elasticity (N/m)'],
            'Lp': self.info['planar section length (m)'],
            'Lh': self.info['helical section length (m)'],
            'dG': self.info['Gibbs free energy difference (Gp - Gh) (kBT)'],
            }

    def model(self, params):
        """Extract the relavant arguments and use :func:`FJC_PEG_fn`.

        Parameters
        ----------
        params : list of floats
            `[N, a]`, where the presence of `a` is optional.
        """
        # setup convenient aliases
        T = self.info['temperature (K)']
        x_data = self.info['x data (m)']
        N = self.L(params[0])
        if len(params) > 1:
            a = abs(params[1])
        else:
            a = self.info['Kuhn length (m)']
        kwargs = self._kwargs()
        # compute model data
        self._model_data[:] = FJC_PEG_fn(x_data, N=N, a=a, **kwargs)
        return self._model_data

    def fit(self, *args, **kwargs):
        params = super(FJC_PEG, self).fit(*args, **kwargs)
        params[0] = self.L(params[0])  # convert Nr -> N
        if len(params) > 1:
            params[1] = abs(params[1])  # take the absolute value of `a`
        return params

    def guess_initial_params(self, outqueue=None):
        """Guess initial fitting parameters.

        Returns
        -------
        N : float
            A guess at the section count.
        a : float (optional)
            A guess at the Kuhn length in meters.  If `.info` has a
            setting for `'Kuhn length (m)'`, `a` is not returned.
        """
        x_max = self.info['x data (m)'].max()
        a_given = 'Kuhn length (m)' in self.info
        if a_given:
            a = self.info['Kuhn length (m)']
        else:
            a = x_max / 10.0
        f_max = self._data.max()
        kwargs = self._kwargs()
        kwargs['a'] = a
        x_section = inverse_FJC_PEG_fn(F_data=f_max, **kwargs)
        N = x_max / x_section;
        Nr = self.Lr(N)
        if a_given:
            return [Nr]
        return [Nr, a]


def WLC_fn(x_data, T, L, p):
    """The worm like chain interpolation model.

    Parameters
    ----------
    x_data : array_like
        x values for which the WLC tension should be calculated.
    T : float
        temperature in Kelvin.
    L : float
        contour length in meters.
    p : float
        persistence length in meters.

    Returns
    -------
    f_data : array
        `F(x_data)`.

    Examples
    --------
    >>> WLC_fn(numpy.array([1e-9, 5e-9, 10e-9], dtype=numpy.float),
    ...        T=300, L=15e-9, p=2.5e-10) # doctest: +ELLIPSIS
    array([  1.717...e-12,   1.070...e-11,   4.418...e-11])

    Notes
    -----
    The function is the simple polynomial worm like chain
    interpolation forumula proposed by C. Bustamante, et al. [#]_.

    .. math::
      F(x) = \frac{k_B T}{p} \left[
        \frac{1}{4}\left( \frac{1}{(1-x/L)^2} - 1 \right)
        + \frac{x}{L}
                             \right]

    .. [#] C. Bustamante, J.F. Marko, E.D. Siggia, and S.Smith.
    "Entropic elasticity of lambda-phage DNA."
    Science. 1994.
    doi: `10.1126/science.8079175 <http://dx.doi.org/10.1126/science.8079175>`
    """
    a = kB * T / p
    scaled_data = x_data / L
    return a * (0.25*((1-scaled_data)**-2 - 1) + scaled_data)

class WLC (ModelFitter):
    """Fit the data to a worm like chain.

    Examples
    --------
    Generate some example data

    >>> T = 300  # Kelvin
    >>> L = 35e-9  # meters
    >>> p = 2.5e-10  # meters
    >>> x_data = numpy.linspace(10e-9, 30e-9, num=20)
    >>> d_data = WLC_fn(x_data, T=T, L=L, p=p)

    Fit the example data with a two-parameter fit (`L` and `p`).

    >>> info = {
    ...     'temperature (K)': T,
    ...     'x data (m)': x_data,
    ...     }
    >>> model = WLC(d_data, info=info, rescale=True)
    >>> outqueue = Queue()
    >>> L,p = model.fit(outqueue=outqueue)
    >>> fit_info = outqueue.get(block=False)
    >>> print L
    3.5e-08
    >>> print p
    2.5e-10

    Fit the example data with a one-parameter fit (`L`).  We introduce
    some error in our fixed persistence length for fun.

    >>> info['persistence length (m)'] = 2*p
    >>> model = WLC(d_data, info=info, rescale=True)
    >>> L, = model.fit(outqueue=outqueue)
    >>> fit_info = outqueue.get(block=False)
    >>> print L  # doctest: +ELLIPSIS
    3.318...e-08
    """
    def Lp(self, L):
        """To avoid invalid values of `L`, we reparametrize with `Lp`.

        Parameters
        ----------
        L : float
            contour length in meters

        Returns
        -------
        Lp : float
            rescaled version of `L`.

        Examples
        --------
        >>> x_data = numpy.linspace(1e-9, 20e-9, num=10)
        >>> model = WLC(data=x_data, info={'x data (m)':x_data})
        >>> model.Lp(20e-9)  # doctest: +ELLIPSIS
        -inf
        >>> model.Lp(19e-9)  # doctest: +ELLIPSIS
        nan
        >>> model.Lp(21e-9)  # doctest: +ELLIPSIS
        -2.99...
        >>> model.Lp(100e-9)  # doctest: +ELLIPSIS
        1.386...

        Notes
        -----
        The rescaling is designed to limit `L` to values strictly
        greater than the maximum `x` data value, so we use

        .. math::
            L = [\exp(L_p))+1] * x_\text{max}

        which has the inverse

        .. math::
            L_p = \ln(L/x_\text{max}-1)

        This will obviously effect the interpretation of the fit's covariance matrix.
        """
        x_max = self.info['x data (m)'].max()
        return numpy.log(L/x_max - 1)

    def L(self, Lp):
        """Inverse of :meth:`Lp`.

        Parameters
        ----------
        Lp : float
            rescaled version of `L`

        Returns
        -------
        L : float
            contour length in meters

        Examples
        --------
        >>> x_data = numpy.linspace(1e-9, 20e-9, num=10)
        >>> model = WLC(data=x_data, info={'x data (m)':x_data})
        >>> model.L(model.Lp(21e-9))  # doctest: +ELLIPSIS
        2.100...e-08
        >>> model.L(model.Lp(100e-9))  # doctest: +ELLIPSIS
        9.999...e-08
        """
        x_max = self.info['x data (m)'].max()
        return (numpy.exp(Lp)+1)*x_max

    def model(self, params):
        """Extract the relavant arguments and use :func:`WLC_fn`.

        Parameters
        ----------
        params : list of floats
            `[Lp, p]`, where the presence of `p` is optional.
        """
        # setup convenient aliases
        T = self.info['temperature (K)']
        x_data = self.info['x data (m)']
        L = self.L(params[0])
        if len(params) > 1:
            p = abs(params[1])
        else:
            p = self.info['persistence length (m)']
        # compute model data
        self._model_data[:] = WLC_fn(x_data, T, L, p)
        return self._model_data

    def fit(self, *args, **kwargs):
        params = super(WLC, self).fit(*args, **kwargs)
        params[0] = self.L(params[0])  # convert Lp -> L
        if len(params) > 1:
            params[1] = abs(params[1])  # take the absolute value of `p`
        return params

    def guess_initial_params(self, outqueue=None):
        """Guess initial fitting parameters.

        Returns
        -------
        Lp : float
            A guess at the reparameterized contour length in meters.
        p : float (optional)
            A guess at the persistence length in meters.  If `.info`
            has a setting for `'persistence length (m)'`, `p` is not
            returned.
        """
        x_max = self.info['x data (m)'].max()
        p_given = 'persistence length (m)' in self.info
        if p_given:
            p = self.info['persistence length (m)']
        else:
            p = x_max / 10.0
        L = 1.5 * x_max
        Lp = self.Lp(L)
        if p_given:
            return [Lp]
        return [Lp, p]


class PolymerFitPlugin (Plugin):
    """Polymer model (WLC, FJC, etc.) fitting.
    """
    def __init__(self):
        super(PolymerFitPlugin, self).__init__(name='polymer_fit')
        self._arguments = [  # For Command initialization
            Argument('polymer model', default='WLC', help="""
Select the default polymer model for 'polymer fit'.  See the
documentation for descriptions of available algorithms.
""".strip()),
            Argument('FJC Kuhn length', type='float', default=4e-10,
                    help='Kuhn length in meters'),
            Argument('FJC_PEG Kuhn length', type='float', default=4e-10,
                    help='Kuhn length in meters'),
            Argument('FJC_PEG elasticity', type='float', default=150.0,
                    help='Elasticity of a PEG segment in Newtons per meter.'),
            Argument('FJC_PEG delta G', type='float', default=3.0, help="""
Gibbs free energy difference between trans-trans-trans (ttt) and
trans-trans-gauche (ttg) PEG states in units of kBT.
""".strip()),
            Argument('FJC_PEG L_helical', type='float', default=2.8e-10,
                    help='Contour length of PEG in the ttg state.'),
            Argument('FJC_PEG L_planar', type='float', default=3.58e-10,
                    help='Contour length of PEG in the ttt state.'),
            Argument('WLC persistence length', type='float', default=4e-10,
                    help='Persistence length in meters'),            
            ]
        self._settings = [
            Setting(section=self.setting_section, help=self.__doc__)]
        for argument in self._arguments:
            self._settings.append(argument_to_setting(
                    self.setting_section, argument))
            argument.default = None # if argument isn't given, use the config.
        self._input_columns = [
            ('distance column', 'cantilever adjusted extension (m)',
             """
Name of the column to use as the surface position input.
""".strip()),
            ('deflection column', 'deflection (N)',
             """
Name of the column to use as the deflection input.
""".strip()),
            ]
        self._commands = [
            PolymerFitCommand(self), PolymerFitPeaksCommand(self),
            TranslateFlatPeaksCommand(self),
            ]

    def dependencies(self):
        return ['vclamp']

    def default_settings(self):
        return self._settings


class PolymerFitCommand (ColumnAddingCommand):
    """Polymer model (WLC, FJC, etc.) fitting.

    Fits an entropic elasticity function to a given chunk of the
    curve.  Fit quality compares the residual with the thermal noise
    (a good fit should be 1 or less).

    Because the models are complicated and varied, you should
    configure the command by setting configuration options instead of
    using command arguments.  TODO: argument_to_setting()
    """
    def __init__(self, plugin):
        super(PolymerFitCommand, self).__init__(
            name='polymer fit',
            columns=plugin._input_columns,
            new_columns=[
                ('output tension column', 'polymer tension',
                 """
Name of the column (without units) to use as the polymer tension output.
""".strip()),
                ],
            arguments=[
                Argument(name='fit parameters info name', type='string',
                         default='polymer fit',
                         help="""
Name (without units) for storing the fit parameters in the `.info` dictionary.
""".strip()),
                Argument(name='bounds', type='point', optional=False, count=2,
                         help="""
Indicies of points bounding the selected data.
""".strip()),
                Argument(name='peak extraction method', default='convex hull',
                         help=(
                        'Select the method used to extract the peak '
                        'deflection from the fitted model.  `convex hull`, '
                        '`peak data`, or `peak model`.')),
                ] + plugin._arguments,
            help=self.__doc__, plugin=plugin)

    def _run(self, hooke, inqueue, outqueue, params):
        self._add_to_command_stack(params)
        log = logging.getLogger('hooke')
        params = self._setup_params(hooke, params)
        data = self._block(hooke, params)
        model = params['polymer model']
        dist_data = self._get_column(
            hooke=hooke, params=params, column_name='distance column')
        def_data = self._get_column(
            hooke=hooke, params=params, column_name='deflection column')
        start,stop = params['bounds']
        tension_data,ps = self.fit_polymer_model(
            params, dist_data, def_data, start, stop, outqueue)
        if params['peak extraction method'] == 'convex hull':
            peak_def,hull = self._convex_hull_deflection(
                distance_data=dist_data, deflection_data=def_data,
                deflection_model=tension_data, start=start, stop=stop,
                outqueue=outqueue)
        elif params['peak extraction method'] == 'peak data':
            peak_def = numpy.nanmax(def_data[start:stop])
        elif params['peak extraction method'] == 'peak model':
            peak_def = numpy.nanmax(tension_data[start:stop])
        else:
            raise ValueError(params['peak extraction method'])
        log.debug('{}: {}'.format(params['peak extraction method'], peak_def))
        ps['peak deflection'] = peak_def
        ps['peak extraction method'] = params['peak extraction method']
        ps['model'] = model
        data.info[params['fit parameters info name']] = ps
        self._set_column(hooke=hooke, params=params,
                         column_name='output tension column',
                         values=tension_data)
        # UGLY HACK:
        with open('/tmp/polymer_fit_peaks.dat', 'a') as f:
            L = ps['contour length (m)']
            x = dist_data[stop-1]
            T = self.plugin.config['temperature']
            p = params['WLC persistence length']
            f.write('\t{:g}\t{:g}\t{:g}'.format(L, x, peak_def))


    def _setup_params(self, hooke, params):
        for key,value in params.items():
            if value == None:  # Use configured default value.
                params[key] = self.plugin.config[key]
        name,def_unit = split_data_label(params['deflection column'])
        params['output tension column'] = join_data_label(
            params['output tension column'], def_unit)
        return params

    def fit_polymer_model(self, params, dist_data, def_data, start, stop,
                          outqueue=None):
        """Railyard for the `fit_*_model` family.

        Uses the `polymer model` configuration setting to call the
        appropriate backend algorithm.
        """
        fn = getattr(self, 'fit_%s_model'
                     % params['polymer model'].replace('-','_'))
        return fn(params, dist_data, def_data, start, stop, outqueue)

    def fit_FJC_model(self, params, dist_data, def_data, start, stop,
                      outqueue=None):
        """Fit the data with :class:`FJC`.
        """
        info = {
            'temperature (K)': self.plugin.config['temperature'],
            'x data (m)': dist_data[start:stop],
            }
        if True:  # TODO: optionally free persistence length
            info['Kuhn length (m)'] = (
                params['FJC Kuhn length'])
        model = FJC(def_data[start:stop], info=info, rescale=True)
        queue = Queue()
        params = model.fit(outqueue=queue)
        if True:  # TODO: if Kuhn length fixed
            a = info['Kuhn length (m)']
        else:
            a = params[1]
        L = params[0]
        T = info['temperature (K)']
        fit_info = queue.get(block=False)
        f_data = numpy.ones(dist_data.shape, dtype=dist_data.dtype) * numpy.nan
        f_data[start:stop] = FJC_fn(dist_data[start:stop], T=T, L=L, a=a)
        return [f_data, fit_info]

    def fit_FJC_PEG_model(self, params, dist_data, def_data, start, stop,
                          outqueue=None):
        """Fit the data with :class:`FJC_PEG`.
        """
        info = {
            'temperature (K)': self.plugin.config['temperature'],
            'x data (m)': dist_data[start:stop],
            # TODO: more info
            }
        if True:  # TODO: optionally free persistence length
            info['Kuhn length (m)'] = (
                params['FJC Kuhn length'])
        model = FJC_PEG(def_data[start:stop], info=info, rescale=True)
        queue = Queue()
        params = model.fit(outqueue=queue)
        if True:  # TODO: if Kuhn length fixed
            a = info['Kuhn length (m)']
        else:
            a = params[1]
        N = params[0]
        T = info['temperature (K)']
        fit_info = queue.get(block=False)
        f_data = numpy.ones(dist_data.shape, dtype=dist_data.dtype) * numpy.nan
        f_data[start:stop] = FJC_PEG_fn(dist_data[start:stop], **kwargs)
        return [f_data, fit_info]

    def fit_WLC_model(self, params, dist_data, def_data, start, stop,
                      outqueue=None):
        """Fit the data with :class:`WLC`.
        """
        info = {
            'temperature (K)': self.plugin.config['temperature'],
            'x data (m)': dist_data[start:stop],
            }
        if True:  # TODO: optionally free persistence length
            info['persistence length (m)'] = (
                params['WLC persistence length'])
        model = WLC(def_data[start:stop], info=info, rescale=True)
        queue = Queue()
        params = model.fit(outqueue=queue)
        if True:  # TODO: if persistence length fixed
            p = info['persistence length (m)']
        else:
            p = params[1]
            info['persistence length (m)'] = p
        L = params[0]
        info['contour length (m)'] = L
        T = info['temperature (K)']
        fit_info = queue.get(block=False)
        info['fit'] = fit_info
        info.pop('x data (m)')
        f_data = numpy.ones(dist_data.shape, dtype=dist_data.dtype) * numpy.nan
        f_data[start:stop] = WLC_fn(dist_data[start:stop], T=T, L=L, p=p)
        return [f_data, info]

    def _convex_hull_deflection(self, distance_data, deflection_data,
                                deflection_model, start, stop, outqueue=None):
        """Return the last model deflection point inside the data hull.

        If the `stop` point is a bit past it's ideal location, the
        rapid rise of some polymer models can lead to artificially
        high peak deflections if the largest distance value is plugged
        into the polymer model directly.  As a more robust estimation
        of the peak deflection, we calculate the convex hull
        surrounding the distance-deflection data and return the last
        model deflection point that is inside that hull.
        """
        distance_data = distance_data[start:stop]
        deflection_data = deflection_data[start:stop]
        deflection_model = deflection_model[start:stop]
        unfolds = []
        hulls = []
        data = numpy.array(
            [[x,y] for x,y in zip(distance_data, deflection_data)])
        model = numpy.array(
            [[x,y] for x,y in zip(distance_data, deflection_model)])
        hull = qhull(data)
        inside = points_inside_hull(hull, model)
        # distance data is not necessarily monatonic
        index_inside = [j for j,i in enumerate(inside) if i is True]
        distance_inside = [(distance_data[i],i) for i in index_inside]
        if distance_inside:
            peak_dist,peak_index = max(distance_inside)
            unfold = deflection_model[peak_index]
        else:  # all model points are outside the hull?!
            unfold = None
        return (unfold, hull)


class PolymerFitPeaksCommand (ColumnAccessCommand):
    """Polymer model (WLC, FJC, etc.) fitting.

    Use :class:`PolymerFitCommand` to fit the each peak in a list of
    previously determined peaks.
    """
    def __init__(self, plugin):
        super(PolymerFitPeaksCommand, self).__init__(
            name='polymer fit peaks',
            columns=plugin._input_columns,
            arguments=[
                Argument(name='peak info name', type='string',
                         default='polymer peaks',
                         help="""
Name for the list of peaks in the `.info` dictionary.
""".strip()),
                Argument(name='peak index', type='int', count=-1, default=None,
                         help="""
Index of the selected peak in the list of peaks.  Use `None` to fit all peaks.
""".strip()),
                ] + plugin._arguments,
            help=self.__doc__, plugin=plugin)

    def _run(self, hooke, inqueue, outqueue, params):
        self._add_to_command_stack(params)
        log = logging.getLogger('hooke')
        data = self._block(hooke, params)
        fit_command = hooke.command_by_name['polymer fit']
        inq = Queue()
        outq = Queue()
        curve = params['curve']
        params['curve'] = None
        p = copy.deepcopy(params)
        p['curve'] = params['curve']
        del(p['peak info name'])
        del(p['peak index'])
        # UGLY HACK:
        with open('/tmp/polymer_fit_peaks.dat', 'a') as f:
            f.write(curve.path)
        for i,peak in enumerate(data.info[params['peak info name']]):
            if params['peak index'] == None or i in params['peak index']:
                p['bounds'] = [peak.index, peak.post_index()]
                p['output tension column'] = peak.name
                p['fit parameters info name'] = peak.name
                p['stack'] = False
                fit_command.run(hooke, inq, outq, **p)
            ret = outq.get()
            if not isinstance(ret, Success):
                raise ret
        # UGLY HACK:
        with open('/tmp/polymer_fit_peaks.dat', 'a') as f:
            f.write('\n')

class TranslateFlatPeaksCommand (ColumnAccessCommand):
    """Translate flat filter peaks into polymer peaks for fitting.

    Use :class:`~hooke.plugin.flatfilt.FlatPeaksCommand` creates a
    list of peaks for regions with large derivatives.  For velocity
    clamp measurements, these regions are usually the rebound phase
    after a protein domain unfolds, the cantilever detaches, etc.
    Because these features occur after the polymer loading phase, we
    need to shift the selected regions back to align them with the
    polymer loading regions.
    """
    def __init__(self, plugin):
        super(TranslateFlatPeaksCommand, self).__init__(
            name='flat peaks to polymer peaks',
            columns=plugin._input_columns,
            arguments=[
                Argument(name='input peak info name', type='string',
                         default='flat filter peaks',
                         help="""
Name for the input peaks in the `.info` dictionary.
""".strip()),
                Argument(name='output peak info name', type='string',
                         default='polymer peaks',
                         help="""
Name for the ouptput peaks in the `.info` dictionary.
""".strip()),
                Argument(name='end offset', type='int', default=-1,
                         help="""
Number of points between the end of a new peak and the start of the old.
""".strip()),
                Argument(name='start fraction', type='float', default=0.2,
                         help="""
Place the start of the new peak at `start_fraction` from the end of
the previous old peak to the end of the new peak.  Because the first
new peak will have no previous old peak, it uses a distance of zero
instead.
""".strip()),
            ] + plugin._arguments,
            help=self.__doc__, plugin=plugin)

    def _run(self, hooke, inqueue, outqueue, params):
        self._add_to_command_stack(params)
        data = self._block(hooke, params)
        dist_data = self._get_column(
            hooke=hooke, params=params, column_name='distance column')
        def_data = self._get_column(
            hooke=hooke, params=params, column_name='deflection column')
        previous_old_stop = numpy.absolute(dist_data).argmin()
        new = []
        try:
            peaks = data.info[params['input peak info name']]
        except KeyError, e:
            raise Failure('No value for %s in %s.info (%s): %s'
                          % (params['input peak info name'], data.info['name'],
                             sorted(data.info.keys()), e))
        for i,peak in enumerate(peaks):
            next_old_start = peak.index
            stop = next_old_start + params['end offset'] 
            dist_start = (
                dist_data[previous_old_stop]
                + params['start fraction']*(
                    dist_data[stop] - dist_data[previous_old_stop]))
            start = numpy.absolute(dist_data - dist_start).argmin()
            p = Peak('polymer peak %d' % i,
                     index=start,
                     values=def_data[start:stop])
            new.append(p)
            previous_old_stop = peak.post_index()
        data.info[params['output peak info name']] = new


# TODO:
# def dist2fit(self):
#     '''Calculates the average distance from data to fit, scaled by
#     the standard deviation of the free cantilever area (thermal
#     noise).
#     '''
