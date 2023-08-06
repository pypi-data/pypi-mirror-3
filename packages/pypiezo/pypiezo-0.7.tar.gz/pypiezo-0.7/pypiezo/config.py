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

"Piezo configuration"

import h5config.config as _config
import h5config.tools as _h5config_tools

import pycomedi.constant as _constant


class PackageConfig (_h5config_tools.PackageConfig):
    "Configure `pypiezo` module operation"
    settings = _h5config_tools.PackageConfig.settings + [
        _config.BooleanSetting(
            name='matplotlib',
            help='Plot piezo motion using `matplotlib`.',
            default=False),
        ]


class ChannelConfig (_config.Config):
    "Configure a single DAC/ADC channel"
    settings = [
        _config.Setting(
            name='name',
            help="Channel name (so the user will know what it's used for).",
            default=None),
        _config.Setting(
            name='device',
            help='Comedi device.',
            default='/dev/comedi0'),
        _config.IntegerSetting(
            name='subdevice',
            help='Comedi subdevice index.  -1 for automatic detection.',
            default=-1),
        _config.IntegerSetting(
            name='channel',
            help='Subdevice channel index.',
            default=0),
        _config.IntegerSetting(
            name='maxdata',
            help="Channel's maximum bit value."),
        _config.IntegerSetting(
            name='range',
            help="Channel's selected range index.",
            default=0),
        _config.ChoiceSetting(
            name='analog-reference',
            help="Channel's selected analog reference index.",
            choices=[(x.name, x) for x in _constant.AREF]),
        _config.FloatListSetting(
            name='conversion-coefficients',
            help=('Bit to physical unit conversion coefficients starting with '
                  'the constant coefficient.')),
        _config.FloatSetting(
            name='conversion-origin',
            help=('Origin (bit offset) of bit to physical polynomial '
                  'expansion.')),
        _config.FloatListSetting(
            name='inverse-conversion-coefficients',
            help=('Physical unit to bit conversion coefficients starting with '
                  'the constant coefficient.')),
        _config.FloatSetting(
            name='inverse-conversion-origin',
            help=('Origin (physical unit offset) of physical to bit '
                  'polynomial expansion.')),
        ]


class OutputChannelConfig (ChannelConfig):
    pass


class InputChannelConfig (ChannelConfig):
    pass


class AxisConfig (_config.Config):
    "Configure a single piezo axis"
    settings = [
        _config.FloatSetting(
            name='gain',
            help=(
                'Volts applied at piezo per volt output from the DAQ card '
                '(e.g. if your DAQ output is amplified before driving the '
                'piezo),')),
        _config.FloatSetting(
            name='sensitivity',
            help='Meters of piezo deflection per volt applied to the piezo.'),
        _config.FloatSetting(
            name='minimum',
            help='Set a lower limit on allowed output voltage',
            default=None),
        _config.FloatSetting(
            name='maximum',
            help='Set an upper limit on allowed output voltage',
            default=None),
        _config.ConfigSetting(
            name='channel',
            help='Configure the underlying DAC channel.',
            config_class=OutputChannelConfig,
            default=None),
        _config.ConfigSetting(
            name='monitor',
            help='Configure the underlying (optional) ADC monitoring channel.',
            config_class=InputChannelConfig,
            default=None),
        ]


class PiezoConfig (_config.Config):
    "Configure a piezo experiment"
    settings = [
        _config.Setting(
            name='name',
            help="Piezo name (so the user will know what it's used for).",
            default=None),
        _config.ConfigListSetting(
            name='axes',
            help='Configure the underlying axes.',
            config_class=AxisConfig,
            default=None),
        _config.ConfigListSetting(
            name='inputs',
            help='Configure the underlying (optional) ADC monitoring channels.',
            config_class=InputChannelConfig,
            default=None),
        ]


class WiggleConfig (_config.Config):
    "Configure an interference wiggle"
    settings = [
        _config.Setting(
            name='axis',
            help="Name of the axis to wiggle.",
            default='z'),
        _config.Setting(
            name='input',
            help="Name of the channel to watch.",
            default='deflection'),
        _config.FloatSetting(
            name='frequency',
            help="Frequency for a full wiggle cycle (hertz).",
            default=2),
        _config.IntegerSetting(
            name='samples',
            help='Number of samples in a full wiggle cycle.',
            default=1024),
        _config.IntegerSetting(
            name='offset',
            help='Center of the wiggle position (bits)',
            default=None),
        _config.IntegerSetting(
            name='amplitude',
            help='Amplitude of the wiggle sinusoid (bits)',
            default=None),
        _config.IntegerSetting(
            name='wavelength',
            help=('Instead of giving an explicit amplitude, you can specify '
                  'the laser wavelength in meters.  The amplitude will then '
                  'be set to contain about two interference cycles.'),
            default=None),
        ]
