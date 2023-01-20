"""Test Xiaomi devices."""
from datetime import datetime

import pytest
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

from bluetooth_clocks import supported_devices
from bluetooth_clocks.devices.xiaomi import LYWSD02
from bluetooth_clocks.exceptions import InvalidTimeBytesError

__author__ = "Koen Vervloesem"
__copyright__ = "Koen Vervloesem"
__license__ = "MIT"


def test_in_supported_devices() -> None:
    """Test whether the Xiaomi LYWSD02 is in the list of supported devices."""
    assert LYWSD02.DEVICE_TYPE in supported_devices()


def test_recognize() -> None:
    """Test whether the Xiaomi LYWSD02 is recognized from an advertisement."""
    assert LYWSD02.recognize(
        BLEDevice("E7:2E:00:B1:38:96", "LYWSD02"),
        AdvertisementData(
            local_name="LYWSD02",
            manufacturer_data={},
            platform_data=(),
            rssi=-67,
            service_data={
                "0000fe95-0000-1000-8000-00805f9b34fb": bytes(
                    [
                        0x70,
                        0x20,
                        0x5B,
                        0x04,
                        0x27,
                        0x96,
                        0x38,
                        0xB1,
                        0x00,
                        0x2E,
                        0xE7,
                        0x09,
                        0x04,
                        0x10,
                        0x02,
                        0xD5,
                        0x00,
                    ]
                )
            },
            service_uuids=[
                "0000181a-0000-1000-8000-00805f9b34fb",
                "0000fef5-0000-1000-8000-00805f9b34fb",
            ],
            tx_power=0,
        ),
    )


def test_readable() -> None:
    """Test whether the time is readable on the device."""
    assert LYWSD02.is_readable()


def test_get_time_from_bytes() -> None:
    """Test the conversion from bytes to a timestamp."""
    timestamp = datetime.fromisoformat("2023-01-07 18:41:33+00:00").timestamp()
    assert (
        LYWSD02(BLEDevice("E7:2E:00:B1:38:96")).get_time_from_bytes(
            bytes([0xDD, 0xBC, 0xB9, 0x63, 0x00])
        )
        == timestamp
    )


def test_get_time_from_bytes_invalid() -> None:
    """Test whether trying to convert invalid bytes raises an exception."""
    with pytest.raises(InvalidTimeBytesError):
        LYWSD02(BLEDevice("E7:2E:00:B1:38:96")).get_time_from_bytes(bytes([0x2A]))


def test_get_bytes_from_time() -> None:
    """Test the command to set the time."""
    timestamp = datetime.fromisoformat("2023-01-07 18:41:33+00:00").timestamp()
    # Ignore the timezone offset
    assert LYWSD02(BLEDevice("E7:2E:00:B1:38:96")).get_bytes_from_time(timestamp)[
        :-1
    ] == bytes([0xDD, 0xBC, 0xB9, 0x63])
