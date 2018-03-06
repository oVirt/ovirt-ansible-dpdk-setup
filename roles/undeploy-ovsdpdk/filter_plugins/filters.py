#!/usr/bin/python
import subprocess


class FilterModule(object):
    def filters(self):
        return {
            'get_kernel_driver': self.get_kernel_driver,
        }

    def _get_kernel_driver(self, pci_address):
        lspci_proc = subprocess.Popen(
                "lspci -v -s {}".format(pci_address).split(),
                stdout=subprocess.PIPE)
        grep_proc = subprocess.Popen(
                "grep modules:".split(),
                stdin=lspci_proc.stdout,
                stdout=subprocess.PIPE)
        cut_proc = subprocess.Popen(
                "cut -d: -f2".split(),
                stdin=grep_proc.stdout,
                stdout=subprocess.PIPE)
        output, error = cut_proc.communicate()
        return output.strip()

    def get_kernel_driver(self, pci_addresses):
        return self._get_kernel_driver(pci_addresses[0])



