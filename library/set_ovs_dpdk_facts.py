#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 Red Hat, Inc.
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
#
import os
import subprocess
import traceback

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.dpdk_setup_common import \
    get_nic_cpus_without_zero_core
from ansible.module_utils.dpdk_setup_common import get_cpu_list
from ansible.module_utils.dpdk_setup_common import DEVICE_PATH_FMT
from ansible.module_utils.dpdk_setup_common import DPDK_DRIVERS


def get_dpdk_nics_numa_info(pci_addresses):
    nics_per_numa = {}
    for addr in pci_addresses:
        numa_node = int(_get_numa_node(addr))
        if numa_node == -1:
            numa_node = 0
        if numa_node in nics_per_numa:
            nics_per_numa[numa_node]['nics'] += 1
        else:
            nics_per_numa[numa_node] = {}
            nics_per_numa[numa_node]['nics'] = 1
            nics_per_numa[numa_node]['cpu_list'] = \
                get_nic_cpus_without_zero_core(addr)

    return nics_per_numa


def _get_numa_node(pci_address):
    numa_node = os.path.join(
        DEVICE_PATH_FMT.format(pci_address),
        'numa_node'
    )
    with open(numa_node) as f:
        return f.read()


def _range_to_list(core_list):
    edges = core_list.rstrip().split('-')
    return list(range(int(edges[0]), int(edges[1]) + 1))


def _list_from_string(str_list):
    return list(map(int, str_list.rstrip().split(',')))


def _get_cpu_list(cores):
    if '-' in cores:
        return _range_to_list(cores)
    if ',' in cores:
        return _list_from_string(cores)


def _get_numa_nodes_nr():
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


def get_core_mask(cores):
    mask = 0
    for core in cores:
        mask |= (1 << int(core))
    return hex(mask)


def get_pmd_cores(nics_numa_info, pmd_threads_count):
    pmd_cores = []
    for node_info in nics_numa_info.values():
        nics_count = node_info['nics']
        cores = _get_cpu_list(node_info['cpu_list'])

        num_cores = nics_count * pmd_threads_count
        while num_cores > 0:
            min_core = min(cores)
            pmd_cores.append(min_core)
            cores.remove(min_core)
            num_cores -= 1

    return pmd_cores


def get_dpdk_lcores(pmd_cores, cpu_list):
    socket_mem = ""
    cores = _get_cpu_list(cpu_list)
    available_cores = list(set(cores) - set(pmd_cores))
    return available_cores[:2]


def get_socket_mem(nics_numa_info):
    socket_mem_list = []
    numa_nodes = list(nics_numa_info.keys())

    for i in range(0, _get_numa_nodes_nr()):
        if i in numa_nodes:
            socket_mem_list.append('2048')
        else:
            socket_mem_list.append('1024')

    return ','.join(socket_mem_list)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            pci_drivers=dict(default=None, type='dict', required=True),
            pmd_threads_count=dict(default=None, type='int', required=True)
        )
    )
    pci_drivers = module.params.get('pci_drivers')
    pci_addresses = [addr for addr, driver in pci_drivers.iteritems()
                     if driver in DPDK_DRIVERS]
    pmd_threads_count = module.params.get('pmd_threads_count')
    try:
        dpdk_nics_numa_info = get_dpdk_nics_numa_info(pci_addresses)

        socket_mem = get_socket_mem(dpdk_nics_numa_info)

        pmd_cores = get_pmd_cores(dpdk_nics_numa_info, pmd_threads_count)
        pmd_cpu_mask = get_core_mask(pmd_cores)

        dpdk_lcores = get_dpdk_lcores(pmd_cores, get_cpu_list(pci_addresses))
        dpdk_lcores_mask = get_core_mask(dpdk_lcores)
    except Exception as e:
        module.fail_json(msg=str(e), exception=traceback.format_exc())

    module.exit_json(
        dpdk_socket_mem=socket_mem,
        pmd_cpu_mask=pmd_cpu_mask,
        dpdk_lcores_mask=dpdk_lcores_mask
    )

if __name__ == "__main__":
    main()