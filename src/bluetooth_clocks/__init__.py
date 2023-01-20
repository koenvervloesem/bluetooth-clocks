"""Set and get the time on various Bluetooth clocks.

This project offers a way to easily recognize Bluetooth Low Energy clocks from their
advertisements and has a device-independent API to set and get the time on them.
"""
from __future__ import annotations

import logging
import sys
from abc import ABC, abstractmethod
from importlib import import_module
from inspect import isclass
from pathlib import Path
from pkgutil import iter_modules
from time import time
from typing import ClassVar, Type  # noqa: F401
from uuid import UUID

from bleak import BleakClient
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

from bluetooth_clocks.exceptions import TimeNotReadableError, UnsupportedDeviceError

if sys.version_info[:2] >= (3, 8):
    from importlib.metadata import PackageNotFoundError, version  # pragma: no cover
else:
    from importlib_metadata import PackageNotFoundError, version  # pragma: no cover

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = "bluetooth-clocks"  # pylint: disable=invalid-name
    __version__ = version(dist_name)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"
finally:
    del version, PackageNotFoundError

_logger = logging.getLogger(__name__)


SECONDS_IN_HOUR = 3_600
"""The number of seconds in an hour.

You can use this constant in subclasses of :class:`BluetoothClock`.
"""

MICROSECONDS = 1_000_000
"""The number of microseconds in a second.

You can use this constant in subclasses of :class:`BluetoothClock`.
"""


_supported_devices: list[type[BluetoothClock]] = []
"""Registry of all :class:`BluetoothClock` subclasses for supported devices."""


def supported_devices() -> list[str]:
    """Get a list of names of supported devices.

    Returns:
        list[str]: A list of the names of devices supported by this library.

    Example:
        >>> from bluetooth_clocks import supported_devices
        >>> "ThermoPro TP393" in supported_devices()
        True
    """
    return [device.DEVICE_TYPE for device in _supported_devices]


class BluetoothClock(ABC):
    """Abstract class that represents the definition of a Bluetooth clock.

    Support for every type of Bluetooth clock is implemented as a separate
    subclass by giving the class variables a value and/or by overriding
    methods or implementing abstract methods of this class.

    Attributes:
        address (str): The Bluetooth address of the device.
        name (str | None): The name of the device, or ``None`` if it doesn't
          have a name.
    """

    DEVICE_TYPE: ClassVar[str]  # noqa: CCE001
    """The name of the device type."""

    SERVICE_UUID: ClassVar[UUID]  # noqa: CCE001
    """The UUID of the service used to read/write the time."""

    CHAR_UUID: ClassVar[UUID]  # noqa: CCE001
    """The UUID of the characteristic used to read/write the time."""

    TIME_GET_FORMAT: ClassVar[str | None]  # noqa: CCE001
    """The format string to convert bytes read from the device to a time.

    This is ``None`` if the device doesn't support reading the time.
    """

    TIME_SET_FORMAT: ClassVar[str]  # noqa: CCE001
    """The format string to convert a time to bytes written to the device."""

    WRITE_WITH_RESPONSE: ClassVar[bool]  # noqa: CCE001
    """``True`` if the bytes to set the time should use write with response."""

    LOCAL_NAME: ClassVar[str | None]  # noqa: CCE001
    """The local name used to recognize this type of device.

    This is ``None`` if the local name isn't used to recognize the device."""

    LOCAL_NAME_STARTS_WITH: ClassVar[bool | None]  # noqa: CCE001
    """Whether the local name should start with `LOCAL_NAME`.

    ``True`` if the start of `LOCAL_NAME` is used to recognize this type of device.
    ``False`` if the local name should exactly match `LOCAL_NAME`.
    This is ``None`` if the local name isn't used to recognize the device.
    """

    def __init__(self, device: BLEDevice) -> None:
        """Create a BluetoothClock object.

        Args:
            device (BLEDevice): The Bluetooth device.
        """
        self.address = device.address
        self.name = device.name

    @classmethod
    def create_from_advertisement(
        cls, device: BLEDevice, advertisement_data: AdvertisementData
    ) -> BluetoothClock:
        """Create object of a :class:`BluetoothClock` subclass from advertisement data.

        This is a factory method that you use if you don't know the exact device type
        beforehand. This method automatically recognizes the device type and creates
        an object of the corresponding subclass.

        Args:
            device (BLEDevice): The Bluetooth device.
            advertisement_data (~bleak.backends.scanner.AdvertisementData): The
              advertisement data.

        Raises:
            UnsupportedDeviceError: If the device with address `address` isn't
              supported.

        Returns:
            :class:`BluetoothClock`: An object of the subclass corresponding to
            the recognized device type.
        """
        for device_class in _supported_devices:
            if device_class.recognize(device, advertisement_data):
                return device_class(device)
        raise UnsupportedDeviceError(device, advertisement_data)

    @classmethod
    def is_readable(cls) -> bool:
        """Test whether you can read the time from this device.

        Returns:
            bool: ``True`` if this device supports reading the time, ``False``
            otherwise.

        Example:
            >>> from bluetooth_clocks.devices.xiaomi import LYWSD02
            >>> from bluetooth_clocks.devices.qingping import CGC1
            >>> LYWSD02.is_readable()
            True
            >>> CGC1.is_readable()
            False
        """
        return bool(cls.TIME_GET_FORMAT)

    @classmethod
    def recognize(
        cls,
        device: BLEDevice,  # pylint: disable=unused-argument
        advertisement_data: AdvertisementData,
    ) -> bool:
        """Recognize this device type from advertisement data.

        By default this checks whether the advertisement data has a local name
        that is equal to or starts with `LOCAL_NAME`, by calling
        :meth:`recognize_from_local_name`.

        Override this method in a subclass if the device type should be recognized
        in another way from advertisement data.

        Args:
            device (BLEDevice): The Bluetooth device.
            advertisement_data (~bleak.backends.scanner.AdvertisementData): The
              advertisement data.

        Returns:
            bool: ``True`` if this subclass of :class:`BluetoothClock` recognizes the
            device, ``False`` otherwise.
        """
        return cls.recognize_from_local_name(advertisement_data.local_name)

    @classmethod
    def recognize_from_service_uuids(cls, service_uuids: list[str] | None) -> bool:
        """Recognize this device type from service UUIDs.

        This is a helper method that subclasses can use to implement their
        :meth:`recognize` method.

        Args:
            service_uuids (list[str] | None = None): Service UUIDs of the device, or
              ``None`` if the device doesn't advertise service UUIDs.

        Returns:
            bool: ``True`` if this subclass of :class:`BluetoothClock` recognizes the
            device from the service UUIDs in `service_uuids`, ``False`` otherwise.

        """
        if service_uuids is None:
            # The device doesn't advertise service UUIDs
            return False
        return str(cls.SERVICE_UUID) in service_uuids

    @classmethod
    def recognize_from_local_name(
        cls,
        local_name: str | None,
    ) -> bool:
        """Recognize the device from an advertised local name.

        This is a helper method that subclasses can use to implement their
        :meth:`recognize` method.

        Args:
            local_name (str | None = None): The local name of the device, or ``None`` if
              it doesn't advertise its local name.

        Returns:
            bool: ``True`` if this subclass of :class:`BluetoothClock` recognizes the
            device from its local name `local_name`, ``False`` otherwise.

        """
        if local_name is None or cls.LOCAL_NAME is None:
            # The device doesn't advertise a local name
            # or the device type can't be recognized by its local name.
            return False
        if cls.LOCAL_NAME_STARTS_WITH:
            return local_name.startswith(cls.LOCAL_NAME)
        return local_name == cls.LOCAL_NAME

    def get_time_from_bytes(  # pylint: disable=unused-argument
        self, time_bytes: bytes
    ) -> float:
        """Convert bytes read from a device to a timestamp.

        Override this method in a subclass for a device that supports getting the time.

        Args:
            time_bytes (bytes): The raw bytes read from the device.

        Raises:
            InvalidTimeBytesError: If `time_bytes` don't have the right format.
            TimeNotReadableError: If the device doesn't support getting the time.

        Returns:
            float: The time encoded as a Unix timestamp.

        Example:
            >>> from bluetooth_clocks.devices.xiaomi import LYWSD02
            >>> from bleak.backends.device import BLEDevice
            >>> from datetime import datetime
            >>> clock = LYWSD02(BLEDevice("E7:2E:00:B1:38:96"))
            >>> timestamp = clock.get_time_from_bytes(
            ...             bytes([0xcd, 0xae, 0xb9, 0x63, 0x01]))
            >>> print(datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S"))
            2023-01-07 18:41:33
        """
        raise TimeNotReadableError

    @abstractmethod
    def get_bytes_from_time(self, timestamp: float, ampm: bool = False) -> bytes:
        """Generate the bytes to set the time on this device.

        Override this method in a subclass to implement the device's time format.

        Args:
            timestamp (float): The time encoded as a Unix timestamp.
            ampm (bool): ``True`` if the device should show the time with AM/PM,
                ``False`` if it should use 24-hour format. Devices that don't
                support choosing the mode can ignore this argument.

        Returns:
            bytes: The bytes needed to set the time of the device to `timestamp`.

        Example:
            >>> from bluetooth_clocks.devices.thermopro import TP393
            >>> from bleak.backends.device import BLEDevice
            >>> from datetime import datetime
            >>> clock = TP393(BLEDevice("10:76:36:14:2A:3D"))
            >>> timestamp = datetime.fromisoformat("2023-01-07 17:32:50").timestamp()
            >>> clock.get_bytes_from_time(timestamp, ampm=True).hex()
            'a517010711203206005a'
        """

    async def get_time(self) -> float:
        """Get the time of the Bluetooth clock.

        Raises:
            TimeNotReadableError: If the device doesn't support getting the time.

        Returns:
            float: The time of the Bluetooth clock.
        """
        # Don't try to connect if the device doesn't support getting the time.
        if not self.is_readable():
            raise TimeNotReadableError

        _logger.info("Connecting to device...")
        async with BleakClient(self.address) as client:
            service = client.services.get_service(self.SERVICE_UUID)
            characteristic = service.get_characteristic(self.CHAR_UUID)
            time_bytes = await client.read_gatt_char(characteristic)
            return self.get_time_from_bytes(time_bytes)

    async def set_time(
        self, timestamp: float | None = None, ampm: bool = False
    ) -> None:
        """Set the time of the Bluetooth clock.

        Args:
            timestamp (float | None = None): The timestamp to write to the clock. If
              this is ``None``, the current time is used.
            ampm (bool): ``True`` if the device should show the time with AM/PM,
                ``False`` if it should use 24-hour format. Devices that don't
                support choosing the mode can ignore this argument.
        """
        async with BleakClient(self.address) as client:
            service = client.services.get_service(self.SERVICE_UUID)
            characteristic = service.get_characteristic(self.CHAR_UUID)
            if timestamp is None:
                # Use the current time if the time is not specified.
                timestamp = time()
            await client.write_gatt_char(
                characteristic,
                self.get_bytes_from_time(timestamp, ampm),
                response=self.WRITE_WITH_RESPONSE,
            )


# Iterate through the modules in the module `device`.
package_dir = Path(__file__).resolve().parent / "devices"
for (_, module_name, _) in iter_modules([str(package_dir)]):  # type: ignore

    # Import the module and iterate through its attributes
    module = import_module(f"{__name__}.devices.{module_name}")
    for attribute_name in dir(module):
        attribute = getattr(module, attribute_name)

        if isclass(attribute) and hasattr(attribute, "DEVICE_TYPE"):
            _supported_devices.append(attribute)
