"""Bluetooth clock support for Qingping clocks."""
from __future__ import annotations

from struct import pack
from uuid import UUID

from bluetooth_clocks import BluetoothClock


class CGC1(BluetoothClock):
    """Bluetooth clock support for the Qingping BT Clock Lite (CGC1)."""

    DEVICE_TYPE = "Qingping BT Clock Lite"
    SERVICE_UUID = UUID("22210000-554a-4546-5542-46534450464d")
    """The UUID of the service used to write the time."""

    CHAR_UUID = UUID("00000001-0000-1000-8000-00805f9b34fb")
    """The UUID of the characteristic used to write the time."""

    TIME_GET_FORMAT = None
    """The Qingping BT Clock Lite doesn't support reading the time."""

    TIME_SET_FORMAT = "<BBL"
    """The format string to convert a time to bytes written to the device.

    This starts with two bytes, followed by an unsigned long in little-endian
    format.
    """

    WRITE_WITH_RESPONSE = True
    """We use write with response to write the time to the Qingping BT Clock Lite.

    Note: The device also supports write without reponse.
    """

    LOCAL_NAME = "Qingping BT Clock Lite"
    """The local name used to recognize this type of device."""

    LOCAL_NAME_STARTS_WITH = False
    """The local name should exactly match `LOCAL_NAME`."""

    def get_bytes_from_time(self, timestamp: float, ampm: bool = False) -> bytes:
        """Generate the bytes to set the time on the Qingping BT Clock Lite.

        Args:
            timestamp (float): The time encoded as a Unix timestamp.
            ampm (bool): ``True`` if the device should show the time with AM/PM,
                ``False`` if it should use 24-hour format. The Qingping BT Clock
                Lite ignores this argument, as it doesn’t support this option.

        Returns:
            bytes: The bytes needed to set the time of the device to `timestamp`.
        """
        return pack(self.TIME_SET_FORMAT, 0x05, 0x09, int(timestamp))
