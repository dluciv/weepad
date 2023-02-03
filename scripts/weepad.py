#!/usr/bin/env python3

import sys
import asyncio
from evdev import InputDevice, InputEvent, ecodes as e
import evdev_mapper


class WeePad(evdev_mapper.EvdevMappedKeyboard):

    def __init__(self, source_device: InputDevice, *args, **kwargs):
        super().__init__(source_device, *args, **kwargs)

        self.cur_case: int = 0
        self.keys_pressed: int = 0

    # override
    def extra_keys(self) -> list[int]:
        return [e.KEY_KBD_LAYOUT_NEXT,
                e.KEY_MICMUTE, e.KEY_MSDOS, e.KEY_COFFEE]

    key_mappings: dict[tuple[int, int], int] = {
        (0, e.KEY_KPENTER): e.KEY_KBD_LAYOUT_NEXT,
        (0, e.KEY_KPSLASH): e.KEY_CUT,
        (0, e.KEY_KPASTERISK): e.KEY_COPY,
        (0, e.KEY_KPMINUS): e.KEY_PASTE,

        (0, e.KEY_KP7): e.KEY_F13,
        (0, e.KEY_KP8): e.KEY_F14,
        (0, e.KEY_KP9): e.KEY_F15,

        (0, e.KEY_KP4): e.KEY_UNDO,
        (0, e.KEY_KP6): e.KEY_AGAIN,
        (0, e.KEY_KP1): e.KEY_MICMUTE,
        (0, e.KEY_KP2): e.KEY_MUTE,
        (0, e.KEY_KP3): e.KEY_FIND,
        (0, e.KEY_KP0): e.KEY_HELP,

        (1, e.KEY_KPSLASH): e.KEY_MSDOS,
        (1, e.KEY_KPASTERISK): e.KEY_COFFEE,

        (1, e.KEY_KP6): e.KEY_F16,
        (1, e.KEY_KP7): e.KEY_F17,
        (1, e.KEY_KP8): e.KEY_F18,
        (1, e.KEY_KP9): e.KEY_F19,
        (1, e.KEY_KP0): e.KEY_F20,
        (1, e.KEY_KP1): e.KEY_F21,
        (1, e.KEY_KP2): e.KEY_F22,
        (1, e.KEY_KP3): e.KEY_F23,
        (1, e.KEY_KP4): e.KEY_F24
    }

    # implement
    def map_key(self, k: int) -> int | None:
        return WeePad.key_mappings.get((self.cur_case, k))

    # override
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
