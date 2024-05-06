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

# Why iSCSI targets
iSCSI is a network protocol that allows you to image drives soldered into a motherboard, working servers that can't be shut down, or devices that you have a legal warrant to access but can't seize.
To expose a physical or logical drive via iSCSI on a network, you need to set up an iSCSI target correctly.

# Requisites
Linux only. Python 3.6+ must be installed. 
The script will also check for and install two dependencies the first time it is run:
- targetcli
- python3-rtslib

# Examples
Create iSCSI targets for all drives except for a boot device:
sudo python3 iscsi-targets.py

Create a single iSCSI target for specified /dev/sdb1 partition.
sudo python3 iscsi-targets.py /dev/sdb1

# Creators
Atola Technology - makers of high-performance forensic hardware imagers.
