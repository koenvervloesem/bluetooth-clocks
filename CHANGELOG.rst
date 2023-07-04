=========
Changelog
=========

Version 0.2.0: Get time from PVVX (2023-07-04)
==============================================

This release adds support for reading the time from devices with PVVX firmware.

* Migrate code linting to Ruff, apply fixes by @koenvervloesem in https://github.com/koenvervloesem/bluetooth-clocks/pull/15
* Add MJWSD05MMC and MHO-C122 to list of supported PVVX models by @koenvervloesem in https://github.com/koenvervloesem/bluetooth-clocks/pull/16
* Assume if TYPE_CHECKING is covered by @koenvervloesem in https://github.com/koenvervloesem/bluetooth-clocks/pull/17
* Deprecate Python 3.7 by @koenvervloesem in https://github.com/koenvervloesem/bluetooth-clocks/pull/18
* Add read time command for PVVX firmware by @koenvervloesem in https://github.com/koenvervloesem/bluetooth-clocks/pull/19

Version 0.1.2: Local time, please (2023-02-02)
==============================================

This is a bugfix release. Previously the time on Qingping devices and devices running the PVVX ATC firmware was set to UTC instead of local time.

* Autoupdate pre-commit by @koenvervloesem in https://github.com/koenvervloesem/bluetooth-clocks/pull/12
* Fix local time on PVVX and Qingping devices by @koenvervloesem in https://github.com/koenvervloesem/bluetooth-clocks/pull/13

Version 0.1.1 (2023-01-23)
==========================

This is a bugfix release.

* Fix doctest: use UTC in get_time_from_bytes example by @koenvervloesem in https://github.com/koenvervloesem/bluetooth-clocks/pull/3
* Fix link to Bleak's BLEDevice in docs by @koenvervloesem in https://github.com/koenvervloesem/bluetooth-clocks/pull/4
* Add codecov badge to README by @koenvervloesem in https://github.com/koenvervloesem/bluetooth-clocks/pull/5
* Various documentation fixes by @koenvervloesem in https://github.com/koenvervloesem/bluetooth-clocks/pull/6
* Build documentation on Read The Docs with Python 3.11 by @koenvervloesem in https://github.com/koenvervloesem/bluetooth-clocks/pull/7
* Use Ubuntu 22.04/Python 3.11 for Read The Docs by @koenvervloesem in https://github.com/koenvervloesem/bluetooth-clocks/pull/8
* Update to PyScaffold v4.4 project features by @koenvervloesem in https://github.com/koenvervloesem/bluetooth-clocks/pull/9
* Import future annotations by @koenvervloesem in https://github.com/koenvervloesem/bluetooth-clocks/pull/10

Version 0.1.0 (2023-01-20)
==========================

Initial version of Bluetooth Clocks
