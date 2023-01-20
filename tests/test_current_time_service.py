"""Test Current Time Service devices."""
from __future__ import annotations

from datetime import datetime
from typing import Type  # noqa: F401 pylint: disable=unused-import

import pytest
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

from bluetooth_clocks import BluetoothClock, supported_devices
from bluetooth_clocks.devices.current_time_service import CurrentTimeService, InfiniTime
from bluetooth_clocks.exceptions import InvalidTimeBytesError

__author__ = "Koen Vervloesem"
__copyright__ = "Koen Vervloesem"
__license__ = "MIT"


@pytest.mark.parametrize(
    "model",
    [
        CurrentTimeService,
        InfiniTime,
    ],
)
def test_in_supported_devices(model: type[BluetoothClock]) -> None:
    """Test whether the Current Time Service model is in the list of supported devices."""
    assert model.DEVICE_TYPE in supported_devices()


@pytest.mark.parametrize(
    "model, device, advertisement_data",
    [
        (
            CurrentTimeService,
            BLEDevice("EB:76:55:B9:56:18", "F15"),
            AdvertisementData(
                local_name="F15",
                manufacturer_data={},
                platform_data=(),
                rssi=-67,
                service_data={},
                service_uuids=[
                    "00001805-0000-1000-8000-00805f9b34fb",
                    "0000180a-0000-1000-8000-00805f9b34fb",
                    "0000180d-0000-1000-8000-00805f9b34fb",
                    "0000fee7-0000-1000-8000-00805f9b34fb",
                    "0000feea-0000-1000-8000-00805f9b34fb",
                ],
                tx_power=0,
            ),
        ),
        (
            InfiniTime,
            BLEDevice("F3:BE:3E:97:17:A4", "InfiniTime"),
            AdvertisementData(
                local_name="InfiniTime",
                manufacturer_data={},
                platform_data=(),
                rssi=-67,
                service_data={},
                service_uuids=["00001530-1212-efde-1523-785feabcd123"],
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
    """Test whether the Current Time Service model is recognized from an advertisement."""
    assert model.recognize(device=device, advertisement_data=advertisement_data)


@pytest.mark.parametrize(
    "model",
    [
        CurrentTimeService,
        InfiniTime,
    ],
)
def test_readable(model: type[BluetoothClock]) -> None:
    """Test whether the time is readable on the device."""
    assert model.is_readable()


@pytest.mark.parametrize(
    "model, device, time_bytes, time",
    [
        (
            CurrentTimeService,
            BLEDevice("EB:76:55:B9:56:18"),
            bytes([0xE7, 0x07, 0x01, 0x07, 0x12, 0x29, 0x21, 0x06, 0x00]),
            "2023-01-07 18:41:33",
        ),
        (
            InfiniTime,
            BLEDevice("F3:BE:3E:97:17:A4"),
            bytes([0xE7, 0x07, 0x01, 0x07, 0x12, 0x29, 0x21, 0x06, 0x00]),
            "2023-01-07 18:41:33",
        ),
    ],
)
def test_get_time_from_bytes(
    model: type[BluetoothClock], device: BLEDevice, time_bytes: bytes, time: str
) -> None:
    """Test the conversion from bytes to a timestamp."""
    timestamp = datetime.fromisoformat(time).timestamp()
    assert model(device).get_time_from_bytes(time_bytes) == timestamp


@pytest.mark.parametrize(
    "model, device, time_bytes",
    [
        (
            CurrentTimeService,
            BLEDevice("EB:76:55:B9:56:18"),
            bytes([0x2A]),
        ),
        (
            InfiniTime,
            BLEDevice("F3:BE:3E:97:17:A4"),
            bytes([0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09]),
        ),
    ],
)
def test_get_time_from_bytes_invalid(
    model: type[BluetoothClock], device: BLEDevice, time_bytes: bytes
) -> None:
    """Test whether trying to convert invalid bytes raises an exception."""
    with pytest.raises(InvalidTimeBytesError):
        model(device).get_time_from_bytes(time_bytes)


@pytest.mark.parametrize(
    "model, device, time, time_bytes",
    [
        (
            CurrentTimeService,
            BLEDevice("EB:76:55:B9:56:18"),
            "2023-01-07 18:41:33",
            bytes([0xE7, 0x07, 0x01, 0x07, 0x12, 0x29, 0x21, 0x06, 0x00, 0x00]),
        ),
        (
            InfiniTime,
            BLEDevice("F3:BE:3E:97:17:A4"),
            "2023-01-07 18:41:33",
            bytes([0xE7, 0x07, 0x01, 0x07, 0x12, 0x29, 0x21, 0x06, 0x00, 0x00]),
        ),
    ],
)
def test_get_bytes_from_time(
    model: type[BluetoothClock], device: BLEDevice, time: str, time_bytes: bytes
) -> None:
    """Test the command to set the time."""
    timestamp = datetime.fromisoformat(time).timestamp()
    assert model(device).get_bytes_from_time(timestamp) == bytes(time_bytes)
