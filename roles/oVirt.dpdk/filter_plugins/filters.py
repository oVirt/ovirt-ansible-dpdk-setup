#!/usr/bin/python
import json
import os
import subprocess


DEVICE_PATH_FMT = '/sys/bus/pci/devices/{}'


class FilterModule(object):
    def filters(self):
        return {
            'get_cpu_list': self.get_cpu_list,
            'get_dpdk_nics_numa_info': self.get_dpdk_nics_numa_info,
        }

    def _get_nic_cpu_list(self, pci_address):
        local_cpulist = os.path.join(
            DEVICE_PATH_FMT.format(pci_address),
            'local_cpulist'
        )
        with open(local_cpulist) as f:
            return f.read()

    def _get_numa_node(self, pci_address):
        numa_node = os.path.join(
            DEVICE_PATH_FMT.format(pci_address),
            'numa_node'
        )
        with open(numa_node) as f:
            return f.read()

    def _is_first_core_zero(self, cores):
        return cores[:1] == '0'

    def _remove_first_core(self, cores):
        if cores[1] == '-':
            return '1' + cores[1:]
        elif cores[1] == ',':
            return cores[2:]
        else:
            return ""

    def _get_nic_cpus_without_zero_core(self, pci_address):
        local_cpu_list = self._get_nic_cpu_list(pci_address)
        if self._is_first_core_zero(local_cpu_list):
            local_cpu_list = self._remove_first_core(local_cpu_list)
        return local_cpu_list

    def get_cpu_list(self, pci_addresses):
        cores = []
        for addr in pci_addresses:
            local_cpu_list = self._get_nic_cpus_without_zero_core(addr)
            if local_cpu_list not in cores:
                cores.append(local_cpu_list)
        return ','.join(cores)

    def get_dpdk_nics_numa_info(self, pci_addresses):
        nics_per_numa = {}
        for addr in pci_addresses:
            numa_node = int(self._get_numa_node(addr))
            if numa_node == -1:
                numa_node = 0
            if numa_node in nics_per_numa:
                nics_per_numa[numa_node]['nics'] += 1
            else:
                nics_per_numa[numa_node] = {}
                nics_per_numa[numa_node]['nics'] = 1
                nics_per_numa[numa_node]['cpu_list'] = \
                    self._get_nic_cpus_without_zero_core(addr)

        return nics_per_numa
