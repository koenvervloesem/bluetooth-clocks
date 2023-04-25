"""Module with functions to scan for Bluetooth clocks."""
from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Callable

from bleak import BleakScanner

if TYPE_CHECKING:
    from bleak.backends.device import BLEDevice
    from bleak.backends.scanner import AdvertisementData

from bluetooth_clocks import BluetoothClock, supported_devices
from bluetooth_clocks.exceptions import UnsupportedDeviceError

_logger = logging.getLogger(__name__)


async def find_clock(address: str, scan_duration: float = 5.0) -> BluetoothClock | None:
    """Get BluetoothClock object from Bluetooth address.

    Args:
        address (str): The Bluetooth address of the device.
        scan_duration (float): The scan duration for finding the device. Defaults to
          5 seconds.

    Raises:
        UnsupportedDeviceError: If the device with address `address` isn`t
          supported.

    Returns:
        BluetoothClock | None: A :class:`BluetoothClock` object for the device, or
        ``None`` if the device isn't found.
    """
    found_clock = None

    def device_found(device: BLEDevice, advertisement_data: AdvertisementData) -> None:
        """Try to recognize device as a Bluetooth clock."""
        nonlocal found_clock
        if device.address == address:
            _logger.info(
                "Device with address {address} found",
                extra={"address": address},
            )
            found_clock = BluetoothClock.create_from_advertisement(
                device,
                advertisement_data,
            )
            _logger.info(
                "Device with address {address} recognized as {device_type}",
                extra={"address": address, "device_type": found_clock.DEVICE_TYPE},
            )

    scanner = BleakScanner(detection_callback=device_found)

    _logger.info("Scanning for device...")
    await scanner.start()
    await asyncio.sleep(scan_duration)
    await scanner.stop()

    return found_clock


async def discover_clocks(
    callback: Callable[[BluetoothClock], None],
    scan_duration: float = 5.0,
) -> None:
    """Discover Bluetooth clocks.

    Args:
        callback (Callable[[BluetoothClock], None]): Function to call when a clock
          has been discovered. This function gets passed the discovered
          :class:`BluetoothClock` object as its argument.
        scan_duration (float): The scan duration for discovering devices. Defaults to
          5 seconds.
    """
    found_addresses = []

    def device_found(device: BLEDevice, advertisement_data: AdvertisementData) -> None:
        """Call callback if we recognize a found device as a clock."""
        nonlocal found_addresses
        address = device.address
        if address not in found_addresses:
            try:
                clock = BluetoothClock.create_from_advertisement(
                    device,
                    advertisement_data,
                )
                name = advertisement_data.local_name
                clock_type = clock.DEVICE_TYPE
                _logger.info(
                    "Found a {clock_type}: address {address}, name {device_name}",
                    extra={
                        "clock_type": clock_type,
                        "address": address,
                        "device_name": name,
                    },
                )
                callback(clock)
            except UnsupportedDeviceError:
                # Just ignore devices we don't recognize as a clock.
                pass
            finally:
                # Don't try to recognize the device with the same address again.
                found_addresses.append(address)

    _logger.info(
        "Supported devices: {devices}",
        extra={"devices": ", ".join(supported_devices())},
    )
    scanner = BleakScanner(detection_callback=device_found)

    _logger.info(
        "Scanning for supported clocks for {scan_duration} seconds...",
        extra={"scan_duration": scan_duration},
    )

    await scanner.start()
    await asyncio.sleep(scan_duration)
    await scanner.stop()
