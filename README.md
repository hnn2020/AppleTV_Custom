# Custom Apple TV Component for Home Assistant

This is a custom component for Home Assistant that extends the built-in Apple TV integration with enhanced remote control functionality, specifically adding swipe actions.

## Features

- All standard Apple TV remote functionality
- Added swipe control in four directions (left, right, up, down)
- Configurable swipe sensitivity

## Installation

1. Copy the files to your Home Assistant configuration directory under `custom_components/apple_tv_custom/`.
2. Restart Home Assistant.
3. Configure the component as you would the standard Apple TV integration.

## Usage

### Swipe Commands

The swipe functionality can be called using the remote service with the following commands:

```yaml
service: remote.send_command
target:
  entity_id: remote.apple_tv_living_room
data:
  command: swipe_left  # Can be swipe_left, swipe_right, swipe_up, or swipe_down
  delta: 0.7  # Optional: controls swipe intensity (default is 0.5)
```

### Available Swipe Commands

- `swipe_left`: Swipe from right to left
- `swipe_right`: Swipe from left to right
- `swipe_up`: Swipe from bottom to top
- `swipe_down`: Swipe from top to bottom

### In Automations

Example automation to swipe left when a button is pressed:

```yaml
automation:
  - alias: "Apple TV Swipe Left"
    trigger:
      platform: state
      entity_id: input_boolean.swipe_button
      to: 'on'
    action:
      - service: remote.send_command
        target:
          entity_id: remote.apple_tv_living_room
        data:
          command: swipe_left
```

## Reference

This component builds on the standard Apple TV integration in Home Assistant and uses the [pyatv](https://github.com/postlund/pyatv) library for communication with Apple TV devices.

For more information about the underlying library, visit:
- [pyatv Documentation](https://pyatv.dev/)
- [Apple TV Component in Home Assistant](https://github.com/home-assistant/core/tree/dev/homeassistant/components/apple_tv)