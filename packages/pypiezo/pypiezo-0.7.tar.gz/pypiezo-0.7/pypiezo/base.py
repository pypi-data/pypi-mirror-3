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

"""Basic piezo control.

Several of the classes defined in this module are simple wrappers for
combining a `pycomedi` class instance (e.g. `Channel`) with the
appropriate config data (e.g. `InputChannelConfig`).  The idea is that
the `h5config`-based config data will make it easy for you to save
your hardware configuration to disk (so that you have a record of what
you did).  It should also make it easy to load your configuration from
the disk (so that you can do the same thing again).  Because this
`h5config` <-> `pycomedi` communication works both ways, you have two
options when you're initializing a class:

1) On your first run, it's probably easiest to setup your channels and
   such using the usual `pycomedi` interface
   (`device.find_subdevice_by_type`, etc.)  After you have setup your
   channels, you can initialize them with a stock config instance, and
   call the `setup_config` method to copy the channel configuration
   into the config file.  Now the config instance is ready to be saved
   to disk.
2) On later runs, you have the option of loading the `pycomedi`
   objects from your old configuration.  After loading the config data
   from disk, initialize your class by passing in a `devices` list,
   but without passing in the `Channel` instances.  The class will
   take care of setting up the channel instances internally,
   recreating your earlier setup.

For examples of how to apply either approach to a particular class,
see that class' docstring.
"""

import math as _math
from time import sleep as _sleep

import numpy as _numpy
from scipy.stats import linregress as _linregress

try:
    import matplotlib as _matplotlib
    import matplotlib.pyplot as _matplotlib_pyplot
    import time as _time  # for timestamping lines on plots
except (ImportError, RuntimeError), e:
    _matplotlib = None
    _matplotlib_import_error = e

from pycomedi.device import Device
from pycomedi.subdevice import StreamingSubdevice
from pycomedi.channel import AnalogChannel
from pycomedi.constant import AREF, TRIG_SRC, SDF, SUBDEVICE_TYPE, UNIT
from pycomedi.utility import inttrig_insn, Reader, Writer

from . import LOG as _LOG
from . import config as _config
from . import package_config as _package_config


def convert_bits_to_volts(config, data):
    """Convert bit-valued data to volts.

    >>> config = _config.ChannelConfig()
    >>> config['conversion-coefficients'] = [1, 2, 3]
    >>> config['conversion-origin'] = -1
    >>> convert_bits_to_volts(config, -1)
    1
    >>> convert_bits_to_volts(
    ...     config, _numpy.array([-1, 0, 1, 2], dtype=_numpy.float))
    array([  1.,   6.,  17.,  34.])
    """
    coefficients = config['conversion-coefficients']
    origin = config['conversion-origin']
    return _numpy.polyval(list(reversed(coefficients)), data-origin)

def convert_volts_to_bits(config, data):
    """Convert bit-valued data to volts.

    >>> config = _config.ChannelConfig()
    >>> config['inverse-conversion-coefficients'] = [1, 2, 3]
    >>> config['inverse-conversion-origin'] = -1
    >>> convert_volts_to_bits(config, -1)
    1
    >>> convert_volts_to_bits(
    ...     config, _numpy.array([-1, 0, 1, 2], dtype=_numpy.float))
    array([  1.,   6.,  17.,  34.])

    Note that the inverse coeffiecient and offset are difficult to
    derive from the forward coefficient and offset.  The current
    Comedilib conversion functions, `comedi_to_physical()` and
    `comedi_from_physical()` take `comedi_polynomial_t` conversion
    arguments.  `comedi_polynomial_t` is defined in `comedilib.h`_,
    and holds a polynomial of length
    `COMEDI_MAX_NUM_POLYNOMIAL_COEFFICIENTS`, currently set to 4.  The
    inverse of this cubic polynomial might be another polynomial, but
    it might also have a more complicated form.  A general inversion
    solution is considered too complicated, so when you're setting up
    your configuration, you should use Comedilib to save both the
    forward and inverse coefficients and offsets.

    .. _comedilib.h: http://www.comedi.org/git?p=comedi/comedilib.git;a=blob;f=include/comedilib.h;hb=HEAD
    """
    origin = config['inverse-conversion-origin']
    inverse_coefficients = config['inverse-conversion-coefficients']
    if len(inverse_coefficients) == 0:
        raise NotImplementedError('cubic polynomial inversion')
    return _numpy.polyval(list(reversed(inverse_coefficients)), data-origin)

def convert_volts_to_meters(config, data):
    """Convert volt-valued data to meters.

    >>> config = _config.AxisConfig()
    >>> config['gain'] = 20.0
    >>> config['sensitivity'] = 8e-9
    >>> convert_volts_to_meters(config, 1)
    1.6e-07
    >>> convert_volts_to_meters(
    ...     config, _numpy.array([1, 6, 17, 34], dtype=_numpy.float))
    ... # doctest: +ELLIPSIS
    array([  1.6...e-07,   9.6...e-07,   2.7...e-06,
             5.4...e-06])
    """
    return data * config['gain'] * config['sensitivity']

def convert_meters_to_volts(config, data):
    """Convert bit-valued data to volts.

    >>> config = _config.AxisConfig()
    >>> config['gain'] = 20.0
    >>> config['sensitivity'] = 8e-9
    >>> convert_meters_to_volts(config, 1.6e-7)
    1.0
    >>> convert_meters_to_volts(
    ...     config, _numpy.array([1.6e-7, 9.6e-7, 2.72e-6, 5.44e-6],
    ...                          dtype=_numpy.float))
    array([  1.,   6.,  17.,  34.])
    """
    return data / (config['gain'] * config['sensitivity'])

def convert_bits_to_meters(axis_config, data):
    """Convert bit-valued data to meters.

    >>> channel_config = _config.ChannelConfig()
    >>> channel_config['conversion-coefficients'] = [1, 2, 3]
    >>> channel_config['conversion-origin'] = -1
    >>> axis_config = _config.AxisConfig()
    >>> axis_config['gain'] = 20.0
    >>> axis_config['sensitivity'] = 8e-9
    >>> axis_config['channel'] = channel_config
    >>> convert_bits_to_meters(axis_config, 1)
    ... # doctest: +ELLIPSIS
    2.7...e-06
    >>> convert_bits_to_meters(
    ...     axis_config, _numpy.array([-1, 0, 1, 2], dtype=_numpy.float))
    ... # doctest: +ELLIPSIS
    array([  1.6...e-07,   9.6...e-07,   2.7...e-06,
             5.4...e-06])
    """
    data = convert_bits_to_volts(axis_config['channel'], data)
    return convert_volts_to_meters(axis_config, data)

def convert_meters_to_bits(axis_config, data):
    """Convert meter-valued data to volts.

    >>> channel_config = _config.ChannelConfig()
    >>> channel_config['inverse-conversion-coefficients'] = [1, 2, 3]
    >>> channel_config['inverse-conversion-origin'] = -1
    >>> axis_config = _config.AxisConfig()
    >>> axis_config['gain'] = 20.0
    >>> axis_config['sensitivity'] = 8e-9
    >>> axis_config['channel'] = channel_config
    >>> convert_meters_to_bits(axis_config, 1.6e-7)
    17.0
    >>> convert_meters_to_bits(
    ...     axis_config,
    ...     _numpy.array([1.6e-7, 9.6e-7, 2.72e-6, 5.44e-6],
    ...                  dtype=_numpy.float))
    array([   17.,   162.,  1009.,  3746.])
    """
    data = convert_meters_to_volts(axis_config, data)
    return convert_volts_to_bits(axis_config['channel'], data)

def get_axis_name(axis_config):
    """Return the name of an axis from the `AxisConfig`

    This is useful, for example, with
    `Config.select_config(get_attribute=get_axis_name)`.
    """
    channel_config = axis_config['channel']
    return channel_config['name']

def load_device(filename, devices):
    """Return an open device from `devices` which has a given `filename`.

    Sometimes a caller will already have the required `Device`, in
    which case we just pull that instance out of `devices`, check that
    it's open, and return it.  Other times, the caller may want us to
    open the device ourselves, so if we can't find an appropriate
    device in `devices`, we create a new one, append it to `devices`
    (so the caller can close it later), and return it.

    You will have to open the `Device` yourself, though, because the
    open device instance should not be held by a particular
    `PiezoAxis` instance.  If you don't want to open devices yourself,
    you can pass in a blank list of devices, and the initialization
    routine will append any necessary-but-missing devices to it.

    >>> from pycomedi.device import Device

    >>> devices = [Device('/dev/comedi0')]
    >>> device = load_device(filename='/dev/comedi0', devices=devices)
    >>> device.filename
    '/dev/comedi0'
    >>> device.file is not None
    True
    >>> device.close()

    >>> devices = []
    >>> device = load_device(filename='/dev/comedi0', devices=devices)
    >>> devices == [device]
    True
    >>> device.filename
    '/dev/comedi0'
    >>> device.file is not None
    True
    >>> device.close()

    We try and return helpful errors when things go wrong:

    >>> device = load_device(filename='/dev/comedi0', devices=None)
    Traceback (most recent call last):
      ...
    TypeError: 'NoneType' object is not iterable
    >>> device = load_device(filename='/dev/comedi0', devices=tuple())
    Traceback (most recent call last):
      ...
    ValueError: none of the available devices ([]) match /dev/comedi0, and we cannot append to ()
    >>> device = load_device(filename='/dev/comediX', devices=[])
    Traceback (most recent call last):
      ...
    PyComediError: comedi_open (/dev/comediX): No such file or directory (None)
    """
    try:
        matching_devices = [d for d in devices if d.filename == filename]
    except TypeError:
        _LOG.error('non-iterable devices? ({})'.format(devices))
        raise
    if matching_devices:
        device = matching_devices[0]
        if device.file is None:
            device.open()
    else:
        device = Device(filename)
        device.open()
        try:
            devices.append(device)  # pass new device back to caller
        except AttributeError:
            device.close()
            raise ValueError(
                ('none of the available devices ({}) match {}, and we '
                 'cannot append to {}').format(
                    [d.filename for d in devices], filename, devices))
    return device

def _load_channel_from_config(channel, devices, subdevice_type):
    c = channel.config  # reduce verbosity
    if not channel.channel:
        device = load_device(filename=c['device'], devices=devices)
        if c['subdevice'] < 0:
            subdevice = device.find_subdevice_by_type(
                subdevice_type, factory=StreamingSubdevice)
        else:
            subdevice = device.subdevice(
                index=c['subdevice'], factory=StreamingSubdevice)
        channel.channel = subdevice.channel(
            index=c['channel'], factory=AnalogChannel,
            aref=c['analog-reference'])
        channel.channel.range = channel.channel.get_range(index=c['range'])
    channel.name = c['name']

def _setup_channel_config(config, channel):
    """Initialize the `ChannelConfig` `config` using the
    `AnalogChannel` `channel`.
    """
    config['device'] = channel.subdevice.device.filename
    config['subdevice'] = channel.subdevice.index
    config['channel'] = channel.index
    config['maxdata'] = channel.get_maxdata()
    config['range'] = channel.range.value
    config['analog-reference'] = AREF.index_by_value(channel.aref.value)
    converter = channel.get_converter()
    config['conversion-origin'
           ] = converter.get_to_physical_expansion_origin()
    config['conversion-coefficients'
           ] = converter.get_to_physical_coefficients()
    config['inverse-conversion-origin'
           ] = converter.get_from_physical_expansion_origin()
    config['inverse-conversion-coefficients'
           ] = converter.get_from_physical_coefficients()


class PiezoAxis (object):
    """A one-dimensional piezoelectric actuator.

    If used, the montoring channel must (as of now) be on the same
    device as the controlling channel.

    >>> from pycomedi.device import Device
    >>> from pycomedi.subdevice import StreamingSubdevice
    >>> from pycomedi.channel import AnalogChannel
    >>> from pycomedi.constant import (AREF, SUBDEVICE_TYPE, UNIT)

    >>> d = Device('/dev/comedi0')
    >>> d.open()

    >>> s_in = d.find_subdevice_by_type(SUBDEVICE_TYPE.ai,
    ...     factory=StreamingSubdevice)
    >>> s_out = d.find_subdevice_by_type(SUBDEVICE_TYPE.ao,
    ...     factory=StreamingSubdevice)

    >>> axis_channel = s_out.channel(
    ...     0, factory=AnalogChannel, aref=AREF.ground)
    >>> monitor_channel = s_in.channel(
    ...     0, factory=AnalogChannel, aref=AREF.diff)
    >>> for chan in [axis_channel, monitor_channel]:
    ...     chan.range = chan.find_range(unit=UNIT.volt, min=-10, max=10)

    >>> config = _config.AxisConfig()
    >>> config.update({'gain':20, 'sensitivity':8e-9})
    >>> config['channel'] = _config.OutputChannelConfig()
    >>> config['monitor'] = _config.InputChannelConfig()
    >>> config['monitor']['device'] = '/dev/comediX'

    >>> p = PiezoAxis(config=config)
    ... # doctest: +NORMALIZE_WHITESPACE
    Traceback (most recent call last):
      ...
    NotImplementedError: piezo axis control and monitor on different devices
     (/dev/comedi0 and /dev/comediX)

    >>> config['monitor']['device'] = config['channel']['device']
    >>> p = PiezoAxis(config=config,
    ...     axis_channel=axis_channel, monitor_channel=monitor_channel)

    >>> p.setup_config()
    >>> print(config['channel'].dump())
    name: 
    device: /dev/comedi0
    subdevice: 1
    channel: 0
    maxdata: 65535
    range: 0
    analog-reference: ground
    conversion-coefficients: -10.0, 0.000305180437934
    conversion-origin: 0.0
    inverse-conversion-coefficients: 0.0, 3276.75
    inverse-conversion-origin: -10.0
    >>> print(config['monitor'].dump())
    name: 
    device: /dev/comedi0
    subdevice: 0
    channel: 0
    maxdata: 65535
    range: 0
    analog-reference: diff
    conversion-coefficients: -10.0, 0.000305180437934
    conversion-origin: 0.0
    inverse-conversion-coefficients: 0.0, 3276.75
    inverse-conversion-origin: -10.0

    >>> convert_bits_to_meters(p.config, 0)
    ... # doctest: +ELLIPSIS
    -1.6...e-06

    Opening from the config alone:

    >>> p = PiezoAxis(config=config)
    >>> p.load_from_config(devices=[d])
    >>> p.axis_channel  # doctest: +ELLIPSIS
    <pycomedi.channel.AnalogChannel object at 0x...>
    >>> p.monitor_channel  # doctest: +ELLIPSIS
    <pycomedi.channel.AnalogChannel object at 0x...>

    >>> d.close()
    """
    def __init__(self, config, axis_channel=None, monitor_channel=None):
        self.config = config
        self.axis_channel = axis_channel
        self.monitor_channel = monitor_channel

    def load_from_config(self, devices):
        c = self.config  # reduce verbosity
        if (c['monitor'] and
            c['channel']['device'] != c['monitor']['device']):
            raise NotImplementedError(
                ('piezo axis control and monitor on different devices '
                 '({} and {})').format(
                    c['channel']['device'], c['monitor']['device']))
        if not self.axis_channel:
            output = OutputChannel(config=c['channel'])
            output.load_from_config(devices=devices)
            self.axis_channel = output.channel
        if c['monitor'] and not self.monitor_channel:
            monitor = InputChannel(config=c['monitor'])
            monitor.load_from_config(devices=devices)
            self.monitor_channel = monitor.channel
        self.name = c['channel']['name']

    def setup_config(self):
        "Initialize the axis (and monitor) configs."
        _setup_channel_config(self.config['channel'], self.axis_channel)
        if self.monitor_channel:
            _setup_channel_config(
                self.config['monitor'], self.monitor_channel)
        if self.config['minimum'] is None:
            self.config['minimum'] = convert_bits_to_volts(
                self.config['channel'], 0)
        if self.config['maximum'] is None:
            self.config['maximum'] = convert_bits_to_volts(
                self.config['channel'], self.axis_channel.get_maxdata())



class OutputChannel(object):
    """An input channel monitoring some interesting parameter.

    >>> from pycomedi.device import Device
    >>> from pycomedi.subdevice import StreamingSubdevice
    >>> from pycomedi.channel import AnalogChannel
    >>> from pycomedi.constant import AREF, SUBDEVICE_TYPE, UNIT

    >>> d = Device('/dev/comedi0')
    >>> d.open()

    >>> s = d.find_subdevice_by_type(SUBDEVICE_TYPE.ao,
    ...     factory=StreamingSubdevice)

    >>> channel = s.channel(0, factory=AnalogChannel, aref=AREF.diff)
    >>> channel.range = channel.find_range(unit=UNIT.volt, min=-10, max=10)

    >>> channel_config = _config.OutputChannelConfig()

    >>> c = OutputChannel(config=channel_config, channel=channel)
    >>> c.setup_config()
    >>> print(channel_config.dump())
    name: 
    device: /dev/comedi0
    subdevice: 1
    channel: 0
    maxdata: 65535
    range: 0
    analog-reference: diff
    conversion-coefficients: -10.0, 0.000305180437934
    conversion-origin: 0.0
    inverse-conversion-coefficients: 0.0, 3276.75
    inverse-conversion-origin: -10.0

    >>> convert_volts_to_bits(c.config, -10)
    0.0

    Opening from the config alone:

    >>> c = OutputChannel(config=channel_config)
    >>> c.load_from_config(devices=[d])
    >>> c.channel  # doctest: +ELLIPSIS
    <pycomedi.channel.AnalogChannel object at 0x...>

    >>> d.close()
    """
    def __init__(self, config, channel=None):
        self.config = config
        self.channel = channel

    def load_from_config(self, devices):
        _load_channel_from_config(
            channel=self, devices=devices, subdevice_type=SUBDEVICE_TYPE.ao)

    def setup_config(self):
        _setup_channel_config(self.config, self.channel)


class InputChannel(object):
    """An input channel monitoring some interesting parameter.

    >>> from pycomedi.device import Device
    >>> from pycomedi.subdevice import StreamingSubdevice
    >>> from pycomedi.channel import AnalogChannel
    >>> from pycomedi.constant import AREF, SUBDEVICE_TYPE, UNIT

    >>> d = Device('/dev/comedi0')
    >>> d.open()

    >>> s = d.find_subdevice_by_type(SUBDEVICE_TYPE.ai,
    ...     factory=StreamingSubdevice)

    >>> channel = s.channel(0, factory=AnalogChannel, aref=AREF.diff)
    >>> channel.range = channel.find_range(unit=UNIT.volt, min=-10, max=10)

    >>> channel_config = _config.InputChannelConfig()

    >>> c = InputChannel(config=channel_config, channel=channel)
    >>> c.setup_config()
    >>> print(channel_config.dump())
    name: 
    device: /dev/comedi0
    subdevice: 0
    channel: 0
    maxdata: 65535
    range: 0
    analog-reference: diff
    conversion-coefficients: -10.0, 0.000305180437934
    conversion-origin: 0.0
    inverse-conversion-coefficients: 0.0, 3276.75
    inverse-conversion-origin: -10.0

    >>> convert_bits_to_volts(c.config, 0)
    -10.0

    Opening from the config alone:

    >>> c = InputChannel(config=channel_config)
    >>> c.load_from_config(devices=[d])
    >>> c.channel  # doctest: +ELLIPSIS
    <pycomedi.channel.AnalogChannel object at 0x...>

    >>> d.close()
    """
    def __init__(self, config, channel=None):
        self.config = config
        self.channel = channel

    def load_from_config(self, devices):
        _load_channel_from_config(
            channel=self, devices=devices, subdevice_type=SUBDEVICE_TYPE.ai)

    def setup_config(self):
        _setup_channel_config(self.config, self.channel)


class Piezo (object):
    """A piezo actuator-controlled experiment.

    >>> from pprint import pprint
    >>> from pycomedi.device import Device
    >>> from pycomedi.subdevice import StreamingSubdevice
    >>> from pycomedi.channel import AnalogChannel
    >>> from pycomedi.constant import AREF, SUBDEVICE_TYPE, UNIT

    >>> d = Device('/dev/comedi0')
    >>> d.open()

    >>> axis_config = _config.AxisConfig()
    >>> axis_config['gain'] = 20.0
    >>> axis_config['sensitivity'] = 8e-9
    >>> axis_config['channel'] = _config.OutputChannelConfig()
    >>> axis_config['channel']['analog-reference'] = AREF.ground
    >>> axis_config['channel']['name'] = 'z'
    >>> axis_config['monitor'] = _config.InputChannelConfig()
    >>> axis_config['monitor']['analog-reference'] = AREF.diff
    >>> a = PiezoAxis(config=axis_config)
    >>> a.load_from_config(devices=[d])
    >>> a.setup_config()

    >>> input_config = _config.InputChannelConfig()
    >>> input_config['analog-reference'] = AREF.diff
    >>> input_config['name'] = 'some-input'
    >>> c = InputChannel(config=input_config)
    >>> c.load_from_config(devices=[d])
    >>> c.setup_config()

    >>> config = _config.PiezoConfig()
    >>> config['name'] = 'Charlie'

    >>> p = Piezo(config=config, axes=[a], inputs=[c])
    >>> p.setup_config()
    >>> inputs = p.read_inputs()
    >>> pprint(inputs)  # doctest: +SKIP
    {'some-input': 34494L, 'z-monitor': 32669L}

    >>> pos = convert_volts_to_bits(p.config['axes'][0]['channel'], 0)
    >>> pos
    32767.5
    >>> p.jump('z', pos)
    >>> p.last_output == {'z': int(pos)}
    True

    :meth:`ramp` raises an error if passed an invalid `data` `dtype`.

    >>> output_data = _numpy.arange(0, int(pos), step=int(pos/10),
    ...     dtype=_numpy.float)
    >>> output_data = output_data.reshape((len(output_data), 1))
    >>> input_data = p.ramp(data=output_data, frequency=10,
    ...     output_names=['z'], input_names=['z-monitor', 'some-input'])
    Traceback (most recent call last):
      ...
    ValueError: output dtype float64 does not match expected <type 'numpy.uint16'>
    >>> output_data = _numpy.arange(0, int(pos), step=int(pos/10),
    ...     dtype=p.channel_dtype('z', direction='output'))
    >>> output_data = output_data.reshape((len(output_data), 1))
    >>> input_data = p.ramp(data=output_data, frequency=10,
    ...     output_names=['z'], input_names=['z-monitor', 'some-input'])
    >>> input_data  # doctest: +SKIP
    array([[    0, 25219],
           [ 3101, 23553],
           [ 6384, 22341],
           [ 9664, 21465],
           [12949, 20896],
           [16232, 20614],
           [19516, 20588],
           [22799, 20801],
           [26081, 21233],
           [29366, 21870],
           [32646, 22686]], dtype=uint16)

    >>> p.last_output == {'z': output_data[-1]}
    True

    >>> data = p.named_ramp(data=output_data, frequency=10,
    ...     output_names=['z'], input_names=['z-monitor', 'some-input'])
    >>> pprint(data)  # doctest: +ELLIPSIS, +SKIP
    {'some-input': array([21666, 20566, ..., 22395], dtype=uint16),
     'z': array([    0,  3276,  ..., 32760], dtype=uint16),
     'z-monitor': array([ 3102,  6384,  ..., 32647], dtype=uint16)}

    Opening from the config alone:

    >>> p = Piezo(config=config)
    >>> p.load_from_config(devices=[d])
    >>> for axis in p.axes:
    ...     print(axis.axis_channel)
    ...     print(axis.monitor_channel)
    ... # doctest: +ELLIPSIS
    <pycomedi.channel.AnalogChannel object at 0x...>
    <pycomedi.channel.AnalogChannel object at 0x...>
    >>> for input in p.inputs:
    ...     print(input.channel)
    ... # doctest: +ELLIPSIS
    <pycomedi.channel.AnalogChannel object at 0x...>

    >>> d.close()
    """
    def __init__(self, config, axes=None, inputs=None):
        self.config=config
        self.axes = axes
        self.inputs = inputs
        self.last_output = {}

    def load_from_config(self, devices):
        if not self.axes:
            self.axes = []
            for config in self.config['axes']:
                axis = PiezoAxis(config=config)
                axis.load_from_config(devices=devices)
                self.axes.append(axis)
            self.last_output.clear()
        if not self.inputs:
            self.inputs = []
            for config in self.config['inputs']:
                input = InputChannel(config=config)
                input.load_from_config(devices=devices)
                self.inputs.append(input)
        self.name = self.config['name']

    def setup_config(self):
        "Initialize the axis and input configs."
        for x in self.axes + self.inputs:
            x.setup_config()
        self.config['axes'] = [x.config for x in self.axes]
        self.config['inputs'] = [x.config for x in self.inputs]

    def axis_by_name(self, name):
        "Get an axis by its name."
        for axis in self.axes:
            if axis.name == name:
                return axis
        raise ValueError(name)

    def input_channel_by_name(self, name):
        "Get an input channel by its name."
        for input_channel in self.inputs:
            if input_channel.name == name:
                return input_channel
        raise ValueError(name)

    def channels(self, direction=None):
        """Iterate through all `(name, channel)` tuples.

        ===========  ===================
        `direction`  Returned channels
        ===========  ===================
        'input'      all input channels
        'output'     all output channels
        None         all channels
        ===========  ===================
        """
        if direction not in ('input', 'output', None):
            raise ValueError(direction)
        for a in self.axes:
            if direction != 'input':
                yield (a.name, a.axis_channel)
            if a.monitor_channel and direction != 'output':
                yield ('%s-monitor' % a.name, a.monitor_channel)
        if direction != 'output':
            for c in self.inputs:
                yield (c.name, c.channel)

    def channel_by_name(self, name, direction=None):
        """Get a channel by its name.

        Setting `direction` (see :meth:`channels`) may allow a more
        efficient search.
        """
        for n,channel in self.channels(direction=direction):
            if n == name:
                return channel
        raise ValueError(name)

    def channel_dtype(self, channel_name, direction=None):
        """Get a channel's data type by name.

        Setting `direction` (see :meth:`channels`) may allow a more
        efficient search.
        """
        channel = self.channel_by_name(name=channel_name, direction=direction)
        return channel.subdevice.get_dtype()

    def read_inputs(self):
        "Read all inputs and return a `name`->`value` dictionary."
        # There is no multi-channel read instruction, so preform reads
        # sequentially.
        ret = dict([(n, c.data_read())
                    for n,c in self.channels(direction='input')])
        _LOG.debug('current position: %s' % ret)
        return ret

    def jump(self, axis_name, position, steps=1, sleep=None):
        "Move the output named `axis_name` to `position`."
        _LOG.debug('jump {} to {} in {} steps'.format(
                axis_name, position, steps))
        if steps > 1:
            try:
                orig_pos = self.last_output[axis_name]
            except KeyError, e:
                _LOG.warn(
                    ("cannot make a soft jump to {} because we don't have a "
                     'last-output position for {}').format(
                        position, axis_name))
                return self.jump(axis_name=axis_name, position=position)
            else:
                for i,pos in enumerate(_numpy.linspace(
                        orig_pos, position, steps+1)[1:]):
                    _LOG.debug('jump {} to {} ({} of {} steps)'.format(
                            axis_name, pos, i, steps))
                    self.jump(axis_name=axis_name, position=pos)
                    if sleep:
                        _sleep(sleep)
                return
        position = int(position)
        channel = self.channel_by_name(name=axis_name)
        channel.data_write(position)
        self.last_output[axis_name] = position

    def ramp(self, data, frequency, output_names, input_names=()):
        """Synchronized IO ramp writing `data` and reading `in_names`.

        Parameters
        ----------
        data : numpy array-like
            Row for each cycle, column for each output channel.
        frequency : float
            Target cycle frequency in Hz.
        output_names : list of strings
            Names of output channels in the same order as the columns
            of `data`.
        input_names : list of strings
            Names of input channels to monitor in the same order as
            the columns of the returned array.
        """
        if len(data.shape) != 2:
            raise ValueError(
                'ramp data must be two dimensional, not %d' % len(data.shape))
        if data.shape[1] != len(output_names):
            raise ValueError(
                'ramp data should have on column for each input, '
                'but has %d columns for %d inputs'
                % (data.shape[1], len(output_names)))
        n_samps = data.shape[0]
        log_string = 'ramp %d samples at %g Hz.  out: %s, in: %s' % (
            n_samps, frequency, output_names, input_names)
        _LOG.debug(log_string)  # _LOG on one line for easy commenting-out
        # TODO: check range?
        output_channels = [self.channel_by_name(name=n, direction='output')
                           for n in output_names]
        inputs = [self.channel_by_name(name=n, direction='input')
                          for n in input_names]

        ao_subdevice = output_channels[0].subdevice
        ai_subdevice = inputs[0].subdevice
        device = ao_subdevice.device

        output_dtype = ao_subdevice.get_dtype()
        if data.dtype != output_dtype:
            raise ValueError('output dtype %s does not match expected %s'
                             % (data.dtype, output_dtype))
        input_data = _numpy.ndarray(
            (n_samps, len(inputs)), dtype=ai_subdevice.get_dtype())

        _LOG.debug('setup ramp commands')
        scan_period_ns = int(1e9 / frequency)
        ai_cmd = ai_subdevice.get_cmd_generic_timed(
            len(inputs), scan_period_ns)
        ao_cmd = ao_subdevice.get_cmd_generic_timed(
            len(output_channels), scan_period_ns)

        ai_cmd.start_src = TRIG_SRC.int
        ai_cmd.start_arg = 0
        ai_cmd.stop_src = TRIG_SRC.count
        ai_cmd.stop_arg = n_samps
        ai_cmd.chanlist = inputs
        #ao_cmd.start_src = TRIG_SRC.ext
        #ao_cmd.start_arg = 18  # NI card AI_START1 internal AI start signal
        ao_cmd.start_src = TRIG_SRC.int
        ao_cmd.start_arg = 0
        ao_cmd.stop_src = TRIG_SRC.count
        ao_cmd.stop_arg = n_samps-1
        ao_cmd.chanlist = output_channels

        ai_subdevice.cmd = ai_cmd
        ao_subdevice.cmd = ao_cmd
        for i in range(3):
            rc = ai_subdevice.command_test()
            if rc is None: break
            _LOG.debug('analog input test %d: %s' % (i, rc))
        for i in range(3):
            rc = ao_subdevice.command_test()
            if rc is None: break
            _LOG.debug('analog output test %d: %s' % (i, rc))

        _LOG.debug('lock subdevices for ramp')
        ao_subdevice.lock()
        try:
            ai_subdevice.lock()
            try:
                _LOG.debug('load ramp commands')
                ao_subdevice.command()
                ai_subdevice.command()

                writer = Writer(ao_subdevice, data)
                writer.start()
                reader = Reader(ai_subdevice, input_data)
                reader.start()

                _LOG.debug('arm analog output')
                device.do_insn(inttrig_insn(ao_subdevice))
                _LOG.debug('trigger ramp (via analog input)')
                device.do_insn(inttrig_insn(ai_subdevice))
                _LOG.debug('ramp running')

                writer.join()
                reader.join()
                _LOG.debug('ramp complete')
            finally:
                #_LOG.debug('AI flags: %s' % ai_subdevice.get_flags())
                ai_subdevice.cancel()
                ai_subdevice.unlock()
        finally:
            # release busy flag, which seems to not be cleared
            # automatically.  See
            #   http://groups.google.com/group/comedi_list/browse_thread/thread/4c7040989197abad/
            #_LOG.debug('AO flags: %s' % ao_subdevice.get_flags())
            ao_subdevice.cancel()
            ao_subdevice.unlock()
            _LOG.debug('unlocked subdevices after ramp')

        for i,name in enumerate(output_names):
            self.last_output[name] = data[-1,i]

        if _package_config['matplotlib']:
            if not _matplotlib:
                raise _matplotlib_import_error
            figure = _matplotlib_pyplot.figure()
            axes = figure.add_subplot(1, 1, 1)
            axes.hold(True)
            timestamp = _time.strftime('%H%M%S')
            axes.set_title('piezo ramp %s' % timestamp)
            for d,names in [(data, output_names),
                            (input_data, input_names)]:
                for i,name in enumerate(names):
                    axes.plot(d[:,i], label=name)
            figure.canvas.draw()
            figure.show()
            if not _matplotlib.is_interactive():
                _matplotlib_pyplot.show()
        return input_data

    def named_ramp(self, data, frequency, output_names, input_names=()):
        input_data = self.ramp(
            data=data, frequency=frequency, output_names=output_names,
            input_names=input_names)
        ret = {}
        for i,name in enumerate(output_names):
            ret[name] = data[:,i]
        for i,name in enumerate(input_names):
            ret[name] = input_data[:,i]
        return ret

    def zero(self, axis_names=None, **kwargs):
        zeros = []
        if axis_names is None:
            axis_names = [axis.name for axis in self.axes]
        for axis_name in axis_names:
            axis = self.axis_by_name(axis_name)
            config = self.config.select_config(
                'axes', axis_name, get_attribute=get_axis_name)['channel']
            zero = convert_volts_to_bits(config, 0)
            zeros.append(zero)
            self.jump(axis_name, zero)
        return zeros
