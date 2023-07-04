.. image:: https://github.com/koenvervloesem/bluetooth-clocks/workflows/tests/badge.svg
    :alt: Continuous Integration
    :target: https://github.com/koenvervloesem/bluetooth-clocks/actions
.. image:: https://img.shields.io/pypi/v/bluetooth-clocks.svg
    :alt: Python package version
    :target: https://pypi.org/project/bluetooth-clocks/
.. image:: https://img.shields.io/pypi/pyversions/bluetooth-clocks.svg
    :alt: Supported Python versions
    :target: https://python.org/
.. image:: https://readthedocs.org/projects/bluetooth-clocks/badge/?version=latest
    :target: https://bluetooth-clocks.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status
.. image:: https://codecov.io/gh/koenvervloesem/bluetooth-clocks/branch/main/graph/badge.svg?token=RQNLC3OTFN
    :alt: Codecov coverage
    :target: https://codecov.io/gh/koenvervloesem/bluetooth-clocks
.. image:: https://img.shields.io/github/license/koenvervloesem/bluetooth-clocks.svg
    :alt: License
    :target: https://github.com/koenvervloesem/bluetooth-clocks/blob/main/LICENSE.txt

|

================
Bluetooth Clocks
================


    Set and get the time on various Bluetooth Low Energy clocks


This project offers a way to easily recognize Bluetooth Low Energy (BLE) clocks from
their advertisements and has a device-independent API to set and get the time on them.

.. image:: https://github.com/koenvervloesem/bluetooth-clocks/raw/main/docs/_static/synchronized-clocks.jpg
    :alt: Synchronize all your Bluetooth Low Energy clocks

.. inclusion-marker-after-intro

Supported devices
=================

Bluetooth Clocks supports the following devices:

+--------------------------+------------+-------------------+-----------+
| Device                   | Set time   | Set 12/24h format | Read time |
+==========================+============+===================+===========+
| `Current Time Service`_  | Yes        | No                | Yes       |
| (e.g. PineTime with      |            |                   |           |
| InfiniTime firmware)     |            |                   |           |
+--------------------------+------------+-------------------+-----------+
| `PVVX firmware`_         | Yes        | No                | Yes       |
| (LYWSD03MMC, MHO-C401,   |            |                   |           |
| CGG1, CGDK2, MJWSD05MMC, |            |                   |           |
| MHO-C122)                |            |                   |           |
+--------------------------+------------+-------------------+-----------+
| Qingping BT Clock Lite   | Yes        | No                | No        |
+--------------------------+------------+-------------------+-----------+
| ThermoPro TP358/TP393    | Yes        | Yes               | No        |
+--------------------------+------------+-------------------+-----------+
| Xiaomi LYWSD02           | Yes        | No                | Yes       |
+--------------------------+------------+-------------------+-----------+

.. _Current Time Service: https://www.bluetooth.com/specifications/specs/current-time-service-1-1/
.. _PVVX firmware: https://github.com/pvvx/ATC_MiThermometer

.. inclusion-marker-before-installation

Installation
============

You can install bluetooth-clocks as a package from PyPI with pip::

    pip install bluetooth-clocks

Usage of the command-line program
=================================

If you have installed the package with ``pip``, you can run the program as ``bluetooth-clocks``::

    $ bluetooth-clocks -h
    usage: bluetooth-clocks [-h] [--version] [-v] [-vv] {discover,get,set} ...

    Bluetooth Clocks

    options:
      -h, --help           show this help message and exit
      --version            show program's version number and exit
      -v, --verbose        set loglevel to INFO
      -vv, --very-verbose  set loglevel to DEBUG

    Subcommands:
      {discover,get,set}
        discover           discover supported Bluetooth clocks
        get                get the time from a Bluetooth clock
        set                set the time of a Bluetooth clock

Discovering Bluetooth clocks
----------------------------

You can discover supported Bluetooth clocks with ``bluetooth-clocks discover``::

    $ bluetooth-clocks discover
    Scanning for supported clocks...
    Found a ThermoPro TP358: address BC:C7:DA:6A:52:C6, name TP358 (52C6)
    Found a Xiaomi LYWSD02: address E7:2E:00:B1:38:96, name LYWSD02
    Found a ThermoPro TP393: address 10:76:36:14:2A:3D, name TP393 (2A3D)
    Found a Qingping BT Clock Lite: address 58:2D:34:54:2D:2C, name Qingping BT Clock Lite
    Found a Current Time Service: address EB:76:55:B9:56:18, name F15

These are the options that the ``discover`` subcommand recognizes::

    $ bluetooth-clocks discover -h
    usage: bluetooth-clocks discover [-h] [-s SCAN_DURATION]

    options:
      -h, --help            show this help message and exit
      -s SCAN_DURATION, --scan-duration SCAN_DURATION
                            scan duration (default: 5 seconds)

Setting the time
----------------

Set the time of a clock with a given Bluetooth address::

    $ bluetooth-clocks set -a E7:2E:00:B1:38:96
    Scanning for device E7:2E:00:B1:38:96...
    Writing time to device...
    Synchronized time

If you want to regularly synchronize the time on the device, you can run this command as a service, e.g. with a systemd service or in a cron job in Linux.

These are the options that the ``set`` subcommand recognizes::

    $ bluetooth-clocks set -h
    usage: bluetooth-clocks set [-h] -a ADDRESS [-s SCAN_DURATION] [-t TIME] [-p]

    options:
      -h, --help            show this help message and exit
      -a ADDRESS, --address ADDRESS
                            Bluetooth address (e.g. 12:34:56:78:9A:BC)
      -s SCAN_DURATION, --scan-duration SCAN_DURATION
                            scan duration (default: 5 seconds)
      -t TIME, --time TIME  the time to set, in ISO 8601 format (e.g. 2023-01-10T16:20,
                            default: current time)
      -p, --am-pm           use AM/PM format (default: 24-hour format)

.. warning::

  Don't be a jerk by changing the time of other people's clocks. Use this tool responsibly.

Getting the time
----------------

Get the time from a clock with a given Bluetooth address::

    $ bluetooth-clocks get -a E7:2E:00:B1:38:96
    Scanning for device E7:2E:00:B1:38:96...
    Reading time from device...
    2023-01-14T17:54:17

These are the options that the ``get`` subcommand recognizes::

    $ bluetooth-clocks get -h
    usage: bluetooth-clocks get [-h] -a ADDRESS [-s SCAN_DURATION]

    options:
      -h, --help            show this help message and exit
      -a ADDRESS, --address ADDRESS
                            Bluetooth address (e.g. 12:34:56:78:9A:BC)
      -s SCAN_DURATION, --scan-duration SCAN_DURATION
                            scan duration (default: 5 seconds)

Usage of the library
====================

The functionality of the command-line program can also be used in your own Python programs by using this project as a library.

See the `module reference <https://bluetooth-clocks.readthedocs.io/en/latest/api/modules.html>`_ for complete API documentation.

.. inclusion-marker-before-license

Documentation
=============

Read the `online documentation <https://bluetooth-clocks.readthedocs.io>`_ of Bluetooth Clocks.

Learn more about Bluetooth Low Energy development
=================================================

If you want to learn more about Bluetooth Low Energy development, read the book `Develop your own Bluetooth Low Energy Applications for Raspberry Pi, ESP32 and nRF52 with Python, Arduino and Zephyr <https://koen.vervloesem.eu/books/develop-your-own-bluetooth-low-energy-applications/>`_ and the accompanying GitHub repository `koenvervloesem/bluetooth-low-energy-applications <https://github.com/koenvervloesem/bluetooth-low-energy-applications>`_.

License
=======

This project is provided by Koen Vervloesem as open source software with the MIT license. See the `LICENSE <https://github.com/koenvervloesem/bluetooth-clocks/blob/main/LICENSE.txt>`_ file for more information.
