#!/bin/sh

# Get current drive information
report() { lsblk -rpo "name,type,size,mountpoint" | grep -v "sda"; }

# Interfact for the rofi menu to mount and unmount drives
rofi_menu() { echo "$1" | rofi -dmenu -show run -lines 5 -opacity "85" -bw 0 -width 30 -padding 20 -i -p "$2" | awk '{print $1}'; }

# Display the current disk status message
usbcheck() {
	mounteddrives="$(report | awk '$2=="part"&&$4!=""{printf "%s (%s)",$4,$3}' | sed --expression 's/^.*\///g')"
	if [ -n "$mounteddrives" ]; then echo " $mounteddrives";
	elif [ -n "$usbdrives" ]; then echo "";
	else echo ""; fi
}

# Mount a disk chosen with rofi
mountusb() {
	chosen="$(rofi_menu "$usbdrives" "Mount which drive?")"
	udisksctl mount --no-user-interaction -b "$chosen" 2>/dev/null
}

# Unmount a disk chosen with rofi
umountusb() {
	chosen="$(rofi_menu "$mounteddrives" "Unmount which drive?")"
	udisksctl unmount --no-user-interaction -b "$chosen" 2>/dev/null && exit 0
	udisksctl power-off --no-user-interaction -b "$chosen"
}

# Unmount all mounted disks
umountall(){
	for chosen in $(report | awk '$2=="part"&&$4!=""{printf "%s\n",$1}'); do
		udisksctl unmount --no-user-interaction -b "$chosen" 2>/dev/null && exit 0
		udisksctl power-off --no-user-interaction -b "$chosen"
	done
}

# Generate the current lists of available and mounted disks
usbdrives="$(report | awk '$2=="part"&&$4==""{printf "%s (%s)\n",$1,$3}')"
mounteddrives="$(report | awk '$2=="part"&&$4!=""{printf "%s (%s)\n",$1,$3}')"

# From the given argument, perform the appropriate action for the script
case "$1" in
	--check) usbcheck;;
	--mount) [ -n "$usbdrives" ] && mountusb;;
	--umount) [ -n "$mounteddrives" ] && umountusb;;
	--umount-all) [ -n "$mounteddrives" ] && umountall;;
esac
