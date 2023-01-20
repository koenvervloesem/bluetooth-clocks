"""Module with exceptions raised by this library."""


class BluetoothClocksError(Exception):
    """Base class for all exceptions raised by this library."""


class InvalidTimeBytesError(BluetoothClocksError):
    """Exception raised when bytes read from a device don't have the right format."""


class TimeNotReadableError(BluetoothClocksError):
    """Exception raised when trying to read the time on a device that doesn't support this."""


class UnsupportedDeviceError(BluetoothClocksError):
    """Exception raised when a device is not supported."""
