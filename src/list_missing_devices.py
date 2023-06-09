#!/usr/bin/env python3

"""Elegantly displays attached and missing devices."""

from data_transfer import adb_communicator

from console import console


def missing_devices():
    """Loops through device serials and checks if the device is connected

    prints in color based on missing status.
    """
    console.print("[yellow]Normally Pixel 3a #1-3 and Lenovo Tab E7 #1-28 should be here.")
    console.print(
        "Lenovo Tab E7 #29-33 are not included in the tablet cases unless tablets have been switched out."
    )
    devices = adb_communicator.get_attached_devices()
    # Counter for all connected devices
    total_devices_connected = 0
    # Gets all devices
    for device in adb_communicator.DEVICE_SERIAL_NUMBERS:
        # Checks if device is connected
        if device not in devices:
            console.print(f"[red]{adb_communicator.DEVICE_SERIAL_NUMBERS[device]}")
        else:
            console.print(f"[green]{adb_communicator.DEVICE_SERIAL_NUMBERS[device]}")
            total_devices_connected += 1
    print(f"Total Devices Connected: {total_devices_connected}")


if __name__ == "__main__":
    missing_devices()
