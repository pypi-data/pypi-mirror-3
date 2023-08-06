# Copyright (C) 2011-2012 W. Trevor King <wking@tremily.us>
#
# This file is part of pypiezo.
#
# pypiezo is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# pypiezo is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# pypiezo.  If not, see <http://www.gnu.org/licenses/>.

"""Utilities detecting the position of the sample surface.

TODO: doctests
"""

SLEEP_DURING_SURF_POS_AQUISITION = False # doesn't help

#from time import sleep as _sleep
import numpy as _numpy
from scipy.optimize import leastsq as _leastsq

try:
    import matplotlib as _matplotlib
    import matplotlib.pyplot as _matplotlib_pyplot
    import time as _time  # for timestamping lines on plots
except (ImportError, RuntimeError), e:
    _matplotlib = None
    _matplotlib_import_error = e

from . import LOG as _LOG
from . import package_config as _package_config
from . import base as _base


class SurfaceError (Exception):
    pass


class PoorFit (SurfaceError):
    pass


class PoorGuess (PoorFit):
    pass


class FlatFit (PoorFit):
    "Raised for slope in the non-contact region, or no slope in contact region"
    def __init__(self, left_slope, right_slope):
        self.left_slope = left_slope
        self.right_slope = right_slope
        msg = 'slopes not sufficiently different: %g and %g' % (
            left_slope, right_slope)
        super(FlatFit, self).__init__(msg)


class EdgeKink (PoorFit):
    def __init__(self, kink, edge, window):
        self.kink = kink
        self.edge = edge
        self.window = window
        msg = 'no kink (kink %d not within %d of %d)' % (kink, window, edge)
        super(EdgeKink, self).__init__(self, msg)


def _linspace(*args, **kwargs):
    dtype = kwargs.pop('dtype')
    out = _numpy.linspace(*args, **kwargs)
    return out.reshape((len(out), 1)).astype(dtype)

def _get_min_max_positions(piezo, axis_name, min_position=None,
                           max_position=None):
    output_axis = piezo.axis_by_name(axis_name)
    if min_position is None:
        min_position = _base.convert_volts_to_bits(
            output_axis.config['channel'],
            output_axis.config['minimum'])
    if max_position is None:
        max_position = _base.convert_volts_to_bits(
            output_axis.config['channel'],
            output_axis.config['maximum'])
    return (min_position, max_position)

def get_surface_position_data(piezo, axis_name, max_deflection, steps=2000,
                              frequency=10e3, min_position=None,
                              max_position=None):
    "Measure the distance to the surface"
    _LOG.info('get surface position')
    orig_position = piezo.last_output[axis_name]
    # fully retract the piezo
    min_position,max_position = _get_min_max_positions(
        piezo, axis_name, min_position=min_position, max_position=max_position)
    _LOG.info('retract the piezo to %d' % min_position)
    dtype = piezo.channel_dtype(axis_name, direction='output')
    out = _linspace(orig_position, min_position, steps, dtype=dtype)
    out = out.reshape((len(out), 1)).astype(
        piezo.channel_dtype(axis_name, direction='output'))
    ramp_kwargs = {
        'frequency': frequency,
        'output_names': [axis_name],
        'input_names': ['deflection'],
        }
    ret1 = piezo.named_ramp(data=out, **ramp_kwargs)
    # locate high deflection position
    _LOG.info('approach until there is dangerous deflection (> %d)'
               % max_deflection)
    if SLEEP_DURING_SURF_POS_AQUISITION == True:
        _sleep(.2) # sleeping briefly seems to reduce bounce?
    mtpod = piezo.move_to_pos_or_def(
        axis_name=axis_name, position=max_position, deflection=max_deflection,
        step=(max_position-min_position)/steps, return_data=True)
    high_contact_pos = piezo.last_output[axis_name]
    # fully retract the piezo again
    _LOG.info('retract the piezo to %d again' % min_position)
    if SLEEP_DURING_SURF_POS_AQUISITION == True:
        _sleep(.2)
    out = _linspace(high_contact_pos, min_position, steps, dtype=dtype)
    ret2 = piezo.named_ramp(data=out, **ramp_kwargs)
    # scan to the high contact position
    _LOG.info('ramp in to the deflected position %d' % high_contact_pos)
    if SLEEP_DURING_SURF_POS_AQUISITION == True:
        _sleep(.2)
    out = _linspace(min_position, high_contact_pos, steps, dtype=dtype)
    data = piezo.named_ramp(data=out, **ramp_kwargs)
    if SLEEP_DURING_SURF_POS_AQUISITION == True:
        _sleep(.2)
    # return to the original position
    _LOG.info('return to the original position %d' % orig_position)
    out = _linspace(high_contact_pos, orig_position, steps, dtype=dtype)
    ret3 = piezo.named_ramp(data=out, **ramp_kwargs)
    return {'ret1':ret1, 'mtpod':mtpod, 'ret2':ret2,
            'approach':data, 'ret3':ret3}

def bilinear(x, params):
    """bilinear fit for surface bumps.  Model has two linear regimes
    which meet at x=kink_position and have independent slopes.

    `x` should be a `numpy.ndarray`.
    """
    left_offset,left_slope,kink_position,right_slope = params
    left_mask = x < kink_position
    right_mask = x >= kink_position # = not left_mask
    left_y = left_offset + left_slope*x
    right_y = (left_offset + left_slope*kink_position
               + right_slope*(x-kink_position))
    return left_mask * left_y + right_mask * right_y

def analyze_surface_position_data(
    ddict, min_slope_ratio=10.0, kink_window=None,
    return_all_parameters=False):
    """

    min_slope_ratio : float
        Minimum ratio between the non-contact "left" slope and the
        contact "right" slope.
    kink_window : int (in bits) or None
        Raise `EdgeKink` if the kink is within `kink_window` of the
        minimum or maximum `z` position during the approach.  If
        `None`, a default value of 2% of the approach range is used.
    """
    # uses ddict["approach"] for analysis
    # the others are just along to be plotted
    _LOG.info('analyze surface position data')

    data = ddict['approach']
    # analyze data, using bilinear model
    # y = p0 + p1 x                for x <= p2
    #   = p0 + p1 p2 + p3 (x-p2)   for x >= p2
    dump_before_index = 0 # 25 # HACK!!
    # Generate a reasonable guess...
    start_pos = data['z'].min()
    final_pos = data['z'].max()
    if final_pos == start_pos:
        raise SurfaceError('cannot fit a single approach step (too close?)')
    start_def = data['deflection'].min()
    final_def = data['deflection'].max()
    # start_def and start_pos are probably for 2 different points
    _LOG.info('min deflection {}, max deflection {}'.format(
            start_def, final_def))
    _LOG.info('min position {}, max position {}'.format(start_pos, final_pos))

    left_offset   = start_def
    left_slope    = 0
    kink_position = (final_pos+start_pos)/2.0
    right_slope   = 2.0*(final_def-start_def)/(final_pos-start_pos)
    pstart = [left_offset, left_slope, kink_position, right_slope]
    _LOG.info('guessed params: %s' % pstart)

    offset_scale = (final_pos - start_pos)/100
    left_slope_scale = right_slope/10
    kink_scale = (final_pos-start_pos)/100
    right_slope_scale = right_slope
    scale = [offset_scale, left_slope_scale, kink_scale, right_slope_scale]
    _LOG.info('guessed scale: %s' % scale)

    def residual(p, y, x):
        Y = bilinear(x, p)
        return Y-y
    params,cov,info,mesg,ier = _leastsq(
        residual, pstart,
        args=(data["deflection"][dump_before_index:],
              data["z"][dump_before_index:]),
        full_output=True, maxfev=10000)
    _LOG.info('best fit parameters: %s' % (params,))

    if _package_config['matplotlib']:
        if not _matplotlib:
            raise _matplotlib_import_error
        figure = _matplotlib_pyplot.figure()
        axes = figure.add_subplot(1, 1, 1)
        axes.hold(True)
        timestamp = _time.strftime('%H%M%S')
        axes.set_title('surf_pos %5g %5g %5g %5g' % tuple(params))
        def plot_dict(d, label):
            _pylab.plot(d["z"], d["deflection"], '.',label=label)
        for n,name in [('ret1', 'first retract'),
                       ('mtpod', 'single step in'),
                       ('ret2', 'second retract'),
                       ('approach', 'main approach'),
                       ('ret3', 'return to start')]:
            axes.plot(ddict[n]['z'], ddict[n]['deflection'], label=name)
        def fit_fn(x, params):
            if x <= params[2]:
                return params[0] + params[1]*x
            else:
                return (params[0] + params[1]*params[2]
                        + params[3]*(x-params[2]))
        axes.plot([start_pos, params[2], final_pos],
                  [fit_fn(start_pos, params), fit_fn(params[2], params),
                   fit_fn(final_pos, params)], '-',label='fit')
        #_pylab.legend(loc='best')
        figure.canvas.draw()
        figure.show()
        if not _matplotlib.is_interactive():
            _matplotlib_pyplot.show()

    # check that the fit is reasonable
    # params[1] is slope in non-contact region
    # params[2] is kink position
    # params[3] is slope in contact region
    if kink_window is None:
        kink_window = int(0.02*(final_pos-start_pos))

    if abs(params[1]*min_slope_ratio) > abs(params[3]):
        raise FlatFit(left_slope=params[1], right_slope=params[3])
    if params[2] < start_pos+kink_window:
        raise EdgeKink(kink=params[2], edge=start_pos, window=kink_window)
    if params[2] > final_pos-kink_window:
        raise EdgeKink(kink=params[2], edge=final_pos, window=kink_window)
    _LOG.info('surface position %s' % params[2])
    if return_all_parameters:
        return params
    return params[2]

def get_surface_position(piezo, axis_name, max_deflection, **kwargs):
    ddict = get_surface_position_data(piezo, axis_name, max_deflection)
    return analyze_surface_position_data(ddict, **kwargs)
