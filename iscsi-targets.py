
# ========================================================================================
#                  Atola Technology - Automated iSCSI Target Setup
# ========================================================================================
# This script automatically creates iSCSI targets for all drives except for a boot device.
# Tested on various flavors of Linux like Ubuntu, Fedora, CentOS, and RHEL, including DFIR boot images like Paladin, Caine, and Tsurugi.
#
# Features:
# - IQN of every iSCSI target includes drive model & serial number.
# - When you add such an iSCSI target in the Atola imager as a source drive, it will pull the drive model and serial number from IQN into a case.
# - You can specify a block device as an argument to create an iSCSI target for it.
#
# Developed by Atola Technology - makers of high-performance forensic hardware imagers.
# For more information, visit https://atola.com


import subprocess
import os
import re
import argparse
import sys
import datetime


def run_command(command):
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        print(f"Error executing command '{command}': {result.stderr.strip()}")
        exit(1)
    return result.stdout.decode('utf-8')


def install_targetcli():
    if os.path.exists("usr/bin/dnf"):
        run_command("dnf install python3-rtslib -y")
        run_command("dnf install targetcli -y")
    elif os.path.exists("/usr/bin/yum"):
        run_command("yum install python3-rtslib -y")
        run_command("yum install targetcli -y")
    elif os.path.exists("/usr/bin/apt-get"):
        run_command("apt-get install python3-rtslib-fb -y")
        run_command("apt-get install targetcli-fb -y")

def check_iscsi_port_free():
    if run_command(f"lsof -i :3260 || true") != "":
        print("Port 3260 is already in use. Please make sure that the port is free before running this script.")
        exit(1)

def get_boot_device():
    mount_info = run_command("lsblk | grep -E '^.* /boot' || true")
    if mount_info == "":
        # if lsblk does not show /boot, then it is a live CD
        mount_info = run_command("lsblk | grep /cdrom || true")
        if mount_info == "":
            mount_info = run_command("lsblk | grep -E '^.* /$' || true")

    boot_device = re.search(r'(sd[a-z]+)|(nvme[0-9])|(mmcblk[0-9]+p[0-9]+)', mount_info)
    if boot_device is None:
        return None

    return "/dev/" + next(group for group in boot_device.groups() if group is not None)

def is_disk(device):
    short_name = get_block_short_name(device)
    device_type = run_command(f"lsblk -o NAME,TYPE | grep {short_name} | awk '{{print $2}}' || true").splitlines()
    if len(device_type) == 0:
        print(f"{device} is not exist.")
        exit(1)
    device_type = device_type[0].strip()
    if device_type == "disk":
        return True
    return False


def get_drives():
    drives = run_command("lsblk | grep disk | awk '{{print $1}}'").split("\n")
    sizes = run_command("lsblk | grep disk | awk '{{print $4}}'").split("\n")
    drives = list(filter(str.strip, drives))
    for i in range(len(drives)):
        drives[i] = "/dev/" + drives[i]

    drives_with_size = []
    for drive, size in zip(drives, sizes):
        if size != "0B":
            drives_with_size.append(drive)

    return drives_with_size


def check_if_used_in_iscsi(drive):
    result = run_command(f"targetcli ls /backstores/block | grep {drive} || true")
    return len(result) != 0


def check_is_mounted(drive):
    volumes = run_command(f"mount | grep {drive} || true")
    return len(volumes) != 0


def unmount_drive(drive):
    if check_is_mounted(drive):
        run_command(f"umount {drive}* || true")


def get_block_short_name(drive):
    return drive.split("/")[-1]


def get_drive_details(drive):
    drive_name = get_block_short_name(drive)
    model = run_command(f"lsblk -o NAME,MODEL | grep {drive_name}").splitlines()[0].strip()
    model = model[len(drive_name):-1].strip().replace(" ", "-").replace("_", "-")
    serial = run_command(f"lsblk -o NAME,SERIAL | grep {drive_name}").splitlines()[0].strip()
    serial = serial[len(drive_name):-1].strip()
    return model, serial


def create_iscsi_target(drive, block, iqn):
    if not run_command(f"targetcli ls /iscsi | grep {iqn} || true"):
        run_command(f"targetcli iscsi/ create {iqn}")
        run_command(f"targetcli iscsi/{iqn}/tpg1/luns/ create {block}")
        run_command(f"targetcli iscsi/{iqn}/tpg1/ set attribute generate_node_acls=1")
        print(f"iSCSI target created for {drive} with IQN: {iqn}")
        run_command(f"targetcli saveconfig")


def create_block_for_disk(drive, model, serial):
    if not run_command(f"targetcli ls /backstores/block | grep {model} || true"):
        run_command(f"targetcli backstores/block create name={model} dev={drive} wwn={serial}")
    return f"/backstores/block/{model}"


def create_iqn(name):
    current_year = datetime.datetime.now().year
    current_month = datetime.datetime.now().strftime('%m')
    return f"iqn.{current_year}-{current_month}.com.atola:{name}".lower()


def create_iqn_for_disk(model, serial):
    return create_iqn(f"{model}-{serial}")


def create_block_for_partition(partition):
    partition_name = get_block_short_name(partition)
    if not run_command(f"targetcli ls /backstores/block | grep {partition_name} || true"):
        run_command(f"targetcli backstores/block create name={partition_name} dev={partition}")
    return f"/backstores/block/{partition_name}"


def create_iqn_for_partition(partition):
    partition_name = get_block_short_name(partition)
    return create_iqn(partition_name)


def main(device):
    # Check python3 is installed
    if not os.path.exists("/usr/bin/python3"):
        print(
            "Python3 is not installed. Please install it using 'apt install python3 -y' or 'yum install python3 -y' depending on your distribution.")
        return

    if sys.version_info.major < 3 or sys.version_info.major == 3 and sys.version_info.minor < 6:
        print("Python version should be 3.6 or later.")
        return

    if device is not None:
        is_disk(device)

    # Check if the script is run with root privileges
    if os.geteuid() != 0:
        print("This script needs to be run with root privileges.")
        return

    check_iscsi_port_free()

    # Check if targetcli is installed
    if not os.path.exists("/usr/bin/targetcli"):
        install = input("targetcli is not installed. Do you want to install it? (Y/N): ")
        if install.lower() == "y":
            install_targetcli()
        else:
            return

    # Check if firewall is enabled
    if os.path.exists("/usr/bin/apt-firewall-cmd") or os.path.exists("/usr/bin/firewall-cmd"):
        if "running" in run_command("firewall-cmd --state || true"):
            # Open port 3260 for iSCSI traffic
            run_command("firewall-cmd --permanent --add-port=3260/tcp")
            # Reload firewall to apply changes
            run_command("firewall-cmd --reload")
    elif "ufw" in run_command("dpkg -l | grep ufw || true"):
        if "active" in run_command("ufw status || true"):
            # Open port 3260 for iSCSI traffic
            run_command("ufw allow 3260/tcp")

    boot_device = get_boot_device()
    if not boot_device:
        print("Unable to determine the boot device.")
        return
    print(f"Boot device: {boot_device}")

    if device == boot_device:
        print(f"Boot device {device} cannot be used for iSCSI target creation.")
        return

    if device:
        drives = [device]
    else:
        drives = get_drives()

    for drive in drives:
        if check_if_used_in_iscsi(drive):
            drives.remove(drive)

    if len(drives) == 0:
        print("No block devices can be used for iSCSI target creation.")
        return

    if len(drives) == 1 and drives[0] == boot_device:
        print(f"Boot device {boot_device} is the only drive available and cannot be used for iSCSI target creation.")
        return

    drives = [drive for drive in drives if drive != boot_device]

    if device is not None and not is_disk(device):
        print(f"{device} file system will be unmounted and used for iSCSI target creation.")
    else:
        print("The following block devices will be unmounted and used for iSCSI target creation:")
        for drive in drives:
            model, serial = get_drive_details(drive)
            print(drive + "\t" + model + "\t" + serial)

    confirm = input("Do you want to continue? (Y/N): ")
    if confirm.lower() != "y":
        print("Operation cancelled.")
        return

    for drive in drives:
        unmount_drive(drive)
        if is_disk(drive):
            model, serial = get_drive_details(drive)
            block = create_block_for_disk(drive, model, serial)
            iqn = create_iqn_for_disk(model, serial)
        else:
            block = create_block_for_partition(drive)
            iqn = create_iqn_for_partition(drive)
        create_iscsi_target(drive, block, iqn)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Creates iSCSI targets for block devices')
    parser.add_argument('device', nargs='?', help='Block device to expose as an iSCSI target. If not specified, all block devices except for the boot device will be used.')
    args = parser.parse_args()
    main(args.device)
