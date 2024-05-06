# iscsi-targets
Automatically create iSCSI targets for all drives except for a boot device.

# Features
- IQN of every iSCSI target includes drive model & serial number.
- When you add such an iSCSI target in [Atola imagers](https://atola.com/products/) as a source drive, it will pull the drive model and serial number from IQN into a case.
- You can specify a block device as an argument to create an iSCSI target for it.

Tested on various flavors of Linux like Ubuntu, Fedora, CentOS, and RHEL, including DFIR boot images:
- Paladin
- Caine
- Tsurugi

# Requirements
Python 3.6+ installed. Also, during the first launch, the script will check and install targetcli and python3-rtslib.

# Examples
Create iSCSI targets for all drives except for a boot device:
sudo python3 iscsi-targets.py

Create a single iSCSI target for specified /dev/sdb1 partition.
sudo python3 iscsi-targets.py /dev/sdb1
