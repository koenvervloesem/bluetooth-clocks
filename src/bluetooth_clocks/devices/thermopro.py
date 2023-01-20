"""Bluetooth clock support for ThermoPro sensors with clock."""
from __future__ import annotations

from datetime import datetime
from struct import pack
from uuid import UUID

from bluetooth_clocks import BluetoothClock


class TPXXX(BluetoothClock):
    """Bluetooth clock support for ThermoPro sensors with clock.

    This class isn't meant to be instantiated. Subclasses implement support for
    specific ThermoPro device types by giving values to the class variables
    `DEVICE_TYPE`, `LOCAL_NAME`, and `LOCAL_NAME_STARTS_WITH`.
    """

    SERVICE_UUID = UUID("00010203-0405-0607-0809-0a0b0c0d1910")
    """The UUID of the service used to write the time."""

    CHAR_UUID = UUID("00010203-0405-0607-0809-0a0b0c0d2b11")
    """The UUID of the characteristic used to write the time."""

    TIME_GET_FORMAT = None
    """ThermoPro devices don’t support reading the time."""

    TIME_SET_FORMAT = "BBBBBBBBBB"
    """The format string to convert a time to bytes written to the device.

    These are ten bytes.
    """

    WRITE_WITH_RESPONSE = False
    """Writing the time to ThermoPro devices needs write without response."""

    def get_bytes_from_time(self, timestamp: float, ampm: bool = False) -> bytes:
        """Generate the bytes to set the time on ThermoPro devices.

        Args:
            timestamp (float): The time encoded as a Unix timestamp.
            ampm (bool): ``True`` if the device should show the time with AM/PM,
                ``False`` if it should use 24-hour format.

        Returns:
            bytes: The bytes needed to set the time of the device to `timestamp`.
        """
        date_time = datetime.fromtimestamp(timestamp)
        return pack(
            self.TIME_SET_FORMAT,
            0xA5,
            date_time.year % 2000,
            date_time.month,
            date_time.day,
            date_time.hour,
            date_time.minute,
            date_time.second,
            date_time.weekday() + 1,  # Monday-Sunday -> 0-6
            int(not ampm),
            0x5A,
        )


class TP358(TPXXX):  # pylint: disable=too-few-public-methods
    """Bluetooth clock support for the ThermoPro TP358."""

    DEVICE_TYPE = "ThermoPro TP358"
    LOCAL_NAME = "TP358"
    """The local name used to recognize this type of device."""

    LOCAL_NAME_STARTS_WITH = True
    """The local name should start with `LOCAL_NAME`."""


class TP393(TPXXX):  # pylint: disable=too-few-public-methods
    """Bluetooth clock support for the ThermoPro TP393."""

    DEVICE_TYPE = "ThermoPro TP393"
    LOCAL_NAME = "TP393"
    """The local name used to recognize this type of device."""

    LOCAL_NAME_STARTS_WITH = True
    """The local name should start with `LOCAL_NAME`."""
