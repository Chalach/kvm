# Kernel-based Virtual Machine

![reterter](https://i.imgur.com/ghfNbDH.png)

## Table of Content
1. [Introduction](#introduction)
1. [Requirements and Dependencies](#requirements-and-dependencies)
1. [Hardware](#hardware)
1. [Operating system](#operating-system)
1. [Configuration](#configuration)
1. [Tuning](#tuning)
1. [Software](software/software.md)

## Introduction
Kernel-based Virtual Machine (*KVM*) is a virtualization module in the Linux kernel that allows the kernel to function as a hypervisor. If enabled, the Linux operating system becomes a hypervisor Type-1 (native / bare-metal hypervisor). In order to use this feature KVM requires a processor with hardware virtualization extensions (*Intel VT or AMD-V*). The Open Virtual Machine Firmware (*OVMF*) is a project to enable UEFI support for virtual machines. Starting with Linux 3.9 and recent versions of QEMU, it is now possible to passthrough a graphics card, offering the VM native graphics performance which is useful for graphic-intensive tasks.

This project focuses on the creation of a KVM with GPU passthrough and will take a closer look at the capabilities, flexibility and deployment of data centers. KVM handles the underlying part such as the hardware and provisioning of the virtual machines. Docker in combination with Kubernets handles the upper laying part for the software. Details and a more precise overview will be covered in the Bachelor Thesis.

## Requirements and Dependencies
A GPU passthrough relies on a number of technologies that are not ubiquitous as of today. As already indicated in the introduction the hardware must support the following technologies in order to work properly.
* The CPU must support hardware virtualization (for KVM) and `IOMMU` (for the passthrough itself). Compatible Intel CPUs (*Intel VT-x and Intel VT-d*) are listed [here](https://ark.intel.com/content/www/us/en/ark/search/featurefilter.html?productType=873&0_VTD=True). All AMD CPUs from the Bulldozer generation and up (including Zen) should be compatible.

`IOMMU` (*Input-output memory management unit*) is a generic name for Intel VT-d and AMD-Vi. 
* Additionally the motherboard must support `IOMMU` as well for the GPU passthrough. Both the chipset and the BIOS must support it. Here is a [list of supported hardware](https://en.wikipedia.org/wiki/List_of_IOMMU-supporting_hardware).
* The last requriement is that the [GPU ROM](https://www.techpowerup.com/vgabios/) must support UEFI.

---

### Important
* If the hardware does not support the previously mentioned technologies it is **not possible** to run a KVM with GPU passthrough.

* This project focuses mainly on **Intel CPUs** and Nvidia GPUs! For AMD CPUs / GPUs head over to [this](https://wiki.archlinux.org/index.php/PCI_passthrough_via_OVMF#Prerequisites) wiki.

* **VT-d** stands for Intel Virtualization Technology for Directed I/O and should not be confused with VT-x Intel Virtualization Technology. 

* **VT-x** allows one hardware platform to function as multiple “virtual” platforms while VT-d improves security and reliability of the systems and also improves performance of I/O devices in virtualized environments.

---

### Hardware
The following table shows the used hardware for this project. Hardware virtualization, IOMMU and GPU passthrough are perfectly supported by this hardware.

| Component   | Description                     |
| ----------- | ------------------------------- |
| Motherboard | ASUS MAXIMUS VII Ranger         |
| CPU         | Intel Core i7 4790k @ 4.00GHZ   |
| GPU         | Nvidia GeForce GTX 970 4GB VRAM |
| RAM         | 16GB DDR3 @ 1600 MHZ            |
| Storage     | 120 GB SSD                      |

#### BIOS/UEFI
Initially not all technolgies are enabled by default in the BIOS/UEFI. It is neccessary to enable the following parameters listed below. It is highly recommended that a Central Processing Unit (CPU) supports Hyperthreading. A virtual machine can profit of the additional (virtual) cores.

**ASUS MAXIMUS VII Ranger**

```
Advanced / CPU Configuration → Intel Virtualization Technology = Enabled
Advanced / System Agent Configuration → VT-d = Enabled
Advanced / System Agent Configuration / Graphics Configuration → CPU Graphics Multi-Monitor = Enabled
Advanced / System Agent Configuration / Graphics Configuration → Primary Display = CPU Graphis
Boot / Secure Boot → OS Type = Other OS
Boot / Above 4G Encoding = Enabled
```

The first two settings are responsible to enable Intel VT-x and VT-d on the motherboard. Settings three and four are responsible for the output at boot time and the display of the main operating system. This will enable the onboard graphics from the CPU and switches the main output to it. It is important because with GPU passthrough enabled the graphics card is no longer available for the main system and therefore there is no graphic output via the graphics card. Setting five will disable secure boot as it is not support by Linux. The last setting will enable 64bit capable devices to be decoded in above 4G address space.

Selecting the right hardware and setting the appropriate BIOS/UEFI settings is now completed. Choosing a Linux operating system and loading the kernel parameters are the next steps.

### Operating system
[Manjaro KDE 20.2.1](https://manjaro.org/download/#kde-plasma) is an accessible, friendly, open-source operating system suitable for experts and newcomers. It is not a proprietary operating system which leads to full control over the hardware without restrictions. In such an operating system are we interested in. Manjaro ships with different desktop environments like *Gnome*, *KDE Plasma*, *XFCE* and *Architect* for a familiar look and feel.

As already announced some modifications are neccessary to turn the operating system into a hypervisor.

#### Load Kernel Parameters
Loading the correct kernel parameters will enable IOMMU on the operating system.
`intel_iommu=on` enables IOMMU and `iommu=pt` will prevent Linux from touching devices which cannot be passed through. 

Edit the following line in `/etc/default/grub`

```shell
GRUB_CMDLINE_LINUX_DEFAULT=" ... intel_iommu=on iommu=pt"
```

##### Regenerate GRUB
The GRUB must be regenerated that the settings apply on every restart.

```shell
grub-mkconfig -o /boot/grub/grub.cfg
```

#### Check DMAR and IOMMU
After rebooting, check dmesg to confirm that IOMMU has been correctly enabled.

```shell
sudo dmesg | grep -i -e DMAR -e IOMMU 
[    0.000000] Command line: BOOT_IMAGE=/boot/vmlinuz-5.9-x86_64 root=UUID=aeae42e3-30f2-44ff-a71f-710e311a3a96 ro quiet resume=UUID=4b26c43b-c6ef-4d50-aabe-bb0200bf03d3 udev.log_priority=3 intel_iommu=on iommu=pt vfio-pci.ids=10de:13c2,10de:0fbb
[    0.007089] ACPI: DMAR 0x00000000C8CB4408 0000B8 (v01 INTEL  BDW      00000001 INTL 00000001)
[    0.040111] Kernel command line: BOOT_IMAGE=/boot/vmlinuz-5.9-x86_64 root=UUID=aeae42e3-30f2-44ff-a71f-710e311a3a96 ro quiet resume=UUID=4b26c43b-c6ef-4d50-aabe-bb0200bf03d3 udev.log_priority=3 intel_iommu=on iommu=pt vfio-pci.ids=10de:13c2,10de:0fbb
[    0.040159] DMAR: IOMMU enabled
[    0.093033] DMAR: Host address width 39
[    0.093033] DMAR: DRHD base: 0x000000fed90000 flags: 0x0
[    0.093036] DMAR: dmar0: reg_base_addr fed90000 ver 1:0 cap c0000020660462 ecap f0101a
[    0.093037] DMAR: DRHD base: 0x000000fed91000 flags: 0x1
[    0.093039] DMAR: dmar1: reg_base_addr fed91000 ver 1:0 cap d2008c20660462 ecap f010da
[    0.093039] DMAR: RMRR base: 0x000000c8c23000 end: 0x000000c8c30fff
[    0.093040] DMAR: RMRR base: 0x000000cb000000 end: 0x000000cf1fffff
[    0.093041] DMAR-IR: IOAPIC id 8 under DRHD base  0xfed91000 IOMMU 1
[    0.093042] DMAR-IR: HPET id 0 under DRHD base 0xfed91000
[    0.093042] DMAR-IR: x2apic is disabled because BIOS sets x2apic opt out bit.
[    0.093043] DMAR-IR: Use 'intremap=no_x2apic_optout' to override the BIOS setting.
[    0.093406] DMAR-IR: Enabled IRQ remapping in xapic mode
[    0.156371] iommu: Default domain type: Passthrough (set via kernel command line)
[    0.293285] DMAR: No ATSR found
[    0.293314] DMAR: dmar0: Using Queued invalidation
[    0.293318] DMAR: dmar1: Using Queued invalidation
[    0.356783] pci 0000:00:00.0: Adding to iommu group 0
[    0.356792] pci 0000:00:01.0: Adding to iommu group 1
[    0.356798] pci 0000:00:02.0: Adding to iommu group 2
[    0.356803] pci 0000:00:03.0: Adding to iommu group 3
[    0.356808] pci 0000:00:14.0: Adding to iommu group 4
[    0.356815] pci 0000:00:16.0: Adding to iommu group 5
[    0.356821] pci 0000:00:19.0: Adding to iommu group 6
[    0.356827] pci 0000:00:1a.0: Adding to iommu group 7
[    0.356832] pci 0000:00:1b.0: Adding to iommu group 8
[    0.356837] pci 0000:00:1d.0: Adding to iommu group 9
[    0.356849] pci 0000:00:1f.0: Adding to iommu group 10
[    0.356854] pci 0000:00:1f.2: Adding to iommu group 10
[    0.356860] pci 0000:00:1f.3: Adding to iommu group 10
[    0.356863] pci 0000:01:00.0: Adding to iommu group 1
[    0.356866] pci 0000:01:00.1: Adding to iommu group 1
[    0.356925] DMAR: Intel(R) Virtualization Technology for Directed I/O
[    0.371057] AMD-Vi: AMD IOMMUv2 driver by Joerg Roedel <jroedel@suse.de>
[    0.371057] AMD-Vi: AMD IOMMUv2 functionality not available on this system
[    0.936123]     intel_iommu=on
[    2.507558] i915 0000:00:02.0: [drm] DMAR active, disabling use of stolen memory 
```

#### Ensuring that the groups are valid
The following script validates PCI devices if they are mapped to IOMMU groups. If it does not return anything, IOMMU is not enabled or not supported by the hardware. 

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

##### Output
An IOMMU group is the smallest set of physical devices that can be passed to a virtual machine.

```shell
IOMMU Group 0:
	00:00.0 Host bridge [0600]: Intel Corporation 4th Gen Core Processor DRAM Controller [8086:0c00] (rev 06)
IOMMU Group 1:
	00:01.0 PCI bridge [0604]: Intel Corporation Xeon E3-1200 v3/4th Gen Core Processor PCI Express x16 Controller [8086:0c01] (rev 06)
	01:00.0 VGA compatible controller [0300]: NVIDIA Corporation GM204 [GeForce GTX 970] [10de:13c2] (rev a1)
	01:00.1 Audio device [0403]: NVIDIA Corporation GM204 High Definition Audio Controller [10de:0fbb] (rev a1)
IOMMU Group 2:
	00:02.0 VGA compatible controller [0300]: Intel Corporation Xeon E3-1200 v3/4th Gen Core Processor Integrated Graphics Controller [8086:0412] (rev 06)
IOMMU Group 3:
	00:03.0 Audio device [0403]: Intel Corporation Xeon E3-1200 v3/4th Gen Core Processor HD Audio Controller [8086:0c0c] (rev 06)
IOMMU Group 4:
	00:14.0 USB controller [0c03]: Intel Corporation 9 Series Chipset Family USB xHCI Controller [8086:8cb1]
IOMMU Group 5:
	00:16.0 Communication controller [0780]: Intel Corporation 9 Series Chipset Family ME Interface #1 [8086:8cba]
IOMMU Group 6:
	00:19.0 Ethernet controller [0200]: Intel Corporation Ethernet Connection (2) I218-V [8086:15a1]
IOMMU Group 7:
	00:1a.0 USB controller [0c03]: Intel Corporation 9 Series Chipset Family USB EHCI Controller #2 [8086:8cad]
IOMMU Group 8:
	00:1b.0 Audio device [0403]: Intel Corporation 9 Series Chipset Family HD Audio Controller [8086:8ca0]
IOMMU Group 9:
	00:1d.0 USB controller [0c03]: Intel Corporation 9 Series Chipset Family USB EHCI Controller #1 [8086:8ca6]
IOMMU Group 10:
	00:1f.0 ISA bridge [0601]: Intel Corporation Z97 Chipset LPC Controller [8086:8cc4]
	00:1f.2 SATA controller [0106]: Intel Corporation 9 Series Chipset Family SATA Controller [AHCI Mode] [8086:8c82]
	00:1f.3 SMBus [0c05]: Intel Corporation 9 Series Chipset Family SMBus Controller [8086:8ca2]
```

#### Isolating the GPU
In order to assign a device and all those sharing the same IOMMU group to a virtual machine must have their driver replayced by a stub driver or a VFIO driver. It prevents the host system from interacting with them. This is why the graphics output is moved to the CPU graphics in the BIOS/UEFI section.

Binding those devices to a VFIO driver is the next step. It isolates the GPU from the host system and allows afterwards a passthrough to the virtual machine.

##### Binding vfio-pci via device ID
Referencing to the previous output of the IOMMU group contains the needed IDs.

```shell
IOMMU Group 1:
	00:01.0 PCI bridge [0604]: Intel Corporation Xeon E3-1200 v3/4th Gen Core Processor PCI Express x16 Controller [8086:0c01] (rev 06)
	01:00.0 VGA compatible controller [0300]: NVIDIA Corporation GM204 [GeForce GTX 970] [10de:13c2] (rev a1)
	01:00.1 Audio device [0403]: NVIDIA Corporation GM204 High Definition Audio Controller [10de:0fbb] (rev a1)
```

Update GRUB

vfio-pci.ids=10de:13c2,10de:0fbb
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
setlocale: No such file or directory
 Id   Name          State
------------------------------
 -    ubuntu18.04   shut off
 
```

```shell
sudo virsh edit ubuntu18.04
```
## Tuning


### Setting up the virtual machine operating system
For the virtual machine operating system Ubuntu 18.04.5 LTS was used.


### Reference
https://wiki.archlinux.org/index.php/PCI_passthrough_via_OVMF

https://www.linux-kvm.org/images/b/b3/01x09b-VFIOandYou-small.pdf

https://serverfault.com/questions/222010/difference-between-xen-pv-xen-kvm-and-hvm
