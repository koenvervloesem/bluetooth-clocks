"""Test PVVX devices."""
from time import time

import pytest
import time_machine
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

from bluetooth_clocks import supported_devices
from bluetooth_clocks.devices.pvvx import PVVX
from bluetooth_clocks.exceptions import TimeNotReadableError

__author__ = "Koen Vervloesem"
__copyright__ = "Koen Vervloesem"
__license__ = "MIT"


def test_in_supported_devices() -> None:
    """Test whether PVVX is in the list of supported devices."""
    assert PVVX.DEVICE_TYPE in supported_devices()


def test_recognize() -> None:
    """Test whether PVVX is recognized from an advertisement."""
    assert PVVX.recognize(
        BLEDevice("A4:C1:38:D9:01:10", "LYWSD03MMC"),
        AdvertisementData(
            local_name="LYWSD03MMC",
            manufacturer_data={},
            platform_data=(),
            rssi=-67,
            service_data={
                "0000181a-0000-1000-8000-00805f9b34fb": bytes(
                    [
                        0x10,
                        0x01,
                        0xD9,
                        0x38,
                        0xC1,
                        0xA4,
                        0xA4,
                        0x08,
                        0xDD,
                        0x18,
                        0x14,
                        0x0C,
                        0x64,
                        0xDC,
                        0x05,
                    ]
                )
            },
            service_uuids=[],
            tx_power=0,
        ),
    )


def test_readable() -> None:
    """Test whether the time is readable on the device."""
    assert not PVVX.is_readable()


def test_get_time_from_bytes() -> None:
    """Test the conversion from bytes to a timestamp."""
    with pytest.raises(TimeNotReadableError):
        PVVX(BLEDevice("A4:C1:38:D9:01:10")).get_time_from_bytes(
            bytes([0x23, 0xDD, 0xBC, 0xB9, 0x63])
        )


@time_machine.travel("2023-01-07 18:41:33 +0000")
def test_get_bytes_from_time() -> None:
    """Test the command to set the time."""
    assert PVVX(BLEDevice("A4:C1:38:D9:01:10")).get_bytes_from_time(time()) == bytes(
        [0x23, 0xDD, 0xBC, 0xB9, 0x63]
    )
