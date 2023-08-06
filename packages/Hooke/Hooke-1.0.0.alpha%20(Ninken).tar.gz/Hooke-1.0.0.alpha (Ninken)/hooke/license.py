# Copyright (C) 2006-2012 A. Seeholzer
#                         Alberto Gomez-Casado <a.gomezcasado@tnw.utwente.nl>
#                         Allen Chen
#                         Fabrizio Benedetti <fabrizio.benedetti.82@gmail.com>
#                         Francesco Musiani
#                         Marco Brucale <marco.brucale@unibo.it>
#                         Massimo Sandal <devicerandom@gmail.com>
#                         Pancaldi Paolo <pancaldi.paolo@gmail.com>
#                         Richard Naud
#                         Rolf Schmidt <rschmidt@alcor.concordia.ca>
#                         W. Trevor King <wking@drexel.edu>
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

import textwrap as _textwrap


LICENSE = """
Copyright (C) 2006-2012 A. Seeholzer
                        Alberto Gomez-Casado <a.gomezcasado@tnw.utwente.nl>
                        Allen Chen
                        Fabrizio Benedetti <fabrizio.benedetti.82@gmail.com>
                        Francesco Musiani
                        Marco Brucale <marco.brucale@unibo.it>
                        Massimo Sandal <devicerandom@gmail.com>
                        Pancaldi Paolo <pancaldi.paolo@gmail.com>
                        Richard Naud
                        Rolf Schmidt <rschmidt@alcor.concordia.ca>
                        W. Trevor King <wking@drexel.edu>

This file is part of Hooke.

Hooke is free software: you can redistribute it and/or modify it under the
terms of the GNU Lesser General Public License as published by the Free
Software Foundation, either version 3 of the License, or (at your option) any
later version.

Hooke is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
details.

You should have received a copy of the GNU Lesser General Public License along
with Hooke.  If not, see <http://www.gnu.org/licenses/>.
""".strip()

def short_license(info, wrap=True, **kwargs):
    paragraphs = [
        'Copyright (C) 2006-2012 A. Seeholzer, Alberto Gomez-Casado <a.gomezcasado@tnw.utwente.nl>, Allen Chen, Fabrizio Benedetti <fabrizio.benedetti.82@gmail.com>, Francesco Musiani, Marco Brucale <marco.brucale@unibo.it>, Massimo Sandal <devicerandom@gmail.com>, Pancaldi Paolo <pancaldi.paolo@gmail.com>, Richard Naud, Rolf Schmidt <rschmidt@alcor.concordia.ca>, W. Trevor King <wking@drexel.edu>' % info,
        'Hooke comes with ABSOLUTELY NO WARRANTY and is licensed under the GNU Lesser General Public License.  For details, %(get-details)s.' % info,
        ]
    if wrap:
        for i,p in enumerate(paragraphs):
            paragraphs[i] = _textwrap.fill(p, **kwargs)
    return '\n\n'.join(paragraphs)
