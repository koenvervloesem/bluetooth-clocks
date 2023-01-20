"""Test Qingping devices."""
from time import time

import pytest
import time_machine
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

from bluetooth_clocks import supported_devices
from bluetooth_clocks.devices.qingping import CGC1
from bluetooth_clocks.exceptions import TimeNotReadableError

__author__ = "Koen Vervloesem"
__copyright__ = "Koen Vervloesem"
__license__ = "MIT"


def test_in_supported_devices() -> None:
    """Test whether the Qingping BT Clock Lite is in the list of supported devices."""
    assert CGC1.DEVICE_TYPE in supported_devices()


def test_recognize() -> None:
    """Test whether the Qingping BT Clock Lite is recognized from an advertisement."""
    assert CGC1.recognize(
        BLEDevice("58:2D:34:54:2D:2C", "Qingping BT Clock Lite"),
        AdvertisementData(
            local_name="Qingping BT Clock Lite",
            manufacturer_data={},
            platform_data=(),
            rssi=-67,
            service_data={
                "0000fdcd-0000-1000-8000-00805f9b34fb": bytes(
                    [
                        0x88,
                        0x1E,
                        0x2C,
                        0x2D,
                        0x54,
                        0x34,
                        0x2D,
                        0x58,
                        0x01,
                        0x04,
                        0xD2,
                        0x00,
                        0x80,
                        0x02,
                        0x02,
                        0x01,
                        0x64,
                    ]
                )
            },
            service_uuids=[],
            tx_power=0,
        ),
    )


def test_not_readable() -> None:
    """Test whether the time is not readable on the device."""
    assert not CGC1.is_readable()


def test_get_time_from_bytes() -> None:
    """Test that this class doesn't support conversion from bytes to a timestamp."""
    with pytest.raises(TimeNotReadableError):
        CGC1(BLEDevice("58:2D:34:54:2D:2C")).get_time_from_bytes(
            bytes([0x05, 0x09, 0x00, 0xF6, 0xAE, 0x63])
        )


@time_machine.travel("2022-12-30 15:30:24 +0000")
def test_get_bytes_from_time() -> None:
    """Test the command to set the time."""
    assert CGC1(BLEDevice("58:2D:34:54:2D:2C")).get_bytes_from_time(time()) == bytes(
        [0x05, 0x09, 0x10, 0x04, 0xAF, 0x63]
    )
