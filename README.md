# Kernel based Virtual Machine

![](https://i.imgur.com/ghfNbDH.png)

## Table of Content

1. [Introduction](#introduction)
1. [Requirements and Dependencies](#requirements-and-dependencies)
1. [Hardware](#hardware)
1. [Operating system](#operating-system)
1. [Configuration](#configuration)
1. [Tuning](#tuning)

## Introduction
Kernel-based Virtual Machine (*KVM*) is a virtualization module in the Linux kernel that allows the kernel to function as a hypervisor. In order to use this feature KVM requires a processor with hardware virtualization extensions (*Intel VT or AMD-V*). The Open Virtual Machine Firmware (*OVMF*) is a project to enable UEFI support for virtual machines. Starting with Linux 3.9 and recent versions of QEMU, it is now possible to passthrough a graphics card, offering the VM native graphics performance which is useful for graphic-intensive tasks. This project focuses, according to these presets, to create a virtual machine with KVM and enable GPU-passthrough. After the presets are set, flexibility and deployment in datacenters are the main aspects of this work. Mainly Docker and Kubernetes are used therefore. Details and the whole overview will be covered in the Bachelor Thesis.

## Requirements and Dependencies
As already mentioned in the introduction the hardware must support the following technologies in order to work properly with KVM. The CPU must support [*hardware virtualization*](https://ark.intel.com/content/www/us/en/ark/search/featurefilter.html?productType=873&0_VTD=True) (for KVM) and `IOMMU` (*Input-output memory management unit*) for the passthrough. Additionally the motherboard must support `IOMMU` as well for the GPU passthrough. Both the chipset and the BIOS must support it. The last requriement is that the GPU ROM must support UEFI. **If the hardware does not support those mentioned technologies it is not possible to run a KVM with GPU passthrough.**

### Hardware
For this test run the following hardware was used. It supports hardware virtualization, IOMMU and GPU passthrough.

| Component   | Description                     |
| ----------- |:------------------------------- |
| Motherboard | ASUS MAXIMUS VII Ranger         |
| CPU         | Intel Core i7 4790k @ 4.00GHZ   |
| GPU         | Nvidia GeForce GTX 970 4GB VRAM |
| RAM         | 16GB DDR3                       |
| Storage     | 120 GB SSD                      |

### BIOS/UEFI
Initially not all technolgies are enabled by default in the BIOS/UEFI. It is neccessary to enable the following parameters. It is highly recommended that a Central Processing Unit (CPU) supports Hyperthreading. A virtual machine can profit of the additional (virtual) cores. In this case the following parameters must be set:

```
Advanced / CPU Configuration → Intel Virtualization Technology = Enabled
Advanced / System Agent Configuration → VT-d = Enabled
Advanced / System Agent Configuration / Graphics Configuration → CPU Graphics Multi-Monitor = Enabled
Advanced / System Agent Configuration / Graphics Configuration → Primary Display = CPU Graphis
Boot / Secure Boot → OS Type = Other OS
Boot / Above 4G Encoding = Enabled
```

Hardware and BIOS/UEFI settings are all done. Choosing the right operating system is the next step.

### Operating system
[Manjaro KDE 20.2.1](https://manjaro.org/download/#kde-plasma) is an accessible, friendly, open-source operating system suitable for experts and newcomers. It is not a proprietary operating system which leads to full control over the hardware without restrictions. In such an operating system are we interested in. Manjaro ships with different desktop environments like *Gnome*, *KDE Plasma*, *XFCE* and *Architect* for a familiar look and feel.

Some modifications are needed to turn the operating system into a hypervisor.

#### Load Kernel Modules/Parameters
Append `intel_iommu=on` and `iommu=pt` to the following GRUB line in `/etc/default/grub`

```shell
GRUB_CMDLINE_LINUX_DEFAULT=" ... intel_iommu=on iommu=pt vfio-pci.ids=10de:13c2,10de:0fbb"
```

##### Regenerate GRUB

```shell
grub-mkconfig -o /boot/grub/grub.cfg
```

#### Check DMAR and IOMMU

```shell
sudo dmesg | grep -i -e DMAR -e IOMMU  
```
![](https://i.imgur.com/paxsrMd.png)

```shell
#!/bin/bash
shopt -s nullglob
for g in `find /sys/kernel/iommu_groups/* -maxdepth 0 -type d | sort -V`; do
    echo "IOMMU Group ${g##*/}:"
    for d in $g/devices/*; do
        echo -e "\t$(lspci -nns ${d##*/})"
    done;
done;
```
![](https://i.imgur.com/l0oL8dG.png)

#### Update GRUB

#### Update initramfs

## Install KVM
The following packages are needed to install KVM on Manjaro KDE 20.2.1 `libvirt`, `qemu`, `edk2-ovmf`, `virt-manager`. For this setup the following versions of the packages were installed.



| Package        | Version     |
|:-------------- |:----------- |
| `libvirt`      | *1:6.5.0-3* |
| `qemu`         | *5.2.0-2*   |
| `edk2-ovmf`    | *202011-1*  |
| `virt-manager` | *3.2.0-1*   |


## Enable KVM
To enable KVM it is neccessary to enter the following two commands to enable and start the service.

```shell
sudo systemctl enable libvirtd
sudo systemctl start libvirtd
```

### Configuration
https://wiki.archlinux.org/index.php/PCI_passthrough_via_OVMF#Setting_up_IOMMU

```shell
sudo virsh list --inactive
sudo virsh edit ubuntu18.04
```

## Tuning


### Setting up the virtual machine operating system
For the virtual machine operating system Ubuntu 18.04.5 LTS was used.


### Reference
https://wiki.archlinux.org/index.php/PCI_passthrough_via_OVMF

https://www.linux-kvm.org/images/b/b3/01x09b-VFIOandYou-small.pdf

https://serverfault.com/questions/222010/difference-between-xen-pv-xen-kvm-and-hvm
