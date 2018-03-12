#!/usr/bin/python
import os
import subprocess


class FilterModule(object):
    def filters(self):
        return {
            'devices_exist': self.devices_exist,
            'get_pci_addresses': self.get_pci_addresses,
            'get_cpu_list': self.get_cpu_list,
            'get_dpdk_nics_numa_info': self.get_dpdk_nics_numa_info,
            'get_nics_by_pci_addresses': self.get_nics_by_pci_addresses,
        }

    def _get_pci_address(self, nic):
        cat_proc = subprocess.Popen(
            "cat /sys/class/net/{}/device/uevent".format(nic).split(),
            stdout=subprocess.PIPE)
        grep_proc = subprocess.Popen("grep PCI_SLOT_NAME ".split(),
                                     stdin=cat_proc.stdout,
                                     stdout=subprocess.PIPE)
        cut_proc = subprocess.Popen(" cut -d= -f2".split(),
                                    stdin=grep_proc.stdout,
                                    stdout=subprocess.PIPE)
        output, error = cut_proc.communicate()
        return output

    def _get_nic_cpu_list(self, nic):
        cmd = "cat /sys/class/net/{}/device/local_cpulist".format(nic)
        proc = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
        output, error = proc.communicate()
        return output

    def _get_numa_node(self, nic):
        numa_path = '/sys/class/net/{}/device/numa_node'.format(nic)
        if not os.path.isfile(numa_path):
            return -1
        cmd = 'cat {}'.format(numa_path)
        proc = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
        output, error = proc.communicate()
        return output

    def _get_interface_name(self, pci_address):
        proc = subprocess.Popen(
                "ls -la /sys/bus/pci/devices/{}/net/".format(
                    pci_address).split(),
                stdout=subprocess.PIPE)
        output, error = proc.communicate()
        interface_name = output.split()[-1]
        return interface_name

    def _is_first_core_zero(self, cores):
        return cores[:1] == '0'

    def _remove_first_core(self, cores):
        if cores[1] == '-':
            return '1' + cores[1:]
        elif cores[1] == ',':
            return cores[2:]
        else:
            return ""

    def _get_nic_cpus_without_zero_core(self, nic):
        local_cpu_list = self._get_nic_cpu_list(nic)
        if self._is_first_core_zero(local_cpu_list):
            local_cpu_list = self._remove_first_core(local_cpu_list)
        return local_cpu_list

    def devices_exist(self, nics):
        return all(os.path.isdir(os.path.join('/sys/class/net', nic)) \
                for nic in nics)

    def get_cpu_list(self, nics):
        cores = []
        for nic in nics:
            local_cpu_list = self._get_nic_cpus_without_zero_core(nic)
            if local_cpu_list not in cores:
                cores.append(local_cpu_list)
        return ','.join(cores)

    def get_pci_addresses(self, nics):
        pci_addresses = []
        for nic in nics:
            pci_addresses.append(self._get_pci_address(nic))
        return pci_addresses

    def get_dpdk_nics_numa_info(self, nics):
        nics_per_numa = {}
        for nic in nics:
            numa_node = int(self._get_numa_node(nic))
            if numa_node == -1:
                numa_node = 0
            if numa_node in nics_per_numa:
                nics_per_numa[numa_node]['nics'] += 1
            else:
                nics_per_numa[numa_node] = {}
                nics_per_numa[numa_node]['nics'] = 1
                nics_per_numa[numa_node]['cpu_list'] = \
                    self._get_nic_cpus_without_zero_core(nic)

        return nics_per_numa

    def get_nics_by_pci_addresses(self, pci_addresses):
        nics = []
        for pci_address in pci_addresses:
            nic = self._get_interface_name(pci_address)
            nics.append(nic)

        return nics
