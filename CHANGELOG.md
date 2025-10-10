# Changelog

All notable changes to the ERCOT Real-Time Settlement Point Prices integration will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-10-10

### Added
- Comprehensive code documentation and comments throughout all modules
- CHANGELOG.md for tracking version history
- Enhanced docstrings for all classes and methods to improve AI agent understanding
- Detailed inline comments explaining complex logic and algorithms
- Copilot-friendly instructions and documentation structure

### Changed
- Updated all file headers with consistent formatting and detailed purpose descriptions
- Improved code organization with better section markers
- Enhanced README.md with clearer structure and more detailed examples
- Updated manifest.json with comprehensive metadata

### Documentation
- Added detailed comments to data scraping logic in __init__.py
- Enhanced sensor class documentation with usage examples
- Improved config flow documentation with step-by-step explanations
- Added comprehensive module-level docstrings

## [1.0.3] - 2025-01-15

### Fixed
- Minor bug fixes and improvements
- Stability enhancements for data fetching

## [1.0.2] - 2025-01-10

### Added
- Initial HACS support
- Basic sensor functionality

## [1.0.1] - 2025-01-05

### Added
- Configuration flow for easy setup
- Multiple pricing zone support

## [1.0.0] - 2025-01-01

### Added
- Initial release
- Real-time ERCOT price tracking
- Support for all 15 ERCOT pricing zones
- Sellback rate calculation
- Grid export earnings tracking
- Device grouping for sensors
- UI-based configuration
- HACS compatibility

### Features
- Automatic 5-minute price updates
- HTML scraping from ERCOT official website
- Multiple sensor types ($/MWh, ¢/kWh, sellback rates, earnings)
- Configurable buyback percentages (Tesla Electric 90%, Full Rate 100%, Custom)
- Optional lifetime earnings sensor for solar/battery exports
- Error handling and retry logic
- Home Assistant entity naming conventions
- Device and area support

[1.1.0]: https://github.com/GrumpyTanker/ERCOT-Settlement-Price-Point/compare/v1.0.3...v1.1.0
[1.0.3]: https://github.com/GrumpyTanker/ERCOT-Settlement-Price-Point/releases/tag/v1.0.3
[1.0.2]: https://github.com/GrumpyTanker/ERCOT-Settlement-Price-Point/releases/tag/v1.0.2
[1.0.1]: https://github.com/GrumpyTanker/ERCOT-Settlement-Price-Point/releases/tag/v1.0.1
[1.0.0]: https://github.com/GrumpyTanker/ERCOT-Settlement-Price-Point/releases/tag/v1.0.0
