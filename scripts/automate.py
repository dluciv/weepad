#!/usr/bin/env python3

# TODO: It breethes. Now separate rules from implementation, add minimal engineering...

import asyncio
from collections import defaultdict
from copy import deepcopy
from abc import ABC, abstractmethod
from evdev import InputDevice, InputEvent, categorize, ecodes as e, UInput

phys_dev_f = "/dev/input/by-id/usb-13ba_0001-event-kbd"
phys_dev = InputDevice(phys_dev_f)

class KeyMapper(ABC):
    @abstractmethod
    def map_key(k: int)-> int:
        ...

class ShitPadMapper(KeyMapper):
    def map_key(self, k: int)-> int:
        match k:
            case e.KEY_KPENTER:
                return e.KEY_KBD_LAYOUT_NEXT # ecodes.KEY_KATAKANAHIRAGANA
            case e.KEY_KP7 | e.KEY_HOME:
                return e.KEY_F13
            case e.KEY_KP8 | e.KEY_UP:
                return e.KEY_F14
            case e.KEY_KP9 | e.KEY_PAGEUP:
                return e.KEY_F15
            case e.KEY_KPSLASH:
                return e.KEY_CUT
            case e.KEY_KPASTERISK:
                return e.KEY_COPY
            case e.KEY_KPMINUS:
                return e.KEY_PASTE
            case e.KEY_KP0:
                return e.KEY_HELP
            case v:
                return v


async def inp_helper(ph_dev: InputDevice, vl_dev: UInput):
    mapper = ShitPadMapper()
    async for ev in ph_dev.async_read_loop():
        print(repr(ev))
        ie: InputEvent = ev
        if ie.type == e.EV_KEY:
            ie.code = mapper.map_key(ie.code)
        vl_dev.write_event(ie)
        vl_dev.syn()

loop = asyncio.get_event_loop()

virt_dev1 = UInput(
    name = "Wee Macro Pad",
    vendor  = 399,
    product = 5,
    version = 2,
    bustype = e.BUS_VIRTUAL,
    events = { e.EV_KEY :
        (phys_dev.capabilities()[e.EV_KEY]) +
        [e.KEY_KBD_LAYOUT_NEXT]
    }
)

with \
    phys_dev.grab_context()\
    :
    #to_merge as virt_dev:

    loop.run_until_complete(inp_helper(phys_dev, virt_dev1))
