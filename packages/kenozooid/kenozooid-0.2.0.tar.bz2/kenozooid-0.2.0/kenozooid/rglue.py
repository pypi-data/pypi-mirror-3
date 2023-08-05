# Kenozooid - dive planning and analysis toolbox.
#
# Copyright (C) 2009-2011 by Artur Wroblewski <wrobell@pld-linux.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

"""
rpy integration functions.
"""

from functools import partial
from collections import OrderedDict
import itertools

import rpy2.robjects as ro
R = ro.r

import kenozooid

def _vec(c, na, data):
    """
    Create vector for given type using rpy interface.

    :Parameters:
     c
        Vector class, i.e. BoolVector, FloatVector.
     na
        NA value, which should be used for None values.
     data
        Iterable, the source of vector data.
    """
    return c([na if v is None else v for v in data])


def df(cols, vf, data, *mc):
    """
    Create R data frame using rpy interface.

    :Parameters:
     cols
        Column names.
     vf
        Vector constructor function. 
     data
        Iterable of data frame rows (not columns).
    """
    d = ((n, f(d)) for n, f, d in zip(cols, vf, zip(*data)))
    od = OrderedDict(itertools.chain(mc, d))
    return ro.DataFrame(od)


def dives_df(data):
    """
    Create R data frame for dives using rpy interface.
    """
    cols = 'datetime', 'depth', 'duration', 'temp'
    vf = ro.StrVector, float_vec, float_vec, float_vec
    return df(cols, vf, data)


def dive_profiles_df(data):
    """
    Create R data frame for dive profiles using rpy interface.
    """
    cols = 'time', 'depth', 'temp', 'deco_time', 'deco_depth', 'deco_alarm'
    vf = (float_vec, ) * 5 + (bool_vec, )
    d = ro.DataFrame({})
    iv_f = lambda i: ro.IntVector([i])
    return d.rbind(*(df(cols, vf, p, ('dive', iv_f(i))) \
        for i, p in enumerate(data, 1)))


def inject_dive_data(dives):
    """
    Inject dive data into R space. Two variables are created

    kz.dives
        Data frame of dives.

    kz.profiles
        Data frame of dive profiles

    :Parameters:
     dives
        Iterator of dive data: (dive, profile).
    """
    d, p = zip(*dives)
    d_df = dives_df(d)
    p_df = dive_profiles_df(p)

    ro.globalenv['kz.dives'] = d_df
    ro.globalenv['kz.profiles'] = p_df
    ro.globalenv['kz.version'] = kenozooid.__version__
    R('kz.dives$datetime = as.POSIXct(kz.dives$datetime)')


float_vec = partial(_vec, ro.FloatVector, ro.NA_Real)
bool_vec = partial(_vec, ro.BoolVector, ro.NA_Logical)

# vim: sw=4:et:ai
