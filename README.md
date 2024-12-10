# iscsi-targets
Automatically create iSCSI targets for all drives except for a boot device.

## Features
- IQN of every iSCSI target includes drive model & serial number.
- When you add such an iSCSI target in [Atola imagers](https://atola.com/products/) as a source drive, it will pull the drive model and serial number from IQN into a case.
- You can specify a block device as an argument to create an iSCSI target for it.

Tested on various flavors of Linux like Ubuntu, Fedora, Rocky, CentOS, and RHEL, including DFIR boot images:
- Paladin
- Caine
- Tsurugi

## Why iSCSI targets
iSCSI is a network protocol that allows to access a physical or logical devices. To expose a physical or logical drive via iSCSI on a network, you need to set up an iSCSI target correctly. 

Typical DFIR use cases have to do with image acquisition of:
- Drives soldered into a motherboard or the ones that can't be seized.
- Running servers that can't be shut down.

Another enterprise use case is a replication of an image to multiple computers over a network.

## Requisites
Linux only. Python 3.6+ must be installed. 
The script will also check for and install two dependencies the first time it is run:
- targetcli
- python3-rtslib

## Examples
Create iSCSI targets for all drives except for a boot device:

`sudo python3 iscsi-targets.py`

Create a single iSCSI target for specified /dev/sdb1 partition.

`sudo python3 iscsi-targets.py /dev/sdb1`

## Creators
[Atola Technology](https://atola.com) - makers of high-performance forensic imagers.
