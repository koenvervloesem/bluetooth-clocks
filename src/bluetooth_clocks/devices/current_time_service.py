"""Bluetooth clock support for devices implementing the Current Time Service.

This includes the PineTime with InfiniTime firmware.
"""
from __future__ import annotations

import struct
from datetime import datetime
from uuid import UUID

from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

from bluetooth_clocks import MICROSECONDS, BluetoothClock
from bluetooth_clocks.exceptions import InvalidTimeBytesError


class CurrentTimeService(BluetoothClock):
    """Bluetooth clock support for devices implementing the Current Time Service.

    This implements the standardized Bluetooth service Current Time Service
    (https://www.bluetooth.com/specifications/specs/current-time-service-1-1/).
    """

    DEVICE_TYPE = "Current Time Service"
    SERVICE_UUID = UUID("00001805-0000-1000-8000-00805f9b34fb")
    CHAR_UUID = UUID("00002a2b-0000-1000-8000-00805f9b34fb")

    TIME_GET_FORMAT = "<HBBBBBBB"
    """The format string to convert bytes read from the Current Time Service to a time.

    This starts with an unsigned short in little-endian format, followed by seven bytes.
    """

    TIME_SET_FORMAT = "<HBBBBBBBB"
    """The format string to convert a time to bytes written to the device.

    This starts with an unsigned short in little-endian format, followed by eight bytes.
    """
    WRITE_WITH_RESPONSE = True
    """Writing the time to the Current Time Service needs write with response."""

    @classmethod
    def recognize(
        cls, device: BLEDevice, advertisement_data: AdvertisementData
    ) -> bool:
        """Recognize the Current Time Service from advertisement data.

        This checks whether the Current Time Service's service UUID is in the list
        of advertised service UUIDs.

        Args:
            device (BLEDevice): The Bluetooth device.
            advertisement_data (AdvertisementData): The advertisement data.

        Returns:
            bool: ``True`` if the device is recognized as a Current Time Service,
            ``False`` otherwise.
        """
        return cls.recognize_from_service_uuids(advertisement_data.service_uuids)

    def get_time_from_bytes(self, time_bytes: bytes) -> float:
        """Convert bytes read from the Current Time Service to a timestamp.

        Args:
            time_bytes (bytes): The raw bytes read from the device.

        Raises:
            InvalidTimeBytesError: If `time_bytes` don't have the right format.

        Returns:
            float: The time encoded as a Unix timestamp.
        """
        try:
            (
                year,
                month,
                day,
                hour,
                minute,
                second,
                _,  # weekday
                fractions256,
            ) = struct.unpack(self.TIME_GET_FORMAT, time_bytes)
            date_time = datetime(
                year=year,
                month=month,
                day=day,
                hour=hour,
                minute=minute,
                second=second,
                microsecond=int(fractions256 / 256 * MICROSECONDS),
            )
        except struct.error as exception:
            raise InvalidTimeBytesError(time_bytes) from exception
        return date_time.timestamp()

    def get_bytes_from_time(self, timestamp: float, ampm: bool = False) -> bytes:
        """Generate the bytes to set the time on the Current Time Service.

        Args:
            timestamp (float): The time encoded as a Unix timestamp.
            ampm (bool): ``True`` if the device should show the time with AM/PM,
                ``False`` if it should use 24-hour format. The Current Time Service
                ignores this argument, as it doesn't support this option.

        Returns:
            bytes: The bytes needed to set the time of the device to `timestamp`.
        """
        date_time = datetime.fromtimestamp(timestamp)
        return struct.pack(
            self.TIME_SET_FORMAT,
            date_time.year,
            date_time.month,
            date_time.day,
            date_time.hour,
            date_time.minute,
            date_time.second,
            date_time.weekday() + 1,  # Monday-Sunday -> 0-6
            int(date_time.microsecond / MICROSECONDS * 256),
            0,  # Manual update
        )


class InfiniTime(CurrentTimeService):
    """Bluetooth clock support for the PineTime with InfiniTime firmware."""

    DEVICE_TYPE = "InfiniTime"
    LOCAL_NAME = "InfiniTime"
    """The local name used to recognize this type of device."""

    LOCAL_NAME_STARTS_WITH = False
    """The local name should exactly match `LOCAL_NAME`."""

    @classmethod
    def recognize(
        cls, device: BLEDevice, advertisement_data: AdvertisementData
    ) -> bool:
        """Recognize the PineTime with InfiniTime firmware from advertisement data.

        This checks whether the advertisement data has a local name that is equal
        to or starts with `LOCAL_NAME`.

        Args:
            device (BLEDevice): The Bluetooth device.
            advertisement_data (AdvertisementData): The advertisement data.

        Returns:
            bool: ``True`` if the device is recognized as a PineTime with InfiniTime
            firmware, ``False`` otherwise.
        """
        return cls.recognize_from_local_name(advertisement_data.local_name)
