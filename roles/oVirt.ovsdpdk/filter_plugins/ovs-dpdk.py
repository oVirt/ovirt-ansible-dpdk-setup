#!/usr/bin/python

import subprocess

class FilterModule(object):
    def filters(self):
        return {
            'get_core_mask': self.get_core_mask,
            'get_pmd_cores': self.get_pmd_cores,
            'get_dpdk_lcores': self.get_dpdk_lcores,
            'get_socket_mem': self.get_socket_mem
        }

    def _range_to_list(self, core_list):
        edges = core_list.rstrip().split('-')
        return list(range(int(edges[0]), int(edges[1]) + 1))

    def _list_from_string(self, str_list):
        return list(map(int, str_list.rstrip().split(',')))

    def _get_cpu_list(self, cores):
        if '-' in cores:
            return self._range_to_list(cores)
        if ',' in cores:
            return self._list_from_string(cores)

    def _get_numa_nodes_nr(self):
        ls_proc = subprocess.Popen(
                "ls -l /sys/devices/system/node/".split(),
                stdout=subprocess.PIPE)
        grep_proc = subprocess.Popen(
                "grep node".split(),
                stdin=ls_proc.stdout,
                stdout=subprocess.PIPE)
        wc_proc = subprocess.Popen(
                "wc -l".split(),
                stdin=grep_proc.stdout,
                stdout=subprocess.PIPE)

        output, error = wc_proc.communicate()
        return int(output)

    def get_core_mask(self, cores):
        mask = 0
        for core in cores:
            mask |= (1 << int(core))
        return hex(mask)

    def get_pmd_cores(self, nics_numa_info, pmd_threads_count):
        pmd_cores = []
        for node_info in nics_numa_info.values():
            nics_count = node_info['nics']
            cores = self._get_cpu_list(node_info['cpu_list'])

            num_cores = nics_count * pmd_threads_count
            while num_cores > 0:
                min_core = min(cores)
                pmd_cores.append(min_core)
                cores.remove(min_core)
                num_cores -= 1

        return pmd_cores

    def get_dpdk_lcores(self, pmd_cores, cpu_list):
        socket_mem = ""
        cores = self._get_cpu_list(cpu_list)
        available_cores = list(set(cores) - set(pmd_cores))
        return available_cores[:2]

    def get_socket_mem(self, nics_numa_info):
        socket_mem_list = []
        numa_nodes = list(nics_numa_info.keys())

        for i in range(0, self._get_numa_nodes_nr()):
            if i in numa_nodes:
                socket_mem_list.append('2048')
            else:
                socket_mem_list.append('1024')

        return ','.join(socket_mem_list)

