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

"""Construct example piezo configurations to simplify testing

These methods make it easier to write tests in packages that depend on
pypiezo.
"""

from .base import get_axis_name as _get_axis_name
from .config import AxisConfig as _AxisConfig
from .config import InputChannelConfig as _InputChannelConfig
from .config import OutputChannelConfig as _OutputChannelConfig
from .config import PiezoConfig as _PiezoConfig


def get_piezo_config(storage=None):
    """Return a default PiezoConfig instance.

    >>> p = get_piezo_config()
    >>> print p.dump()  # doctest: +REPORT_UDIFF
    name: test piezo
    axes:
      0:
        gain: 1.0
        sensitivity: 1.0
        minimum: None
        maximum: None
        channel:
          name: x
          device: /dev/comedi0
          subdevice: -1
          channel: 0
          maxdata: 100
          range: 0
          analog-reference: ground
          conversion-coefficients: 0, 1
          conversion-origin: 0
          inverse-conversion-coefficients: 0, 1
          inverse-conversion-origin: 0
        monitor: 
      1:
        gain: 1.0
        sensitivity: 1.0
        minimum: None
        maximum: None
        channel:
          name: z
          device: /dev/comedi0
          subdevice: -1
          channel: 1
          maxdata: 100
          range: 0
          analog-reference: ground
          conversion-coefficients: 0, 1
          conversion-origin: 0
          inverse-conversion-coefficients: 0, 1
          inverse-conversion-origin: 0
        monitor: 
    inputs:
      0:
        name: deflection
        device: /dev/comedi0
        subdevice: -1
        channel: 0
        maxdata: 100
        range: 0
        analog-reference: ground
        conversion-coefficients: 0, 1
        conversion-origin: 0
        inverse-conversion-coefficients: 0, 1
        inverse-conversion-origin: 0
      1:
        name: temperature
        device: /dev/comedi0
        subdevice: -1
        channel: 1
        maxdata: 100
        range: 0
        analog-reference: ground
        conversion-coefficients: 0, 1
        conversion-origin: 0
        inverse-conversion-coefficients: 0, 1
        inverse-conversion-origin: 0
    >>> _get_axis_name(p['axes'][0])
    'x'
    >>> d = p.select_config('inputs', 'deflection')
    >>> d['name']
    'deflection'
    """
    piezo_config = _PiezoConfig(storage=storage)
    piezo_config['name'] = 'test piezo'
    piezo_config['axes'] = []
    for i,name in enumerate(['x', 'z']):
        axis = _AxisConfig()
        axis['channel'] = _OutputChannelConfig()
        axis['channel']['name'] = name
        axis['channel']['channel'] = i
        axis['channel']['maxdata'] = 100
        axis['channel']['conversion-coefficients'] = (0,1)
        axis['channel']['conversion-origin'] = 0
        axis['channel']['inverse-conversion-coefficients'] = (0,1)
        axis['channel']['inverse-conversion-origin'] = 0
        piezo_config['axes'].append(axis)
    piezo_config['inputs'] = []
    for i,name in enumerate(['deflection', 'temperature']):
        channel = _InputChannelConfig()
        channel = _OutputChannelConfig()
        channel['name'] = name
        channel['channel'] = i
        channel['maxdata'] = 100
        channel['conversion-coefficients'] = (0,1)
        channel['conversion-origin'] = 0
        channel['inverse-conversion-coefficients'] = (0,1)
        channel['inverse-conversion-origin'] = 0
        piezo_config['inputs'].append(channel)
    return piezo_config
