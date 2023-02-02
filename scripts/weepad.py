#!/usr/bin/env python3

import sys
import asyncio
from evdev import InputDevice, InputEvent, ecodes as e
from copy import deepcopy
import evdev_mapper


class WeePad(evdev_mapper.EvdevMappedKeyboard):
    # override/implement
    def extra_keys(self) -> list[int]:
        return [e.KEY_KBD_LAYOUT_NEXT, e.KEY_MICMUTE, e.KEY_MSDOS, e.KEY_COFFEE]

    # override/implement
    def map_key(self, k: int) -> int | None:
        match self.cur_case, k:
            case (0, e.KEY_KPENTER):
                return e.KEY_KBD_LAYOUT_NEXT
            case (0, e.KEY_KPSLASH):
                return e.KEY_CUT
            case (0, e.KEY_KPASTERISK):
                return e.KEY_COPY
            case (0, e.KEY_KPMINUS):
                return e.KEY_PASTE

            case (0, e.KEY_KP7):
                return e.KEY_F13
            case (0, e.KEY_KP8):
                return e.KEY_F14
            case (0, e.KEY_KP9):
                return e.KEY_F15
            case (0, e.KEY_KP4):
                return e.KEY_UNDO
            case (0, e.KEY_KP6):
                return e.KEY_AGAIN
            case (0, e.KEY_KP1):
                return e.KEY_MICMUTE
            case (0, e.KEY_KP2):
                return e.KEY_MUTE
            case (0, e.KEY_KP3):
                return e.KEY_FIND
            case (0, e.KEY_KP0):
                return e.KEY_HELP

            case (1, e.KEY_KPSLASH):
                return e.KEY_MSDOS
            case (1, e.KEY_KPASTERISK):
                return e.KEY_COFFEE
            case (1, e.KEY_KP6):
                return e.KEY_F16
            case (1, e.KEY_KP7):
                return e.KEY_F17
            case (1, e.KEY_KP8):
                return e.KEY_F18
            case (1, e.KEY_KP9):
                return e.KEY_F19
            case (1, e.KEY_KP0):
                return e.KEY_F20
            case (1, e.KEY_KP1):
                return e.KEY_F21
            case (1, e.KEY_KP2):
                return e.KEY_F22
            case (1, e.KEY_KP3):
                return e.KEY_F23
            case (1, e.KEY_KP4):
                return e.KEY_F24

            case (_, v):
                return v

    def map_input_event(self, ie: InputEvent) -> InputEvent | None:
        if ie.type != e.EV_KEY:
            return ie

        if ie.value == 1:
            self.keys_pressed += 1
        elif ie.value == 0:
            self.keys_pressed -= 1

        if self.keys_pressed == 0:
            self.cur_case = 0
        elif self.keys_pressed == 1 and ie.code == e.KEY_KPDOT:
            self.cur_case = 1

        if ie.code == e.KEY_KPDOT:
            return None

        return super().map_input_event(ie)

    def __init__(self, source_device: InputDevice, *args, **kwargs):
        super().__init__(source_device, *args, **kwargs)

        self.cur_case: int = 0
        self.keys_pressed: int = 0


if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    phys_dev_f = sys.argv[1]  # e.g. "/dev/input/by-id/usb-13ba_0001-event-kbd"
    phys_dev = InputDevice(phys_dev_f)

    virt_dev1 = WeePad(
        phys_dev,
        name="Wee Macro Pad",
        vendor=399,
        product=5,
        version=2,
        bustype=e.BUS_VIRTUAL
    )

    with phys_dev.grab_context():
        loop.run_until_complete(virt_dev1.async_map_loop())
