"""Test ThermoPro devices."""
from __future__ import annotations

from datetime import datetime
from typing import Type  # noqa: F401 pylint: disable=unused-import

import pytest
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

from bluetooth_clocks import BluetoothClock, supported_devices
from bluetooth_clocks.devices.thermopro import TP358, TP393
from bluetooth_clocks.exceptions import TimeNotReadableError

__author__ = "Koen Vervloesem"
__copyright__ = "Koen Vervloesem"
__license__ = "MIT"


@pytest.mark.parametrize(
    "model",
    [
        TP358,
        TP393,
    ],
)
def test_in_supported_devices(model: type[BluetoothClock]) -> None:
    """Test whether the ThermoPro device is in the list of supported devices."""
    assert model.DEVICE_TYPE in supported_devices()


@pytest.mark.parametrize(
    "model, device, advertisement_data",
    [
        (
            TP358,
            BLEDevice("BC:C7:DA:6A:52:C6", "TP358 (52C6)"),
            AdvertisementData(
                local_name="TP358 (52C6)",
                manufacturer_data={0xD2C2: bytes([0x00, 0x3C, 0x02, 0x2C])},
                platform_data=(),
                rssi=-67,
                service_data={},
                service_uuids=[],
                tx_power=0,
            ),
        ),
        (
            TP393,
            BLEDevice("10:76:36:14:2A:3D", "TP393 (2A3D)"),
            AdvertisementData(
                local_name="TP393 (2A3D)",
                manufacturer_data={0xD0C2: bytes([0x00, 0x3F, 0x02, 0x2C])},
                platform_data=(),
                rssi=-67,
                service_data={},
                service_uuids=[],
                tx_power=0,
            ),
        ),
    ],
)
def test_recognize(
    model: type[BluetoothClock],
    device: BLEDevice,
    advertisement_data: AdvertisementData,
) -> None:
    """Test whether the ThermoPro device is recognized from an advertisement."""
    assert model.recognize(device=device, advertisement_data=advertisement_data)


@pytest.mark.parametrize(
    "model",
    [
        TP358,
        TP393,
    ],
)
def test_not_readable(model: type[BluetoothClock]) -> None:
    """Test whether the time is not readable on the device."""
    assert not model.is_readable()


@pytest.mark.parametrize(
    "model, device, time_bytes",
    [
        (
            TP358,
            BLEDevice("BC:C7:DA:6A:52:C6"),
            bytes([0xA5, 0x16, 0x0C, 0x1D, 0x12, 0x09, 0x01, 0x04, 0x01, 0x5A]),
        ),
        (
            TP393,
            BLEDevice("10:76:36:14:2A:3D"),
            bytes([0xA5, 0x17, 0x01, 0x07, 0x11, 0x20, 0x32, 0x06, 0x00, 0x5A]),
        ),
    ],
)
def test_get_time_from_bytes(
    model: type[BluetoothClock], device: BLEDevice, time_bytes: bytes
) -> None:
    """Test that this class doesn't support conversion from bytes to a timestamp."""
    with pytest.raises(TimeNotReadableError):
        model(device).get_time_from_bytes(time_bytes)


@pytest.mark.parametrize(
    "model, device, time, ampm, time_bytes",
    [
        (
            TP358,
            BLEDevice("BC:C7:DA:6A:52:C6"),
            "2022-12-29 18:09:01",
            False,
            bytes([0xA5, 0x16, 0x0C, 0x1D, 0x12, 0x09, 0x01, 0x04, 0x01, 0x5A]),
        ),
        (
            TP393,
            BLEDevice("10:76:36:14:2A:3D"),
            "2023-01-07 17:32:50",
            True,
            bytes([0xA5, 0x17, 0x01, 0x07, 0x11, 0x20, 0x32, 0x06, 0x00, 0x5A]),
        ),
    ],
)
def test_get_bytes_from_time(
    model: type[BluetoothClock],
    device: BLEDevice,
    time: str,
    ampm: bool,
    time_bytes: bytes,
) -> None:
    """Test the command to set the time."""
    timestamp = datetime.fromisoformat(time).timestamp()
    assert model(device).get_bytes_from_time(timestamp, ampm=ampm) == time_bytes
