# Reading Busses Home Assistant Integration

A Home Assistant integration for tracking real-time bus information from Reading's open data API.

## Features

- Real-time bus arrival information
- Displays next 3 scheduled services
- Shows actual and expected departure times
- Easy configuration with API key and Stop ID

## Installation

### HACS

1. Open HACS in Home Assistant
2. Go to Integrations
3. Click "Explore & Download Repositories"
4. Search for "Reading Busses"
5. Click "Download"
6. Restart Home Assistant

### Manual

1. Download the `custom_components/reading_bus` folder
2. Place it in your Home Assistant `custom_components` directory
3. Restart Home Assistant

## Configuration

1. Go to **Settings → Devices & Services → Create Integration**
2. Search for "Reading Bus API"
3. Enter your API key (from [reading-opendata.r2p.com](https://reading-opendata.r2p.com))
4. Enter your Stop ID
5. Click Submit

## API Key

Get your free API key from: https://reading-opendata.r2p.com

## Sensors

The integration creates three sensors:

- `sensor.reading_bus_next_service_1` - Next service
- `sensor.reading_bus_next_service_2` - Second next service
- `sensor.reading_bus_next_service_3` - Third next service

Each sensor displays:
- Line name and actual/expected times as the state
- Full journey details as attributes (destination, status, etc.)

## Example Automations

```yaml
- alias: "Notify when bus is soon"
  trigger:
    platform: state
    entity_id: sensor.reading_bus_next_service_1
  action:
    service: notify.notify
    data:
      message: "Bus arriving: {{ trigger.to_state.state }}"
```

## License

MIT
