# ERCOT Real-Time Settlement Point Prices

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Home Assistant integration for real-time electricity pricing from ERCOT (Electric Reliability Council of Texas).

Track live Settlement Point Prices (SPP) and calculate your solar/battery sellback earnings automatically.

---

## Features

- **Real-time ERCOT prices** - Updates every 5 minutes with the latest Settlement Point Prices
- **All ERCOT zones supported** - Choose from 15 different pricing zones (Load Zones and Hub Zones)
- **Multiple rate calculations** - See prices in $/MWh and ¢/kWh
- **Sellback rate tracking** - Configure your utility's buyback percentage (Tesla Electric 90%, custom, or 100%)
- **Lifetime earnings tracking** - Automatically calculate earnings from grid exports
- **Device grouping** - All sensors grouped under a single ERCOT device
- **Easy configuration** - Set up via UI, no YAML editing required

---

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Click the 3 dots in the top right → Custom repositories
3. Add this repository URL: `https://github.com/yourusername/hass-ercot-spp`
4. Category: Integration
5. Click "Add"
6. Search for "ERCOT" and click Download
7. Restart Home Assistant

### Manual Installation

1. Download the `custom_components/ercot_spp` folder
2. Copy to your Home Assistant `custom_components` directory
3. Restart Home Assistant

---

## Configuration

### Initial Setup

1. Go to **Settings → Devices & Services**
2. Click **+ Add Integration**
3. Search for "ERCOT"
4. Select "ERCOT Real-Time SPP"

### Configuration Options

**ERCOT Pricing Zone**
- Select your zone (LZ_NORTH is most common for DFW area)
- Cannot be changed after setup (would need to remove and re-add)

**Grid Export Energy Sensor** _(Optional)_
- Select the sensor that tracks your solar/battery grid exports
- Must be an energy sensor (kWh)
- Example: `sensor.solaredge_grid_exported`

**Buyback Rate Provider**
- **Tesla Electric (90% of SPP)** - For Tesla Electric customers
- **100% of SPP** - For utilities that pay full market rate
- **Custom Percentage** - Enter your specific buyback rate (1-100%)

**Custom Percentage** _(Only if Custom selected)_
- Enter the percentage your utility pays (e.g., 85%)

---

## Sensors Created

Each integration instance creates these sensors under one device:

| Sensor | Description | Unit | Example |
|--------|-------------|------|---------|
| **Price** | Raw ERCOT Settlement Point Price | $/MWh | 14.72 |
| **Price (¢/kWh)** | Price in consumer-friendly units | ¢/kWh | 1.47 |
| **Last Updated** | Timestamp of last ERCOT update | - | Oct 01, 2025 10:17 |
| **Sellback Rate** | Your export rate | $/kWh | 0.01325 |
| **Sellback Rate (¢/kWh)** | Export rate in cents | ¢/kWh | 1.32 |
| **Sellback Earnings** | Lifetime earnings* | $ | 245.67 |

_*Only created if you configure an export sensor_

---

## ERCOT Zones

### Load Zones (Residential/Small Commercial)
- **LZ_NORTH** - North Texas (DFW, Waco, Abilene)
- **LZ_SOUTH** - South Texas (Corpus Christi, Laredo)
- **LZ_HOUSTON** - Greater Houston area
- **LZ_WEST** - West Texas (Midland, Odessa)
- **LZ_AEN** - AEP Central (central/east Texas)
- **LZ_CPS** - CPS Energy (San Antonio area)
- **LZ_LCRA** - LCRA (Austin area)
- **LZ_RAYBN** - Rayburn Country Electric

### Hub Zones (Wholesale/Commercial)
- **HB_BUSAVG** - Hub Bus Average
- **HB_HOUSTON** - Houston Hub
- **HB_HUBAVG** - Hub Average
- **HB_NORTH** - North Hub
- **HB_PAN** - Panhandle Hub
- **HB_SOUTH** - South Hub
- **HB_WEST** - West Hub

---

## Usage Examples

### Energy Dashboard

Add the price sensors to your Energy Dashboard to see how prices correlate with your usage:

```yaml
# configuration.yaml
energy:
  price_sensors:
    - sensor.ercot_lz_north_price_cents_kwh
```

### Automations

**Example: Charge battery when prices are low**

```yaml
automation:
  - alias: "Charge Battery - Cheap Power"
    trigger:
      - platform: numeric_state
        entity_id: sensor.ercot_lz_north_price_cents_kwh
        below: 1.0  # Below 1¢/kWh
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.battery_charging
```

**Example: Alert on negative prices**

```yaml
automation:
  - alias: "ERCOT Negative Pricing Alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.ercot_lz_north_price_mwh
        below: 0
    action:
      - service: notify.mobile_app
        data:
          message: "ERCOT prices are negative! Free electricity!"
```

**Example: Export during high prices**

```yaml
automation:
  - alias: "Discharge Battery - High Prices"
    trigger:
      - platform: numeric_state
        entity_id: sensor.ercot_lz_north_sellback_rate_cents_kwh
        above: 5.0  # Above 5¢/kWh
    condition:
      - condition: numeric_state
        entity_id: sensor.battery_level
        above: 20  # Keep 20% reserve
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.battery_discharging
```

### Template Sensors

**Daily earnings estimate**

```yaml
template:
  - sensor:
      - name: "Daily Export Estimate"
        unit_of_measurement: "$"
        state: >
          {% set export_today = states('sensor.daily_solar_export')|float(0) %}
          {% set rate = states('sensor.ercot_lz_north_sellback_rate')|float(0) %}
          {{ (export_today * rate)|round(2) }}
```

---

## Troubleshooting

### Sensors show "unavailable"

1. Check Home Assistant logs: **Settings → System → Logs**
2. Look for errors containing "ercot_spp"
3. Verify ERCOT website is accessible: https://www.ercot.com/content/cdr/html/real_time_spp.html
4. Restart Home Assistant

### Price shows 0

1. Wait 5 minutes for first update
2. Check if ERCOT website has data
3. Verify your zone is correct
4. Check logs for parsing errors

### Earnings not tracking

1. Verify export sensor is configured
2. Check export sensor is working: **Developer Tools → States**
3. Ensure export sensor has `device_class: energy`
4. Export sensor must increment (not reset to 0)

---

## Data Source

This integration scrapes data from:
- **URL**: https://www.ercot.com/content/cdr/html/real_time_spp.html
- **Update Frequency**: Every 5 minutes
- **Data Format**: HTML table with 15-minute interval prices

**Note**: ERCOT prices include:
- 15 Minute Online Reserve Price Adders
- Real-Time Online Reliability Deployment Price Adders

---

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes with clear commit messages
4. Test thoroughly
5. Submit a pull request

---

## License

MIT License - see LICENSE file for details

---

## Disclaimer

This integration is not affiliated with or endorsed by ERCOT. Use at your own risk. 

Price data is provided as-is from ERCOT's public website. For official pricing and billing, consult your utility provider.

---

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/hass-ercot-spp/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/hass-ercot-spp/discussions)
- **Home Assistant Community**: [Forum Thread](https://community.home-assistant.io)

---

## Credits

Created by [Your Name]

Special thanks to the Home Assistant community and ERCOT for providing public data access.