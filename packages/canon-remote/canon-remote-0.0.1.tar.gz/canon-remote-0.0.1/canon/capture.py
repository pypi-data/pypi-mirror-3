#  This file is part of canon-remote.
#  Copyright (C) 2011-2012 Kiril Zyapkov <kiril.zyapkov@gmail.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.


import time
import logging
from array import array

import usb.core

from canon import commands, CanonError
from canon.bitfield import Bitfield, Flag, BooleanFlag
from canon.util import itole32a
from functools import wraps

_log = logging.getLogger(__name__)

class TransferMode(Bitfield):
    THUMB_TO_PC    = 0x01
    FULL_TO_PC     = 0x02
    THUMB_TO_DRIVE = 0x04
    FULL_TO_DRIVE  = 0x08
    _size = 4
    pc = Flag(0, thumb=THUMB_TO_PC, full=FULL_TO_PC)
    drive =  Flag(0, thumb=THUMB_TO_DRIVE, full=FULL_TO_DRIVE)


class CaptureSettings(Bitfield):
    APERTURE_F1_2 = 0x0d
    APERTURE_F1_4 = 0x10
    APERTURE_F1_6 = 0x13
    APERTURE_F1_8 = 0x15
    APERTURE_F2_0 = 0x18
    APERTURE_F2_2 = 0x1b
    APERTURE_F2_5 = 0x1d
    APERTURE_F2_8 = 0x20
    APERTURE_F3_2 = 0x23
    APERTURE_F3_5 = 0x25
    APERTURE_F4_0 = 0x28
    APERTURE_F4_5 = 0x2b
    APERTURE_F5_0 = 0x2d
    APERTURE_F5_6 = 0x30
    APERTURE_F6_3 = 0x33
    APERTURE_F7_1 = 0x35
    APERTURE_F8 = 0x38
    APERTURE_F9 = 0x3b
    APERTURE_F10 = 0x3d
    APERTURE_F11 = 0x40
    APERTURE_F13 = 0x43
    APERTURE_F14 = 0x45
    APERTURE_F16 = 0x48
    APERTURE_F18 = 0x4b
    APERTURE_F20 = 0x4d
    APERTURE_F22 = 0x50
    APERTURE_F25 = 0x53
    APERTURE_F29 = 0x55
    APERTURE_F32 = 0x58

    SHUTTER_SPEED_BULB = 0x04
    SHUTTER_SPEED_30_SEC = 0x10
    SHUTTER_SPEED_25_SEC = 0x13
    SHUTTER_SPEED_20_SEC = 0x15
    SHUTTER_SPEED_15_SEC = 0x18
    SHUTTER_SPEED_13_SEC = 0x1b
    SHUTTER_SPEED_10_SEC = 0x1d
    SHUTTER_SPEED_8_SEC = 0x20
    SHUTTER_SPEED_6_SEC = 0x23
    SHUTTER_SPEED_5_SEC = 0x25
    SHUTTER_SPEED_4_SEC = 0x28
    SHUTTER_SPEED_3_2_SEC = 0x2b
    SHUTTER_SPEED_2_5_SEC = 0x2d
    SHUTTER_SPEED_2_SEC = 0x30
    SHUTTER_SPEED_1_6_SEC = 0x32
    SHUTTER_SPEED_1_3_SEC = 0x35
    SHUTTER_SPEED_1_SEC = 0x38
    SHUTTER_SPEED_0_8_SEC = 0x3b
    SHUTTER_SPEED_0_6_SEC = 0x3d
    SHUTTER_SPEED_0_5_SEC = 0x40
    SHUTTER_SPEED_0_4_SEC = 0x43
    SHUTTER_SPEED_0_3_SEC = 0x45
    SHUTTER_SPEED_1_4 = 0x48
    SHUTTER_SPEED_1_5 = 0x4b
    SHUTTER_SPEED_1_6 = 0x4d
    SHUTTER_SPEED_1_8 = 0x50
    SHUTTER_SPEED_1_10 = 0x53
    SHUTTER_SPEED_1_13 = 0x55
    SHUTTER_SPEED_1_15 = 0x58
    SHUTTER_SPEED_1_20 = 0x5b
    SHUTTER_SPEED_1_25 = 0x5d
    SHUTTER_SPEED_1_30 = 0x60
    SHUTTER_SPEED_1_40 = 0x63
    SHUTTER_SPEED_1_50 = 0x65
    SHUTTER_SPEED_1_60 = 0x68
    SHUTTER_SPEED_1_80 = 0x6b
    SHUTTER_SPEED_1_100 = 0x6d
    SHUTTER_SPEED_1_125 = 0x70
    SHUTTER_SPEED_1_160 = 0x73
    SHUTTER_SPEED_1_200 = 0x75
    SHUTTER_SPEED_1_250 = 0x78
    SHUTTER_SPEED_1_320 = 0x7b
    SHUTTER_SPEED_1_400 = 0x7d
    SHUTTER_SPEED_1_500 = 0x80
    SHUTTER_SPEED_1_640 = 0x83
    SHUTTER_SPEED_1_800 = 0x85
    SHUTTER_SPEED_1_1000 = 0x88
    SHUTTER_SPEED_1_1250 = 0x8b
    SHUTTER_SPEED_1_1600 = 0x8d
    SHUTTER_SPEED_1_2000 = 0x90
    SHUTTER_SPEED_1_2500 = 0x93
    SHUTTER_SPEED_1_3200 = 0x95
    SHUTTER_SPEED_1_4000 = 0x98
    SHUTTER_SPEED_1_5000 = 0x9a
    SHUTTER_SPEED_1_6400 = 0x9d
    SHUTTER_SPEED_1_8000 = 0xA0

    ISO_50 = 0x40
    ISO_100 = 0x48
    ISO_125 = 0x4b
    ISO_160 = 0x4d
    ISO_200 = 0x50
    ISO_250 = 0x53
    ISO_320 = 0x55
    ISO_400 = 0x58
    ISO_500 = 0x5b
    ISO_640 = 0x5d
    ISO_800 = 0x60
    ISO_1000 = 0x63
    ISO_1250 = 0x65
    ISO_1600 = 0x68
    ISO_3200 = 0x70

    AUTO_FOCUS_ONE_SHOT = 0
    AUTO_FOCUS_AI_SERVO = 1
    AUTO_FOCUS_AI_FOCUS = 2
    MANUAL_FOCUS = 3

    FLASH_MODE_OFF = 0
    FLASH_MODE_ON = 1
    FLASH_MODE_AUTO = 2

    BEEP_OFF = 0x00
    BEEP_ON = 0x01

    EXPOSURE_PLUS_2 = 0x10
    EXPOSURE_PLUS_1_ = 0x0d
    EXPOSURE_PLUS_1_1_2 = 0x0c
    EXPOSURE_PLUS_1_1_3 = 0x0b
    EXPOSURE_PLUS_1 = 0x08
    EXPOSURE_PLUS_0_2_3 = 0x05
    EXPOSURE_PLUS_0_1_2 = 0x04
    EXPOSURE_PLUS_0_1_3 = 0x03
    EXPOSURE_ZERO = 0x00
    EXPOSURE_MINUS_0_1_3 = 0xfd
    EXPOSURE_MINUS_0_1_2 = 0xfc
    EXPOSURE_MINUS_0_2_3 = 0xfb
    EXPOSURE_MINUS_1 = 0xf8
    EXPOSURE_MINUS_1_1_3 = 0xf5
    EXPOSURE_MINUS_1_1_2 = 0xf4
    EXPOSURE_MINUS_1_2_3 = 0xf3
    EXPOSURE_MINUS_2 = 0xf0

    # (compression+raw, formats?, size)
    IMAGE_FORMAT_RAW = (0x04, 0x02, 0x00)
    IMAGE_FORMAT_SMALL_NORMAL_JPEG = (0x02, 0x01, 0x02)
    IMAGE_FORMAT_SMALL_FINE_JPEG = (0x03, 0x01, 0x02)
    IMAGE_FORMAT_MEDIUM_NORMAL_JPEG = (0x02, 0x01, 0x01)
    IMAGE_FORMAT_MEDIUM_FINE_JPEG = (0x03, 0x01, 0x01)
    IMAGE_FORMAT_LARGE_NORMAL_JPEG = (0x02, 0x01, 0x00)
    IMAGE_FORMAT_LARGE_FINE_JPEG = (0x03, 0x01, 0x00)
    IMAGE_FORMAT_RAW_AND_SMALL_NORMAL_JPEG = (0x24, 0x12, 0x20)
    IMAGE_FORMAT_RAW_AND_SMALL_FINE_JPEG = (0x34, 0x12, 0x20)
    IMAGE_FORMAT_RAW_AND_MEDIUM_NORMAL_JPEG = (0x24, 0x12, 0x10)
    IMAGE_FORMAT_RAW_AND_MEDIUM_FINE_JPEG = (0x34, 0x12, 0x10)
    IMAGE_FORMAT_RAW_AND_LARGE_NORMAL_JPEG = (0x24, 0x12, 0x00)
    IMAGE_FORMAT_RAW_AND_LARGE_FINE_JPEG = (0x34, 0x12, 0x00)

    _size = 0x2f

    image_format = Flag(offset=1, length=3)
    flash = Flag(offset=0x06, off=0x00, on=0x01, auto=0x02)
    beep = Flag(offset=0x07, on=0x01, off=0x00)
    macro = BooleanFlag(offset=0x0d, true=0x03, false=0x01)
    focus_mode = Flag(offset=0x12, length=1)
    iso = Flag(offset=0x1a, length=1)
    aperture = Flag(offset=0x1c, length=1,
                    F1_2=0x0d, F1_4=0x10, F1_6=0x13, F1_8=0x15,
                    F2_0=0x18, F2_2=0x1b, F2_5=0x1d, F2_8=0x20, F3_2=0x23,
                    F3_5=0x25, F4_0=0x28, F4_5=0x2b, F5_0=0x2d, F5_6=0x30,
                    F6_3=0x33, F7_1=0x35, F8=0x38, F9=0x3b, F10=0x3d,
                    F11=0x40, F13=0x43, F14=0x45, F16=0x48, F18=0x4b,
                    F20=0x4d, F22=0x50, F25=0x53, F29=0x55, F32=0x58)
    shutter_speed = Flag(offset=0x1e)
    exposure_bias = Flag(offset=0x20)
    shooting_mode = Flag(offset=0x08)

def require_active_capture(func):
    @wraps(func)
    def wrapper(inst, *args, **kw):
        if inst.active:
            return func(inst, *args, **kw)
        raise CanonError("{} only works when capture is active"
                         .format(func.__name__))
    return wrapper

class RemoteControlCommand(commands.FixedResponseCommand):
    """Known subcommands are listed here

    http://www.graphics.cornell.edu/~westin/canon/ch03s18.html

    """
    cmd1 = 0x13
    cmd2 = 0x12
    cmd3 = 0x201
    subcmd = None
    subcmd_resplen = None
    _required_props = (commands.FixedResponseCommand._required_props +
                       ['subcmd'])
    first_chunk_size = 0x40

    def __init__(self, payload=None, serial=None):
        cmd_payload = itole32a(self.subcmd)
        if payload is not None:
            cmd_payload.extend(payload)
        else:
            cmd_payload.extend([0x00] * 4) # at least one zero word follows
        super(RemoteControlCommand, self).__init__(cmd_payload, serial)

    @property
    def resplen(self):
        if self.subcmd_resplen is not None:
            return self.subcmd_resplen
        _log.info("{} with unknown resplen, guessing 0x1c".format(self))
        return 0x1c # this seems to be the minimum

class InitRemoteControlCmd(RemoteControlCommand):
    subcmd = 0x00
    subcmd_resplen = 0x1c

class ExitRemoteControlCmd(RemoteControlCommand):
    subcmd = 0x01
    subcmd_resplen = 0x1c

class GetParamsCmd(RemoteControlCommand):
    """
    http://www.graphics.cornell.edu/~westin/canon/ch03s18.html#sec.CamContGetPars
    """
    subcmd = 0x0a
    subcmd_resplen = 0x4c

class SetParamsCmd(RemoteControlCommand):
    """
    http://www.graphics.cornell.edu/~westin/canon/ch03s18.html#sec.CamContSetPars
    """
    subcmd = 0x07
    subcmd_resplen = 0x1c

class GetCaptureSettingsCmd(GetParamsCmd):
    def __init__(self):
        super(GetCaptureSettingsCmd, self).__init__(itole32a(0x04) +
                                                    itole32a(0x00))
    def _parse_response(self, data):
        # RELEASE_PARAMS_LEN in canon.h
        return CaptureSettings(data[0x1c:0x4b])

class SetCaptureSettingsCmd(SetParamsCmd):
    """
    http://www.graphics.cornell.edu/~westin/canon/ch03s18.html#sec.CamContSetPars
    """
    def __init__(self, settings):
        payload = array('B', itole32a(0x30))
        payload.extend(settings)
        super(SetCaptureSettingsCmd, self).__init__(payload)

class SetTransferModeCmd(RemoteControlCommand):
    """
    http://www.graphics.cornell.edu/~westin/canon/ch03s18.html#sec.CamContSetXferMode
    """
    subcmd = 0x09
    subcmd_resplen = 0x1c
    def __init__(self, transfermode):
        if isinstance(transfermode, array):
            assert transfermode.itemsize == 1
            assert len(transfermode) == 4
        else:
            transfermode = itole32a(int(transfermode))

        # XXX:
        # this one probably has more meaning than just setting
        # transfermode flags ...
        payload = itole32a(0x04) + transfermode
        super(SetTransferModeCmd, self).__init__(payload)

class SetZoomPositionCmd(RemoteControlCommand):
    """
    http://www.graphics.cornell.edu/~westin/canon/ch03s18.html#sec.CamContSetZoom
    """
    subcmd = 0x0c
    subcmd_resplen = 0x1c

class ShutterReleaseCmd(RemoteControlCommand):
    """
    http://www.graphics.cornell.edu/~westin/canon/ch03s18.html#sec.CamContRelShutter
    """
    subcmd = 0x04
    subcmd_resplen = 0x1c

class DownloadCapturedImageCmd(commands.VariableResponseCommand):
    """
    http://www.graphics.cornell.edu/~westin/canon/ch03s19.html
    """
    cmd1 = 0x17
    cmd2 = 0x12
    def __init__(self, image_index, target, thumbnail=False):
        self.target = target
        payload = array('B', [0] * 4)
        payload.extend(itole32a(0x1400))
        payload.extend(itole32a(0x01 if thumbnail else 0x02))
        payload.extend(image_index)
        super(DownloadCapturedImageCmd, self).__init__(payload)

    def execute(self, usb):
        reader = self._send(usb)
        for chunk in reader:
            self._target.write(chunk)


class CanonCapture(object):
    """Manage taking pictures via USB. The whole point.
    """
    def __init__(self, usb):
        self._usb = usb
        self._settings = None
        self._in_rc = False

    def initialize(self, force=False):
        self.stop()

    def start(self, force=False):
        if self._in_rc and not force:
            _log.info("remote capture already active, force me")
            return

        for _ in range(3):
            try:
                if not self._usb.interrupt_read(0x10, ignore_timeouts=True):
                    break
            except usb.core.USBError, e:
                _log.warn("While trying to flush the interrupt pipe: {}"
                          .format(e))
                break
            time.sleep(0.3)

        # if keys are not locked RC INIT fails, maybe
        commands.GenericLockKeysCmd().execute(self._usb)

        # 5 seconds seem more than enough
        with self._usb.timeout_ctx(5000):
            InitRemoteControlCmd().execute(self._usb)
            self._in_rc = True

        # initially set the transfermode to something known
        self.transfermode = TransferMode.FULL_TO_DRIVE

        # wtf is that?
        SetZoomPositionCmd(array('B', [0x04] + [0x00] * 7))

    def stop(self):
        with self._usb.timeout_ctx(1000):
            ExitRemoteControlCmd().execute(self._usb)
            self._in_rc = False

    @property
    def active(self):
        return self._in_rc

    def get_capture_settings(self):
        self._settings = GetCaptureSettingsCmd().execute(self._usb)
        _log.info("capture settings from camera: {}".format(self._settings))
        return self._settings

    @property
    @require_active_capture
    def settings(self):
        if not self._settings:
            return self.get_capture_settings()
        return self._settings

    @property
    @require_active_capture
    def transfer_mode(self):
        """XXX: Remote Capture 2.5.7 seems to do this in a different manner.
        """
        return GetParamsCmd([0x04] + [0x00] * 7).execute(self._usb)
#        return self._usb.do_command_rc(commands.RC_GET_PARAMS, 0x04, 0x00)

    @transfer_mode.setter
    @require_active_capture
    def transfer_mode(self, flags):
        SetTransferModeCmd(flags).execute(self._usb)

    @property
    @require_active_capture
    def shooting_mode(self):
        raise NotImplementedError()

    @property
    @require_active_capture
    def iso_speed(self):
        raise NotImplementedError()

    @property
    @require_active_capture
    def aperture(self):
        raise NotImplementedError()

    @property
    @require_active_capture
    def shutter_speed(self):
        raise NotImplementedError()

    @property
    @require_active_capture
    def white_balance(self):
        raise NotImplementedError()

    @property
    @require_active_capture
    def flash(self):
        raise NotImplementedError()

    @property
    @require_active_capture
    def image_mode(self):
        raise NotImplementedError()

    @property
    @require_active_capture
    def flash_compensation(self):
        raise NotImplementedError()

    @property
    @require_active_capture
    def exposure_compensation(self):
        raise NotImplementedError()

    @property
    @require_active_capture
    def macro(self):
        return self.settings.macro

    @macro.setter
    @require_active_capture
    def macro(self, enabled):
        enabled = bool(enabled)
        self.settings.macro = enabled
        self._set_capture_settings(self.settings)
        self.get_capture_settings()

    @require_active_capture
    def __call__(self, store_to=None, store_on_camera=None):
        """Capture an image.

            ``store_to``
                should be a writable file-like object which
                also implements the context protocol.
            ``store_on_camera``
                whether to store the image in the internal camera
                storage or not. If `store_to` is given, this is `False`
                by default, otherwise it's `True`.

            If neither argument was supplied, a capture won't happen.
        """
        tm = TransferMode()
        if store_to and not hasattr(store_to, 'write'):
            store_to = open(store_to, 'wb+')

        if store_to: # assume correct type ...
            tm.pc += TransferMode.FULL_TO_PC
            if store_on_camera == True:
                tm.drive += TransferMode.FULL_TO_DRIVE
            self.transfer_mode = tm
            with store_to:
                irq_data = self._capture_command()
                DownloadCapturedImageCmd(irq_data, store_to)

        elif store_on_camera == False:
            raise CanonError("Don't you need the image stored somewhere?")

        else:
            tm.drive += TransferMode.FULL_TO_DRIVE
            self.transfer_mode = tm
            self._capture_command()

    def _capture_command(self):
        with self._usb.poller_ctx() as p:
            ShutterReleaseCmd().execute(self._usb)
            now = time.time()
            while (len(p.received) < 0x10):
                if time.time() - now > 10:
                    _log.warn("Capture is taking longer than 10 seconds ...")
                    return
                time.sleep(1)
            _log.info("Capture completed")
            return p.received

    def _set_capture_settings(self, settings):
        payload = array('B')
        payload.extend(itole32a(0x30))
        payload.extend(settings)
        SetCaptureSettingsCmd(settings).execute(self._usb)
        self.get_capture_settings()

    capture = __call__
