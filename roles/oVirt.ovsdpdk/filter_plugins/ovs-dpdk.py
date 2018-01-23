#!/usr/bin/python


class FilterModule(object):
    def filters(self):
        return {
            'get_core_mask': self.get_core_mask
        }

    def get_core_mask(self, cores):
        mask = 0
        for core in cores:
            mask |= (1 << int(core))
        return hex(mask)
