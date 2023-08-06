# Copyright (C) 2012 W. Trevor King <wking@tremily.us>
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

"""Utilities for wiggling a the piezo near the surface.

This helps you detect interference between the laser bouncing off the
tip and the surface.  The wiggling continues until you stop it, which
gives you feedback while you reposition the laser to minimize the
interference.  One day we'll all have fancy AFMs with software control
over the laser alignment, but until then, we've got this module
helping you with your thumbscrews.
"""

import time as _time

import numpy as _numpy

try:
    import h5py as _h5py
    import h5config as _h5config
    from h5config.storage.hdf5 import HDF5_Storage as _HDF5_Storage
    from h5config.storage.hdf5 import h5_create_group as _h5_create_group
except ImportError, e:
    _h5py = None
    _h5py_import_error = e

try:
    import matplotlib as _matplotlib
    import matplotlib.pyplot as _matplotlib_pyplot
except (ImportError, RuntimeError), e:
    _matplotlib = None
    _matplotlib_import_error = e

from curses_check_for_keypress import CheckForKeypress as _CheckForKeypress

from . import LOG as _LOG
from . import base as _base
from . import package_config as _package_config


def _setup_config(piezo, config):
    if config['wavelength'] and config['amplitude']:
        log_string = \
            'use either laser_wavelength or amplitude, but not both'
        _LOG.warn(log_string)

    if None in (config['amplitude'], config['offset']):
        output_axis = piezo.axis_by_name(config['axis'])
        maxdata = output_axis.axis_channel.get_maxdata()
        midpoint = int(maxdata/2)
        if config['offset'] is None:
            offset = midpoint
            _LOG.debug(('generated offset for interference wiggle: {}'
                        ).format(config['offset']))
        if config['amplitude'] is None:
            if config['offset'] <= midpoint:
                max_amplitude = int(config['offset'])
            else:
                max_amplitude = int(maxdata-config['offset'])
            offset_meters = _base.convert_bits_to_meters(
                output_axis.config, config['offset'])
            if config['wavelength'] is None:
                config['amplitude'] = 0.5*max_amplitude
            else:
                bit_wavelength = _base.convert_meters_to_bits(
                    output_axis.config,
                    offset_meters + config['wavelength']
                    ) - config['offset']
                config['amplitude'] = 2*bit_wavelength
            _LOG.debug(('generated amplitude for interference wiggle: {}'
                        ).format(config['amplitude']))
            if config['amplitude'] > max_amplitude:
                raise ValueError(
                    'no room for a two wavelength wiggle ({} > {})'.format(
                        config['amplitude'], max_amplitude))

def _construct_output(piezo, config):
    n = config['samples']  # samples in a single oscillation
    out = (config['amplitude']
           * _numpy.sin(_numpy.arange(2*n)*2*_numpy.pi/n)
           + config['offset'])
    # 2*n for 2 periods, so you can judge precision
    out = out.reshape((len(out), 1)).astype(
        piezo.channel_dtype(config['axis'], direction='output'))
    return out

def _setup_datafile(filename, group, piezo, config, output):
    if not _h5py:
        raise _h5py_import_error
    output_axis = afm.piezo.axis_by_name(config['axis'])
    input_channel = afm.piezo.input_channel_by_name(config['input'])
    with _h5py.File(filename, 'w') as f:
        cwg = _h5_create_group(f, group)
        storage = _HDF5_Storage()
        for config_,key in [
            (config, 'config/wiggle'),
            (output.axis.config,
             'config/{}/axis'.format(config['axis'])),
            (input_channel.config,
             'config/{}/channel'.format(config['input']))]:
            if config_ is None:
                continue
            config_cwg = _h5_create_group(cwg, key)
            storage.save(config=config, group=config_cwg)
        cwg['wiggle/raw/{}'.format(config['axis'])] = output

def _update_datafile(filename, group, config, cycle, data):
    timestamp = ('{0}-{1:02d}-{2:02d}T{3:02d}-{4:02d}-{5:02d}'
                 ).format(*_time.localtime())
    with _h5py.File(filename, 'a') as f:
        wiggle_group = _h5_create_group(f, group)
        cwg = _h5_create_group(
            wiggle_group, 'wiggle/{}'.format(cycle))
        cwg['time'] = timestamp
        cwg['raw/{}'.format(config['input'])] = data

def _setup_plot(piezo, config, output):
    if not _matplotlib:
        raise _matplotlib_import_error
    _matplotlib.interactive(True)
    figure = _matplotlib_pyplot.figure()
    axes = figure.add_subplot(1, 1, 1)
    axes.hold(False)
    timestamp = _time.strftime('%H%M%S')
    axes.set_title('wiggle for interference %s' % timestamp)
    plot = axes.plot(output, output, 'b.-')
    figure.canvas.draw()
    figure.show()
    if not _matplotlib.is_interactive():
        _matplotlib_pyplot.show()
    return (figure, axes, plot)

def _update_plot(figure, axes, plot, cycle, data):
    plot[0].set_ydata(data[:,0])
    axes.set_ylim([data.min(), data.max()])
    _matplotlib_pyplot.draw()

def _run_wiggles(piezo, config, figure, axes, plot, output, filename=None,
                 group='/', keypress_test_mode=False):
    scan_frequency = config['frequency'] * config['samples']
    cycle = 0
    c = _CheckForKeypress(test_mode=keypress_test_mode)
    while c.input() == None:
        # input will need processing for multi-segment AFMs...
        data = piezo.ramp(
            output, scan_frequency, output_names=[config['axis']],
            input_names=[config['input']])
        _LOG.debug('completed a wiggle round')
        if filename:
            _update_datafile(
                filename=filename, group=group, config=config,
                cycle=cycle, data=data)
        if plot:
            _update_plot(
                figure=figure, axes=axes, plot=plot, cycle=cycle, data=data)
        cycle += 1

def wiggle_for_interference(
    piezo, config, plot=True, filename=None, group='/',
    keypress_test_mode=False):
    """Output a sine wave and measure interference.

    With a poorly focused or aligned laser, leaked laser light
    reflecting off the surface may interfere with the light
    reflected off the cantilever, causing distance-dependent
    interference with a period roughly half the laser's
    wavelength.  This method wiggles the cantilever near the
    surface and monitors the magnitude of deflection oscillation,
    allowing the operator to adjust the laser alignment in order
    to minimize the interference.

    Modern commercial AFMs with computer-aligned lasers must do
    something like this automatically.
    """
    if _package_config['matplotlib']:
        plot = True
    _setup_config(piezo=piezo, config=config)
    _LOG.debug('oscillate for interference wiggle ({})'.format(config))
    output = _construct_output(piezo=piezo, config=config)

    if filename:
        _setup_datafile(
            filename=filename, group=group, piezo=piezo, config=config,
            output=output)
    if plot:
        interactive = _matplotlib.is_interactive()
        figure,axes,plot_ = _setup_plot(
            piezo=piezo, config=config, output=output)
    else:
        figure = axes = plot_ = None
    _run_wiggles(
        piezo=piezo, config=config, figure=figure, axes=axes, plot=plot_,
        output=output, filename=filename, group=group,
        keypress_test_mode=keypress_test_mode)
    if plot:
        _matplotlib.interactive(interactive)
    piezo.last_output[config['axis']] = output[-1,0]
    _LOG.debug('interference wiggle complete')
