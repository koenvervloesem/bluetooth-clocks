"""Bluetooth clock support for Xiaomi devices."""
from __future__ import annotations

import struct
from time import localtime
from uuid import UUID

from bluetooth_clocks import SECONDS_IN_HOUR, BluetoothClock
from bluetooth_clocks.exceptions import InvalidTimeBytesError


class LYWSD02(BluetoothClock):
    """Bluetooth clock support for the Xiaomi LYWSD02."""

    DEVICE_TYPE = "Xiaomi LYWSD02"
    SERVICE_UUID = UUID("ebe0ccb0-7a0a-4b0c-8a1a-6ff2997da3a6")
    """The UUID of the service used to write the time."""

    CHAR_UUID = UUID("ebe0ccb7-7a0a-4b0c-8a1a-6ff2997da3a6")
    """The UUID of the characteristic used to write the time."""

    TIME_GET_FORMAT = "<Lb"
    """The format string to convert bytes read from the device to a time."""

    TIME_SET_FORMAT = "<Lb"
    """The format string to convert a time to bytes written to the device."""

    WRITE_WITH_RESPONSE = False
    """Writing the time to the device needs write without response."""

    LOCAL_NAME = "LYWSD02"
    """The local name used to recognize this type of device."""

    LOCAL_NAME_STARTS_WITH = False
    """The local name should exactly match `LOCAL_NAME`."""

    def get_time_from_bytes(self, time_bytes: bytes) -> float:
        """Convert bytes read from the Xiaomi LYWSD02 to a timestamp.

        Args:
            time_bytes (bytes): The raw bytes read from the device.

        Raises:
            InvalidTimeBytesError: If `time_bytes` don't have the right format.

        Returns:
            float: The time encoded as a Unix timestamp.
        """
        try:
            time_time, _ = struct.unpack(self.TIME_GET_FORMAT, time_bytes)
        except struct.error as exception:
            raise InvalidTimeBytesError(time_bytes) from exception
        return float(time_time)

    def get_bytes_from_time(self, timestamp: float, ampm: bool = False) -> bytes:
        """Generate the bytes to set the time on the Xiaomi LYWSD02.

        Args:
            timestamp (float): The time encoded as a Unix timestamp.
            ampm (bool): ``True`` if the device should show the time with AM/PM,
                ``False`` if it should use 24-hour format. The Xiaomi LYWSD02
                ignores this argument, as it doesn't support this option.

        Returns:
            bytes: The bytes needed to set the time of the device to `timestamp`.
        """
        # Convert timestamp to little-endian unsigned long integer
        # And add timezone offset as a signed byte
        return struct.pack(
            self.TIME_SET_FORMAT,
            int(timestamp),
            localtime(timestamp).tm_gmtoff // SECONDS_IN_HOUR,
        )
