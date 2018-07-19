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
| pmd_threads_count       | 1                     | Sets the amount of PMD threads per each DPDK compatible NIC |
| nr_2mb_hugepages        | 1024                  | Sets the amount of 2MB hugepages to use, if 2MB hugepages are used |
| nr_1gb_hugepages        | 4                     | Sets the amount of 1GB hugepages to use, if 1GB hugepages are used |
| use_1gb_hugepages       | true                  | Determines whether 1GB hugepages should be used, if supported |



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
