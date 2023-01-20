"""Test the BluetoothClock abstract class."""
import pytest
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

from bluetooth_clocks import BluetoothClock, supported_devices
from bluetooth_clocks.devices.xiaomi import LYWSD02
from bluetooth_clocks.exceptions import UnsupportedDeviceError

__author__ = "Koen Vervloesem"
__copyright__ = "Koen Vervloesem"
__license__ = "MIT"


def test_supported_devices() -> None:
    """Test whether the list of supported devices isn't empty."""
    assert supported_devices()


def test_create_from_advertisement() -> None:
    """Test whether an object of the right subclass is created from an advertisement."""
    assert isinstance(
        BluetoothClock.create_from_advertisement(
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
        ),
        LYWSD02,
    )


def test_create_from_advertisement_unknown() -> None:
    """Test whether no subclass is created from an unknown advertisement."""
    with pytest.raises(UnsupportedDeviceError):
        BluetoothClock.create_from_advertisement(
            BLEDevice("45:B4:07:8A:66:6A"),
            AdvertisementData(
                local_name=None,
                manufacturer_data={
                    0x004C: bytes([0x10, 0x05, 0x47, 0x1C, 0x7F, 0xF1, 0x93])
                },
                platform_data=(),
                rssi=-67,
                service_data={},
                service_uuids=[],
                tx_power=0,
            ),
        )
