# ERCOT Real-Time SPP Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release][releases-shield]][releases]
![Project Maintenance][maintenance-shield]
[![License][license-shield]](LICENSE)

[![Github Actions][github-actions-shield]][github-actions]
[![GitHub Activity][commits-shield]][commits]
[![GitHub Last Commit][last-commit-shield]][commits]

![Project Stars][stars-shield]
![Project Forks][forks-shield]
![Project Watchers][watchers-shield]

Track real-time electricity prices from ERCOT (Electric Reliability Council of Texas) in Home Assistant. Perfect for automating energy usage based on current grid prices and calculating solar/battery sellback earnings.

## Features

- **Real-time ERCOT prices** - Updates every 5 minutes
- **All 15 zones supported** - Choose from any ERCOT pricing zone
- **Configurable buyback rates** - Tesla Electric, full rate, or custom percentage
- **Lifetime earnings tracking** - For solar/battery exports
- **UI configuration** - No YAML editing needed
- **Easy installation** - Available through HACS

## Installation

1. Ensure [HACS](https://hacs.xyz/) is installed
2. Add this repository to HACS as a custom repository:
   [![Open your Home Assistant instance and open the repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=GrumpyTanker&repository=ERCOT-Settlement-Price-Point&category=integration)
3. Search for "ERCOT" in HACS
4. Install the integration
5. Restart Home Assistant
6. Add the integration via Settings → Devices & Services

## Documentation

For full documentation, see the [README](README.md).

---

[releases-shield]: https://img.shields.io/github/release/GrumpyTanker/ERCOT-Settlement-Price-Point.svg
[releases]: https://github.com/GrumpyTanker/ERCOT-Settlement-Price-Point/releases
[maintenance-shield]: https://img.shields.io/maintenance/yes/2025.svg
[license-shield]: https://img.shields.io/github/license/GrumpyTanker/ERCOT-Settlement-Price-Point.svg

[github-actions-shield]: https://github.com/GrumpyTanker/ERCOT-Settlement-Price-Point/workflows/Validate/badge.svg
[github-actions]: https://github.com/GrumpyTanker/ERCOT-Settlement-Price-Point/actions
[commits-shield]: https://img.shields.io/github/commit-activity/y/GrumpyTanker/ERCOT-Settlement-Price-Point.svg
[commits]: https://github.com/GrumpyTanker/ERCOT-Settlement-Price-Point/commits/main
[last-commit-shield]: https://img.shields.io/github/last-commit/GrumpyTanker/ERCOT-Settlement-Price-Point.svg

[stars-shield]: https://img.shields.io/github/stars/GrumpyTanker/ERCOT-Settlement-Price-Point.svg
[forks-shield]: https://img.shields.io/github/forks/GrumpyTanker/ERCOT-Settlement-Price-Point.svg
[watchers-shield]: https://img.shields.io/github/watchers/GrumpyTanker/ERCOT-Settlement-Price-Point.svg