import asyncio
from collections import defaultdict
from copy import deepcopy
from abc import ABC, abstractmethod
from evdev import InputDevice, InputEvent, categorize, ecodes as e, UInput


class EvdevMappedKeyboard(UInput):
    def __init__(self, source_device: InputDevice, *args, **kwargs):
        self.source_device: InputDevice = source_device

        nwargs = deepcopy(kwargs)
        if 'events' not in nwargs:
            nwargs['events'] = dict()
        if e.EV_KEY not in nwargs['events']:
            nwargs['events'][e.EV_KEY] = source_device.capabilities()[e.EV_KEY]

        nwargs['events'][e.EV_KEY] += self.extra_keys()

        super().__init__(*args, **nwargs)

    async def async_map_loop(self):
        async for ev in self.source_device.async_read_loop():
            # print(repr(ev))
            ie = self.map_input_event(ev)
            if ie is not None:
                self.write_event(ie)
                self.syn()

    def extra_keys(self) -> list[int]:
        return []

    def map_key(self, k: int) -> int | None:
        raise NotImplementedError("Inherit and override please")

    def map_input_event(self, ie: InputEvent) -> InputEvent | None:
        '''Defaults to invocation of map_key, can be ovverriden'''
        if ie.type == e.EV_KEY:
            ie = deepcopy(ie)
            newcode = self.map_key(ie.code)
            if newcode is None:
                return None
            ie.code = newcode
        return ie


if __name__ == '__main__':
    raise Exception("This is a module, not a program")
