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


DEVICE_PATH_FMT = '/sys/bus/pci/devices/{}'
DPDK_DRIVERS = ('vfio-pci',)


def exec_cmd(args):
    proc = subprocess.Popen(
        args, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    out, err = proc.communicate()
    return proc.returncode, out, err


def get_cpu_list(pci_addresses):
    cores = []
    for addr in pci_addresses:
        local_cpu_list = get_nic_cpus_without_zero_core(addr)
        if local_cpu_list not in cores:
            cores.append(local_cpu_list)
    return ','.join(cores)


def get_nic_cpus_without_zero_core(pci_address):
    local_cpu_list = _get_nic_cpu_list(pci_address)
    if _is_first_core_zero(local_cpu_list):
        local_cpu_list = _remove_first_core(local_cpu_list)
    return local_cpu_list


def _get_nic_cpu_list(pci_address):
    local_cpulist = os.path.join(
        DEVICE_PATH_FMT.format(pci_address), 'local_cpulist'
    )
    with open(local_cpulist) as f:
        return f.read()


def _is_first_core_zero(cores):
    return cores[:1] == '0'


def _remove_first_core(cores):
    if cores[1] == '-':
        return '1' + cores[1:]
    elif cores[1] == ',':
        return cores[2:]
    else:
        return ""
