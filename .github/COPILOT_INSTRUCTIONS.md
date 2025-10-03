# GitHub Copilot Instructions for ERCOT SPP Integration

## Project Overview

This is a Home Assistant custom integration that provides real-time electricity pricing data from ERCOT (Electric Reliability Council of Texas). The integration scrapes data from ERCOT's public website and creates sensors for price tracking and solar/battery sellback earnings calculation.

## Architecture

### Core Components

1. **`__init__.py`** - Main integration file
   - Handles setup and teardown of the integration
   - Contains `ERCOTDataUpdateCoordinator` class that fetches data every 5 minutes
   - Implements HTML scraping logic to extract prices from ERCOT website

2. **`sensor.py`** - Sensor platform
   - Defines 6 sensor entities (5 always created, 1 optional)
   - Base class `ERCOTBaseSensor` provides common functionality
   - Individual sensor classes for different price representations

3. **`config_flow.py`** - UI Configuration
   - Handles initial setup wizard (`ERCOTConfigFlow`)
   - Manages reconfiguration via options flow (`ERCOTOptionsFlow`)
   - Provides dropdown selectors for zones and buyback providers

4. **`const.py`** - Constants
   - Domain name and zone definitions
   - All 15 ERCOT pricing zones (8 Load Zones, 7 Hub Zones)

### Data Flow

```
ERCOT Website → HTML Scraping → Data Coordinator → Sensors → Home Assistant
     (5 min)         (regex)      (parse & store)    (display)
```

## Code Style Guidelines

### Python Conventions
- Use type hints for all function parameters and return values
- Follow Home Assistant's async/await patterns
- Use `_LOGGER` for logging with appropriate levels
- Implement proper error handling with try/except blocks
- Use descriptive variable names that explain purpose

### Documentation Standards
- All functions must have docstrings with Args, Returns, and Raises sections
- Use section markers (===) to separate logical code blocks
- Add inline comments for complex logic, especially regex patterns
- Include examples in docstrings for public-facing methods

### File Headers
Each Python file should have a header block with:
- Title and purpose
- Key features/responsibilities
- Author and license information
- Section markers for organization

## Important Patterns

### Data Coordinator Pattern
```python
class ERCOTDataUpdateCoordinator(DataUpdateCoordinator):
    """Fetches data every 5 minutes via update_interval."""
    
    async def _async_update_data(self):
        """This method is called automatically by Home Assistant."""
        # Fetch HTML, parse, return dict
```

### Sensor Pattern
```python
class MySensor(ERCOTBaseSensor):
    """Inherits from base class for common functionality."""
    
    @property
    def native_value(self):
        """Return sensor value from coordinator.data."""
        return self.coordinator.data.get("key")
```

### Config Flow Pattern
```python
async def async_step_user(self, user_input=None):
    """Show form, validate, create entry."""
    if user_input is not None:
        # Process and create entry
    return self.async_show_form(...)
```

## Data Structures

### Coordinator Data Format
```python
{
    "price_mwh": 14.72,              # Float, price in $/MWh
    "timestamp": "Oct 01, 2025 10:17", # String, last update time
    "date": "10/01/2025",            # String, date from ERCOT
    "time": "1015",                  # String, time from ERCOT (HHMM)
}
```

### Config Entry Data
```python
{
    "zone": "LZ_NORTH",              # String, ERCOT zone identifier
    "export_entity": "sensor.xxx",   # Optional string, entity_id
    "buyback_provider": "Tesla Electric",  # String for UI display
    "sellback_percent": 90,          # Integer, 1-100
}
```

## Testing Considerations

### Manual Testing
- Test with different ERCOT zones
- Verify price calculations ($/MWh → ¢/kWh)
- Test earnings tracking with mock export sensor
- Verify counter reset handling (negative delta)
- Test options flow for reconfiguration

### Edge Cases
- ERCOT website down or returns invalid HTML
- Export sensor returns "unknown" or "unavailable"
- Export counter resets to 0 (daily/weekly reset)
- Negative prices (happens during high wind generation)
- Very high prices during grid emergencies

## Common Tasks

### Adding a New Sensor
1. Create new class inheriting from `ERCOTBaseSensor` in `sensor.py`
2. Define `unique_id`, `name`, `unit_of_measurement`, `state_class`
3. Implement `native_value` property to return data from coordinator
4. Add to sensor list in `async_setup_entry()`

### Adding a New Zone
1. Add zone identifier to `ZONES` list in `const.py`
2. Add zone to `zone_map` dictionary in `__init__.py` `_async_update_data()`
3. Add dropdown option in `config_flow.py` zone selector
4. Update README.md zone documentation

### Modifying Data Fetch Logic
- All scraping logic is in `ERCOTDataUpdateCoordinator._async_update_data()`
- Uses regex pattern `r'<td[^>]*>([^<]+)</td>'` to extract table cells
- Last 17 cells contain most recent price row
- Zone mapping starts at index 2 (0=date, 1=time)

## Dependencies

- **aiohttp**: HTTP client for async web scraping
- **Home Assistant Core**: Integration framework
- **Python 3.9+**: Minimum Python version

## External Resources

- ERCOT Data Source: https://www.ercot.com/content/cdr/html/real_time_spp.html
- Home Assistant Dev Docs: https://developers.home-assistant.io/
- HACS Documentation: https://hacs.xyz/

## Version Management

- Use semantic versioning (MAJOR.MINOR.PATCH)
- Update version in `manifest.json` and `CHANGELOG.md`
- Create git tags for releases: `git tag v1.1.0`
- Update CHANGELOG.md with all changes

## AI Agent Guidelines

When making changes:
1. **Preserve existing functionality** - Don't break working code
2. **Follow established patterns** - Match existing code style
3. **Document thoroughly** - Update comments and docstrings
4. **Test edge cases** - Consider error scenarios
5. **Update documentation** - Modify README.md and CHANGELOG.md as needed
6. **Maintain backwards compatibility** - Don't break existing configurations
7. **Use descriptive names** - Make code self-documenting
8. **Handle errors gracefully** - Log errors, don't crash Home Assistant
9. **Respect Home Assistant conventions** - Follow HA coding standards
10. **Think about users** - Consider UX impact of changes
