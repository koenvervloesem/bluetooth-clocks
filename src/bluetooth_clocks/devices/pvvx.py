"""Bluetooth clock support for devices running the PVVX firmware."""
from __future__ import annotations

import asyncio
import logging
import struct
from time import localtime
from typing import TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from bleak.backends.device import BLEDevice
    from bleak.backends.scanner import AdvertisementData

from bleak import BleakClient, BleakGATTCharacteristic

from bluetooth_clocks import BluetoothClock
from bluetooth_clocks.exceptions import InvalidTimeBytesError

_logger = logging.getLogger(__name__)


class PVVX(BluetoothClock):
    """Bluetooth clock support for devices running the PVVX firmware."""

    DEVICE_TYPE = "PVVX"
    SERVICE_UUID = UUID("00001f10-0000-1000-8000-00805f9b34fb")
    CHAR_UUID = UUID("00001f1f-0000-1000-8000-00805f9b34fb")

    TIME_GET_FORMAT = "<BLL"
    """The format string to convert bytes read from the device to a time."""

    TIME_SET_FORMAT = "<BL"
    """The format string to convert a time to bytes written to the PVVX device."""

    WRITE_WITH_RESPONSE = False
    """Writing the time to the PVVX device needs write without response."""

    SERVICE_DATA_UUID = UUID("0000181a-0000-1000-8000-00805f9b34fb")
    """UUID of the service data the PVVX device is advertising."""

    PVVX_GET_SET_TIME_COMMAND = 0x23
    """Command for PVVX firmware to Get/Set Time."""

    def __init__(self, device: BLEDevice) -> None:
        """Create a PVVX object.

        Args:
            device (BLEDevice): The Bluetooth device.
        """
        super().__init__(device)
        self.notified_time = 0.0

    @classmethod
    def recognize(
        cls,
        device: BLEDevice,
        advertisement_data: AdvertisementData,
    ) -> bool:  # ARG003
        """Recognize the PVVX device from advertisement data.

        This checks whether the advertisement has service data with service UUID
        0x181a (PVVX custom format).

        Args:
            device (~bleak.backends.device.BLEDevice): The Bluetooth device.
            advertisement_data (AdvertisementData): The advertisement data.

        Returns:
            bool: ``True`` if the device is recognized as a PVVX device,
            ``False`` otherwise.
        """
        return str(cls.SERVICE_DATA_UUID) in advertisement_data.service_data

    async def get_time(self) -> float:
        """Get the time of the PVVX device.

        Returns:
            float: The time of the Bluetooth clock.
        """
        _logger.info("Connecting to device...")
        async with BleakClient(self.address) as client:
            service = client.services.get_service(self.SERVICE_UUID)
            characteristic = service.get_characteristic(self.CHAR_UUID)

            # Define callback function for notifications and subscribe
            def time_callback(sender: BleakGATTCharacteristic, data: bytearray) -> None:
                """Convert bytes read from a notification to a timestamp."""
                self.notified_time = self.get_time_from_bytes(data)

            await client.start_notify(characteristic, time_callback)

            # Write Get/Set Time command
            await client.write_gatt_char(
                characteristic,
                [self.PVVX_GET_SET_TIME_COMMAND],
                response=self.WRITE_WITH_RESPONSE,
            )

            # Wait for a few seconds so a notification is received.
            await asyncio.sleep(5)

            return self.notified_time

    def get_time_from_bytes(self, time_bytes: bytes) -> float:
        """Convert bytes read from the PVVX device to a timestamp.

        Args:
            time_bytes (bytes): The raw bytes read from the device.

        Raises:
            InvalidTimeBytesError: If `time_bytes` don't have the right format.

        Returns:
            float: The time encoded as a Unix timestamp.
        """
        try:
            _, time_time, _ = struct.unpack(self.TIME_GET_FORMAT, time_bytes)
        except struct.error as exception:
            raise InvalidTimeBytesError(time_bytes) from exception
        return float(time_time)

    def get_bytes_from_time(
        self,
        timestamp: float,
        ampm: bool = False,
    ) -> bytes:
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
        # And add header byte for Get/Set Time command.
        return struct.pack(
            self.TIME_SET_FORMAT,
            self.PVVX_GET_SET_TIME_COMMAND,
            int(timestamp + localtime(timestamp).tm_gmtoff),
        )
