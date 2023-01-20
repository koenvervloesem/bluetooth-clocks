"""Main entry point for Bluetooth Clocks."""
import asyncio
import logging
import sys
from argparse import ArgumentParser, Namespace
from datetime import datetime

from bleak.exc import BleakError

import bluetooth_clocks
from bluetooth_clocks.exceptions import TimeNotReadableError, UnsupportedDeviceError
from bluetooth_clocks.scanners import discover_clocks, find_clock

__author__ = "Koen Vervloesem"
__copyright__ = "Koen Vervloesem"
__license__ = "MIT"

_logger = logging.getLogger(__name__)


def run() -> None:
    """Calls :func:`main` passing the CLI arguments extracted from :obj:`sys.argv`.

    This function can be used as entry point to create console scripts with setuptools.
    """
    asyncio.run(main(sys.argv[1:]))


async def main(args: list[str]) -> None:
    """Wrapper allowing the bluetooth-clocks command to be called on the command line.

    This wrapper accepts string arguments.

    Args:
      args (list[str]): Command line parameters as list of strings.
    """
    cli_args = parse_args(args)
    setup_logging(cli_args.loglevel)
    await cli_args.func(cli_args)


def parse_args(args: list[str]) -> Namespace:
    """Parse command line parameters.

    Args:
      args (List[str]): command line parameters as list of strings
          (for example  ``["--help"]``).

    Returns:
      :class:`argparse.Namespace`: command line parameters namespace
    """
    parser = ArgumentParser(description="Bluetooth Clocks")
    parser.add_argument(
        "--version",
        action="version",
        version=f"bluetooth-clocks {bluetooth_clocks.__version__}",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        dest="loglevel",
        help="set loglevel to INFO",
        action="store_const",
        const=logging.INFO,
    )
    parser.add_argument(
        "-vv",
        "--very-verbose",
        dest="loglevel",
        help="set loglevel to DEBUG",
        action="store_const",
        const=logging.DEBUG,
    )

    subparsers = parser.add_subparsers(title="Subcommands")
    subparsers.required = True

    # Parser for the "discover" subcommand
    parser_discover = subparsers.add_parser(
        "discover", help="discover supported Bluetooth clocks"
    )
    parser_discover.add_argument(
        "-s",
        "--scan-duration",
        type=float,
        default=5.0,
        help="scan duration (default: 5 seconds)",
    )
    parser_discover.set_defaults(func=discover)

    # Parser for the "get" subcommand
    parser_get = subparsers.add_parser(
        "get", help="get the time from a Bluetooth clock"
    )
    parser_get.add_argument(
        "-a",
        "--address",
        help="Bluetooth address (e.g. 12:34:56:78:9A:BC)",
        required=True,
    )
    parser_get.add_argument(
        "-s",
        "--scan-duration",
        type=float,
        default=5.0,
        help="scan duration (default: 5 seconds)",
    )
    parser_get.set_defaults(func=get_clock_time)

    # Parser for the "set" subcommand
    parser_set = subparsers.add_parser("set", help="set the time of a Bluetooth clock")
    parser_set.add_argument(
        "-a",
        "--address",
        help="Bluetooth address (e.g. 12:34:56:78:9A:BC)",
        required=True,
    )
    parser_set.add_argument(
        "-s",
        "--scan-duration",
        type=float,
        default=5.0,
        help="scan duration (default: 5 seconds)",
    )
    parser_set.add_argument(
        "-t",
        "--time",
        type=str,
        help="the time to set, in ISO 8601 format (e.g. 2023-01-10T16:20, default: current time)",
    )
    parser_set.add_argument(
        "-p",
        "--am-pm",
        help="use AM/PM format (default: 24-hour format)",
        action="store_true",
    )
    parser_set.set_defaults(func=set_clock_time)

    # Return complete parser
    return parser.parse_args(args)


def setup_logging(loglevel: int) -> None:
    """Setup basic logging.

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(
        level=loglevel, stream=sys.stdout, format=logformat, datefmt="%Y-%m-%d %H:%M:%S"
    )


async def discover(args: Namespace) -> None:
    """Discover Bluetooth clocks."""
    found_clock = False

    def device_found(clock: bluetooth_clocks.BluetoothClock) -> None:
        """Show details of recognized clock."""
        nonlocal found_clock
        found_clock = True
        print(f"Found a {clock.DEVICE_TYPE}: address {clock.address}", end="")
        if clock.name:
            print(f", name {clock.name}")

    print("Scanning for supported clocks...")
    await discover_clocks(device_found, args.scan_duration)

    if not found_clock:
        print("No supported clocks found")


async def get_clock_time(args: Namespace) -> None:
    """Get the time of a Bluetooth clock."""
    try:
        print(f"Scanning for device {args.address}...")
        clock = await find_clock(args.address, args.scan_duration)
        if clock:
            print("Reading time from device...")
            received_time = await clock.get_time()
            print(datetime.fromtimestamp(received_time).isoformat())
        else:
            print(f"Didn't find device {args.address}.")
    except UnsupportedDeviceError as exc:
        print(f"Unsupported device: {exc}")
    except TimeNotReadableError:
        print("Device doesn't support reading the time")
    except asyncio.exceptions.TimeoutError as exc:
        print(f"Can't connect to device {args.address}: {exc}")
    except BleakError as exc:
        print(f"Can't read from device {args.address}: {exc}")
    except AttributeError as exc:
        print(f"Can't get attribute from device {args.address}: {exc}")


async def set_clock_time(args: Namespace) -> None:
    """Set the time of a Bluetooth clock."""
    try:
        print(f"Scanning for device {args.address}...")
        clock = await find_clock(args.address, args.scan_duration)
        if clock:
            if args.time:
                timestamp = datetime.fromisoformat(args.time).timestamp()
            else:
                timestamp = None
            print("Writing time to device...")
            await clock.set_time(timestamp, args.am_pm)
            print("Synchronized time")
        else:
            print(f"Didn't find device {args.address}.")
    except UnsupportedDeviceError as exc:
        print(f"Unsupported device: {exc}")
    except asyncio.exceptions.TimeoutError as exc:
        print(f"Can't connect to device {args.address}: {exc}")
    except BleakError as exc:
        print(f"Can't write to device {args.address}: {exc}")
    except AttributeError as exc:
        print(f"Can't get attribute from device {args.address}: {exc}")


if __name__ == "__main__":
    # ^  This is a guard statement that will prevent the following code from
    #    being executed in the case someone imports this file instead of
    #    executing it as a script.
    #    https://docs.python.org/3/library/__main__.html
    run()
