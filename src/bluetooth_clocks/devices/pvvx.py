"""Bluetooth clock support for devices running the PVVX firmware."""
from __future__ import annotations

import struct
from uuid import UUID

from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

from bluetooth_clocks import BluetoothClock


class PVVX(BluetoothClock):
    """Bluetooth clock support for devices running the PVVX firmware."""

    DEVICE_TYPE = "PVVX"
    SERVICE_UUID = UUID("00001f10-0000-1000-8000-00805f9b34fb")
    CHAR_UUID = UUID("00001f1f-0000-1000-8000-00805f9b34fb")

    TIME_GET_FORMAT = None
    """The PVVX firmware doesn't support reading the time."""

    TIME_SET_FORMAT = "<BL"
    """The format string to convert a time to bytes written to the PVVX device."""

    WRITE_WITH_RESPONSE = False
    """Writing the time to the PVVX device needs write without response."""

    SERVICE_DATA_UUID = UUID("0000181a-0000-1000-8000-00805f9b34fb")
    """UUID of the service data the PVVX device is advertising."""

    @classmethod
    def recognize(
        cls, device: BLEDevice, advertisement_data: AdvertisementData
    ) -> bool:
        """Recognize the PVVX device from advertisement data.

        This checks whether the advertisement has service data with service UUID
        0x181a (PVVX custom format).

        Args:
            device (BLEDevice): The Bluetooth device.
            advertisement_data (AdvertisementData): The advertisement data.

        Returns:
            bool: ``True`` if the device is recognized as a PVVX device,
            ``False`` otherwise.
        """
        return str(cls.SERVICE_DATA_UUID) in advertisement_data.service_data

    def get_bytes_from_time(self, timestamp: float, ampm: bool = False) -> bytes:
        """Generate the bytes to set the time on the PVVX device.

        Args:
            timestamp (float): The time encoded as a Unix timestamp.
            ampm (bool): ``True`` if the device should show the time with AM/PM,
                ``False`` if it should use 24-hour format. The PVVX device
                ignores this argument, as it doesn't support this option.

        Returns:
            bytes: The bytes needed to set the time of the device to `timestamp`.
        """
        # Convert timestamp to little-endian unsigned long integer
        # And add header byte
        return struct.pack(
            self.TIME_SET_FORMAT,
            0x23,
            int(timestamp),
        )
