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

"Control of a piezo-based atomic force microscope."

import time as _time

import numpy as _numpy

try:
    import matplotlib as _matplotlib
    import matplotlib.pyplot as _matplotlib_pyplot
except (ImportError, RuntimeError), e:
    _matplotlib = None
    _matplotlib_import_error = e

from . import LOG as _LOG
from . import base as _base
from . import package_config as _package_config
from . import surface as _surface
from . import wiggle as _wiggle


class AFMPiezo (_base.Piezo):
    """A piezo-controlled atomic force microscope.

    This particular class expects a single input channel for measuring
    deflection.  Other subclasses provide support for multi-segment
    deflection measurements.

    >>> from pprint import pprint
    >>> from pycomedi.constant import AREF
    >>> from . import config
    >>> from . import surface

    >>> devices = []

    >>> piezo_config = config.PiezoConfig()
    >>> piezo_config['name'] = 'Molly'
    >>> piezo_config['axes'] = [config.AxisConfig()]
    >>> piezo_config['axes'][0]['channel'] = config.OutputChannelConfig()
    >>> piezo_config['axes'][0]['channel']['analog-reference'] = AREF.ground
    >>> piezo_config['axes'][0]['channel']['name'] = 'z'
    >>> piezo_config['inputs'] = [config.InputChannelConfig()]
    >>> piezo_config['inputs'][0]['analog-reference'] = AREF.diff
    >>> piezo_config['inputs'][0]['name'] = 'deflection'

    We set the minimum voltage for the `z` axis to -9 (a volt above
    the minimum possible voltage) to help with testing
    `.get_surface_position`.  Without this minimum voltage, small
    calibration errors could lead to a railed -10 V input for the
    first few surface approaching steps, which could lead to an
    `EdgeKink` error instead of a `FlatFit` error.

    >>> piezo_config['axes'][0].update(
    ...     {'gain':20, 'sensitivity':8e-9, 'minimum':-9})

    >>> p = AFMPiezo(config=piezo_config)
    >>> p.load_from_config(devices=devices)
    >>> p.setup_config()

    >>> deflection = p.read_deflection()
    >>> deflection  # doctest: +SKIP
    34494L
    >>> p.deflection_dtype()
    <type 'numpy.uint16'>

    We need to know where we are before we can move somewhere
    smoothly.

    >>> zeros = p.zero(axis_names=['z'])
    >>> pos = zeros[0]

    Usually `.move_to_pos_or_def` is used to approach the surface, but
    for testing we assume the z output channel is connected directly
    into the deflection input channel.

    >>> target_pos = _base.convert_volts_to_bits(
    ...     p.config.select_config('axes', 'z',
    ...     get_attribute=_base.get_axis_name)['channel'], 2)
    >>> step = int((target_pos - pos)/5)
    >>> target_def = _base.convert_volts_to_bits(
    ...     p.config.select_config('inputs', 'deflection'), 3)
    >>> data = p.move_to_pos_or_def('z', target_pos, target_def, step=step,
    ...     return_data=True)
    >>> p.last_output == {'z': int(target_pos)}
    True
    >>> pprint(data)  # doctest: +SKIP
    {'deflection':
       array([32655, 33967, 35280, 36593, 37905, 39218, 39222], dtype=uint16),
     'z':
       array([32767, 34077, 35387, 36697, 38007, 39317, 39321], dtype=uint16)}

    That was a working position-limited approach.  Now move back to
    the center and try a deflection-limited approach.

    >>> p.jump('z', pos)
    >>> target_def = _base.convert_volts_to_bits(
    ...     p.config.select_config('inputs', 'deflection'), 1)
    >>> data = p.move_to_pos_or_def('z', target_pos, target_def, step=step,
    ...     return_data=True)
    >>> print (p.last_output['z'] < int(target_pos))
    True
    >>> pprint(data)  # doctest: +SKIP
    {'deflection': array([32655, 33968, 35281, 36593], dtype=uint16),
     'z': array([32767, 34077, 35387, 36697], dtype=uint16)}

    >>> wiggle_config = config.WiggleConfig()
    >>> wiggle_config['offset'] = p.last_output['z']
    >>> wiggle_config['wavelength'] = 650e-9
    >>> p.wiggle_for_interference(config=wiggle_config,
    ...     keypress_test_mode=True)
    Press any key to continue

    >>> try:
    ...     p.get_surface_position('z', max_deflection=target_def)
    ... except surface.FlatFit, e:
    ...     print 'got FlatFit'
    got FlatFit
    >>> print e  # doctest: +SKIP
    slopes not sufficiently different: 1.0021 and 1.0021
    >>> abs(e.right_slope-1) < 0.1
    True
    >>> abs(e.left_slope-1) < 0.1
    True

    >>> for device in devices:
    ...     device.close()
    """
    def _deflection_channel(self):
        return self.channel_by_name(name='deflection', direction='input')

    def read_deflection(self):
        """Return sensor deflection in bits.

        TODO: explain how bit <-> volt conversion will work for this
        "virtual" channel.
        """
        return self._deflection_channel().data_read()

    def deflection_dtype(self):
        "Return a Numpy dtype suitable for deflection bit values."
        return self._deflection_channel().subdevice.get_dtype()

    def move_to_pos_or_def(self, axis_name, position=None, deflection=None,
                           step=1, return_data=False, pre_move_steps=0,
                           frequency=None):
        """TODO

        pre_move_steps : int
            number of 'null' steps to take before moving (confirming a
            stable input deflection).
        frequency : float
            The target step frequency in hertz.  If `Null`, go as fast
            as possible.  Note that this is software timing, so it
            should not be relied upon for precise results.
        """
        if position is None and deflection is None:
            raise ValueError('must specify position, deflection, or both')

        if return_data or _package_config['matplotlib']:
            aquire_data = True
        else:
            aquire_data = False

        if position is None:
            # default to the extreme value in the step direction
            if step > 0:
                axis = self.axis_by_name(axis_name)
                position = axis.axis_channel.get_maxdata()
            else:
                position = 0
        elif deflection is None:
            # default to the extreme value
            channel = self._deflection_channel(self)
            deflection = channel.get_maxdata()
        position = int(position)  # round down to nearest integer

        if step == 0:
            raise ValueError('must have non-zero step size')
        elif step < 0 and position > self.last_output[axis_name]:
            step = -step
        elif step > 0 and position < self.last_output[axis_name]:
            step = -step

        log_string = (
            'move to position %d or deflection %g on axis %s in steps of %d'
            % (position, deflection, axis_name, step))
        _LOG.debug(log_string)
        current_deflection = self.read_deflection()
        log_string = 'current position %d and deflection %g' % (
            self.last_output[axis_name], current_deflection)
        _LOG.debug(log_string)

        if aquire_data:
            def_array=[current_deflection]
            pos_array=[self.last_output[axis_name]]
        for i in range(pre_move_steps):
            self.jump(axis_name, piezo.last_output[axis_name])
            current_deflection = self.read_deflection()
            if aquire_data:
                def_array.append(current_deflection)
                pos_array.append(self.last_output[axis_name])
        if frequency is not None:
            time_step = 1./frequency
            next_time = _time.time() + time_step
        # step in until we hit our target position or exceed our target deflection
        while (self.last_output[axis_name] != position and
               current_deflection < deflection):
            dist_to = position - self.last_output[axis_name]
            if abs(dist_to) < abs(step):
                jump_to = position
            else:
                jump_to = self.last_output[axis_name] + step
            self.jump(axis_name, jump_to)
            current_deflection = self.read_deflection()
            log_string = (
                ('current z piezo position {} (target {}), '
                 'current deflection {} (target {})').format(
                    self.last_output[axis_name], position,
                    current_deflection, deflection))
            _LOG.debug(log_string)
            if aquire_data:
                def_array.append(current_deflection)
                pos_array.append(self.last_output[axis_name])
            if frequency is not None:
                now = _time.time()
                if now < next_time:
                    _time.sleep(next_time - now)
                next_time += time_step

        log_string = (
            'move to position %d or deflection %g on axis %s complete'
            % (position, deflection, axis_name))
        _LOG.debug(log_string)
        log_string = 'current position %d and deflection %g' % (
            self.last_output[axis_name], current_deflection)
        _LOG.debug(log_string)
        if _package_config['matplotlib']:
            if not _matplotlib:
                raise _matplotlib_import_error
            figure = _matplotlib_pyplot.figure()
            axes = figure.add_subplot(1, 1, 1)
            axes.hold(True)
            timestamp = _time.strftime('%H%M%S')
            axes.set_title('step approach %s' % timestamp)
            axes.plot(pos_array, def_array, '.', label=timestamp)
            #_pylab.legend(loc='best')
            figure.canvas.draw()
            figure.show()
            if not _matplotlib.is_interactive():
                _matplotlib_pyplot.show()

        if return_data:
            data = {
                axis_name:_numpy.array(
                    pos_array, dtype=self.channel_dtype(
                        axis_name, direction='output')),
                'deflection':_numpy.array(
                    def_array, dtype=self.deflection_dtype()),
                }
            return data

    wiggle_for_interference = _wiggle.wiggle_for_interference
    get_surface_position = _surface.get_surface_position


#def ramp
#        if USE_ABCD_DEFLECTION :
#            for i in range(4) : # i is the photodiode element (0->A, 1->B, ...)
#                self.curIn[i] = out["Deflection segment"][i][-1]
#        else :
#            self.curIn[self.chan_info.def_ind] = out["deflection"][-1]


#class FourSegmentAFM (AFM):
#    def read_deflection(self):
#        "Return sensor deflection in bits."
#        A = int(self.curIn[self.chan_info.def_ind[0]])
#        B = int(self.curIn[self.chan_info.def_ind[1]])
#        C = int(self.curIn[self.chan_info.def_ind[2]])
#        D = int(self.curIn[self.chan_info.def_ind[3]])
#        df = float((A+B)-(C+D))/(A+B+C+D)
#        dfout = int(df * 2**15) + 2**15
#        if TEXT_VERBOSE :
#            print "Current deflection %d (%d, %d, %d, %d)" \
#                % (dfout, A, B, C, D)
#        return dfout


#def test_smoothness(zp, plotVerbose=True):
#    posA = 20000
#    posB = 50000
#    setpoint = zp.def_V2in(3)
#    steps = 200
#    outfreq = 1e5
#    outarray = linspace(posB, posA, 1000)
#    indata=[]
#    outdata=[]
#    curVals = zp.jumpToPos(posA)
#    zp.pCurVals(curVals)
#    _sleep(1) # let jitters die down
#    for i in range(10):
#        print "ramp %d to %d" % (zp.curPos(), posB)
#        curVals, data = moveToPosOrDef(zp, posB, setpoint, step=steps,
#                                       return_data = True)
#        indata.append(data)
#        out = zp.ramp(outarray, outfreq)
#        outdata.append(out)
#    if plotVerbose:
#        from pylab import figure, plot, title, legend, hold, subplot        
#    if PYLAB_VERBOSE or plotVerbose:
#        _import_pylab()
#        _pylab.figure(BASE_FIG_NUM+4)
#        for i in range(10):
#            _pylab.plot(indata[i]['z'],
#                        indata[i]['deflection'], '+--', label='in')
#            _pylab.plot(outdata[i]['z'],
#                        outdata[i]['deflection'], '.-', label='out')
#        _pylab.title('test smoothness (step in, ramp out)')
#        #_pylab.legend(loc='best')
#    
#def test():
#    import z_piezo
#    zp = z_piezo.z_piezo()
#    curVals = zp.moveToPosOrDef(zp.pos_nm2out(600), defl=zp.curDef()+6000, step=(zp.pos_nm2out(10)-zp.pos_nm2out(0)))
#    if TEXT_VERBOSE:
#        zp.pCurVals(curVals)
#    pos = zp.getSurfPos(maxDefl=zp.curDef()+6000)
#    if TEXT_VERBOSE:
#        print "Surface at %g nm", pos
#    print "success"
#    if PYLAB_VERBOSE and _final_flush_plot != None:
#        _final_flush_plot()

