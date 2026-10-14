# iscsi-targets

Automatically expose SATA, NVMe, USB, and eMMC drives as iSCSI targets for remote forensic acquisition.

Useful for acquiring internal or soldered storage that cannot be easily removed from a computer.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-Linux-lightgrey.svg)](https://www.linux.org/)

---

## Overview & Workflow

In digital forensics and incident response (DFIR), acquiring data from embedded chips (such as soldered eMMC or NVMe) or running production servers often rules out physical drive removal. 

`iscsi-targets` enables remote, bit-stream acquisition over an Ethernet network by converting attached storage devices into standard iSCSI targets.

```
┌───────────────────────────────────────────────┐
│               Suspect Computer                │
│  (Soldered eMMC, NVMe, internal SATA drives)  │
└──────────────────────┬────────────────────────┘
                       │ Boot live environment (e.g., Atola Boot Image)
                       ▼
┌───────────────────────────────────────────────┐
│               iscsi-targets.py                │
│            Exposes drives via iSCSI           │
└──────────────────────┬────────────────────────┘
                       │ TCP 3260 (network)
                       ▼
┌───────────────────────────────────────────────┐
│        Atola TaskForce / Atola Insight        │
│          (or any iSCSI-capable imager)        │
└──────────────────────┬────────────────────────┘
                       ▼
┌───────────────────────────────────────────────┐
│         Forensic Image (E01 / RAW)            │
│  Drive Model & Serial added to IQN and can be │
│  pulled into case documentation               │
└───────────────────────────────────────────────┘
```

## Features

- **Supported devices:** Supports SATA, SAS, NVMe, USB, and eMMC
- **Embedded & Soldered Storage Acquisition:** Enables remote forensic acquisition of internal eMMC and NVMe storage soldered onto motherboards: tablets, laptops, single-board computers.
- **Forensic IQN Metadata:** The IQN (iSCSI Qualified Name) of each target automatically embeds the drive model and serial number (e.g., `iqn.2026-10.com.atola:<model>-<serial>`). When added as a source in [Atola imagers](https://atola.com/products/), this metadata is automatically populated into case logs.
- **Boot Device Protection:** Automatically detects and excludes the active boot disk, whether booted from standard storage, Live CD/USB (`/cdrom`), NVMe, or SD/eMMC media. Also ignores eMMC hardware boot partitions and RPMB service areas (`mmcblk*boot*`, `rpmb`).
- **Automatic Firewall Configuration:** Detects active firewalls (`firewalld` or `ufw`) and automatically opens TCP port 3260.
- **Automated Execution:** Includes a `-y` / `--yes` flag to bypass interactive prompts.
- **Flexible Targeting:** Automatically creates targets for all non-boot block devices by default. Alternatively, accepts a specific device/partition as an argument (e.g., `/dev/mmcblk0` or `/dev/sdb1`).

## Use with Atola Boot Image

`iscsi-targets` is integrated into [Atola Boot Image](https://atola.com/products/boot-image/) to expose the internal storage of a suspect machine over the network. This is the only way if you want to remotely image the boot drive of the machine.

1. Boot the suspect computer using Atola Boot Image.
2. It will automatically write-protect its drives, expose them via iSCSI, and show IP address for connection.
3. In [Atola TaskForce](https://atola.com/products/taskforce/) or [Atola Insight](https://atola.com/products/insight/), enter the IP address > the exposed drives will appear in the source list and become available for forensic image acquisition.

## Supported Environments

Tested on various Linux distributions and DFIR live environments:

- **Forensic Distributions:** Atola Boot Image, PALADIN, CAINE, Tsurugi Linux
- **Linux Distributions:** Ubuntu, Debian, Fedora, Rocky Linux, CentOS, RHEL

## Prerequisites

- **OS:** Linux with root / `sudo` privileges.
- **Python:** Python 3.6 or later.
- **Dependencies:** The script requires `targetcli` and `python3-rtslib`. If not already present, it will prompt to automatically install them via the system package manager (`apt`, `dnf`, or `yum`).

## Quick Start & Usage

Download the script:

```bash
curl -O https://raw.githubusercontent.com/atola-technology/iscsi-targets/main/iscsi-targets.py
```

### 1. Expose all drives (excluding boot device)

```bash
sudo python3 iscsi-targets.py
```

### 2. Expose a specific device or partition

Expose an internal eMMC drive:
```bash
sudo python3 iscsi-targets.py /dev/mmcblk0
```

Expose a specific partition:
```bash
sudo python3 iscsi-targets.py /dev/sdb1
```

### Command-Line Arguments

| Argument | Description |
|---|---|
| `device` | *(Optional)* Block device or partition to expose (e.g., `/dev/nvme0n1`, `/dev/mmcblk0`, `/dev/sdb1`). If omitted, all non-boot block devices are targeted. |
| `-y`, `--yes` | *(Optional)* Automatically confirm all prompts without user interaction. |
| `-h`, `--help` | Show help message and exit. |

## Connecting to Targets

### In Atola Imagers (TaskForce / Insight)
Add an iSCSI storage target using the IP address of the suspect machine and port 3260. The drive model and serial number will be automatically parsed from the IQN and added to the case details.

### Standard Linux Initiator (`open-iscsi`)
To discover and connect from any Linux system:

```bash
# Discover targets on suspect host
sudo iscsiadm -m discovery -t sendtargets -p <TARGET_IP>:3260

# Log in to target
sudo iscsiadm -m node -l
```

## Creators

Developed and maintained by [Atola Technology](https://atola.com) - makers of high-performance forensic hardware imagers, including [Atola TaskForce 2](https://atola.com/products/taskforce/), [Atola sTaskForce](https://atola.com/products/tf1/), and [Atola Insight Forensic](https://atola.com/products/insight/).

## License

This project is licensed under the [MIT License](LICENSE).

