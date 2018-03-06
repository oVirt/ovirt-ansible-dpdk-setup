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
| nics                    | [ ]                   | List of nics to bind to dpdk.                       |
| kernel_module           | vfio-pci              | Kernel module for PMD.                              |
| nr_1g_hugepages         | 4                     | Number of 1GB hugepages.                            |
| nr_2m_hugepages         | 256                   | Number of 2MB hugepages.                            |

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
    nics: [eth1]
  
  roles:
    - oVirt.dpdk-setup
```

OVS-DPDK Deployment Removal Playbook
----------------

```yaml
---
- name: clean oVirt DPDK setup
  hosts: some_host
  gather_facts: false

  vars:
    pci_addresses: [<pci_address>]
  
  roles:
    - "oVirt.dpdk-setup/roles/undeploy-ovsdpdk"
`

License
-------

Apache License 2.0
