oVirt DPDK Setup
================

The `oVirt.dpdk-setup` role enables you to set up Open vSwitch with DPDK support.


Requirements:
------------

* Ansible version 2.4 or higher
* NICS must support DPDK
* Hardware support: Make sure VT-d / AMD-Vi is enabled in BIOS


Role Variables
--------------

| Name                    | Default value         |                                                     |
|-------------------------|-----------------------|-----------------------------------------------------|
| pci_drivers             |                       | PCI address to driver mapping. |
| configure_kernel        | true                  | Determines whether the kernel should be configured for DPDK usage. |
| bind_drivers            | true                  | Determines whether drivers should be bound to the devices. |
| set_ovs                 | true                  | Determines whether OVS should be configured and started. |


Dependencies
------------

No.

Example Playbook
----------------

```yaml
---
- name: oVirt DPDK setup
  hosts: some_host
  gather_facts: false

  vars:
    pci_drivers:
      "0000:00:04.0": "vfio-pci"
      "0000:00:04.1": "igb"
      "0000:00:04.2": ""
  
  roles:
    - oVirt.dpdk-setup
```

License
-------

Apache License 2.0
