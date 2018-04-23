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
| pci_addresses           | [ ]                   | PCI addresses of the devices to use DPDK with.      |


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
    pci_addresses: ['0000:00:04.0']
  
  roles:
    - oVirt.dpdk-setup
```

License
-------

Apache License 2.0