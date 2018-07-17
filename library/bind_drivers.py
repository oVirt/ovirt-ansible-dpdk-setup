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
DOCUMENTATION = '''
---
module: bind_drivers
short_description: Binds network devices to network drivers.
author: "Leon Goldberg (@leongold)"
description:
    - "Module to bind network devices to network drivers."
options:
    pci_drivers:
        description:
            - "Dictionary of PCI address to device drivers. Empty string as values
               sets kernel defaults."
        required: true
'''

EXAMPLES = '''
- name: bind pci devices to drivers
  bind_drivers:
    pci_drivers:
      "0000:00:04.0": "vfio-pci"
'''

RETURN = '''
changed:
    description: Describes whether any alterations to devices were made.
    returned: On success.
    type: boolean
    sample: true
'''

import subprocess
import traceback

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.dpdk_setup_common import exec_cmd


def _fetch_present_driver(pci_address):
    out = subprocess.check_output(['lspci', '-v', '-s', pci_address])
    lines = out.strip().split('\n')
    for line in lines:
        if 'Kernel driver' in line:
            return line.split(':')[1].strip()


def _using_virtio(addr):
    out = subprocess.check_output(['lspci'])

    devices = out.split('\n')
    for device in devices:
        short_addr, info = device.split(' ', 1)
        if addr.split(':', 1)[1] == short_addr:
            return 'Virtio' in info

    raise Exception('Could not determine device type @ {}'.format(addr))


def _enable_unsafe_vfio_noiommu_mode():
    _remove_vfio_pci()
    _remove_vfio()

    rc, _, err = exec_cmd(
        ['modprobe', 'vfio', 'enable_unsafe_noiommu_mode=1']
    )
    if rc:
        raise Exception('Could not set unsafe noiommu mode: {}'.format(err))


def _remove_vfio_pci():
    _remove_module('vfio_pci')


def _remove_vfio():
    _remove_module('vfio')


def _remove_module(module):
    rc, _, err = exec_cmd(['modprobe', '-r', module])
    if rc:
        if 'No such file' in err:
            return
        else:
            raise Exception(
                'Could not remove {} module: {}'.format(module, err)
            )


def _bind_device_to_vfio(pci_address, driver):
    if _using_virtio(pci_address):
        _enable_unsafe_vfio_noiommu_mode()
    else:
        rc, _, _, = exec_cmd(['modinfo', 'vfio-pci'])
        if rc:
            rc, _, err = exec_cmd(['modprobe', 'vfio-pci'])
            if rc:
                raise Exception(
                    'Could not load vfio-pci module: {}'.format(err)
                )

    _bind_device_to_driver(pci_address, driver)


def _bind_device_to_driver(pci_address, driver):
    rc, _, err = exec_cmd(['driverctl', 'set-override', pci_address, driver])
    if rc:
        raise Exception('Could not bind device {} to {}: {}'.format(
            pci_address, driver, err)
        )


def _remove_override(pci_address):
    rc, _, err = exec_cmd(['driverctl', 'unset-override', pci_address])
    if rc:
        raise Exception(
            'Could not remove driver override of device {}: {}'.format(
                pci_address, err)
        )


def main():
    module = AnsibleModule(
        argument_spec=dict(
            pci_drivers=dict(default=None, type='dict', required=True)
        )
    )
    pci_drivers = module.params.get('pci_drivers')
    bind_function_map = {'vfio-pci': _bind_device_to_vfio}
    changed = False
    try:
        for pci_address, driver in pci_drivers.viewitems():
            present_driver = _fetch_present_driver(pci_address)
            if present_driver != driver:
                if driver == "":
                    _remove_override(pci_address)
                else:
                    bind_func = bind_function_map.get(
                        driver, _bind_device_to_driver
                    )
                    bind_func(pci_address, driver)
                changed = True
    except Exception as e:
        module.fail_json(msg=str(e), exception=traceback.format_exc())

    module.exit_json(changed=changed)


if __name__ == "__main__":
    main()
