# Mopeka Enhanced

This is an enhanced version of Home Assistant's native Mopeka integration by `@bdraco`. It continues to use the mopeka_ble_iot library to interface with the sensors. No changes have been made there.

The code changes I have made are mainly to add tank presets, calculations for horizontal tank geometry, custom tank sizes, and new sensors. In the past you would have had only the tank level sensor that displays inches, and it was up to you to create the proper template sensors to display percentage or gallons. No longer!

I've taken the 20 lb, 30 lb, and 40 lb vertical tank measurements from the Mopeka ESPHome component, as I believe they may have pulled them from the official Mopeka app. The rest of the tank measruemtns were obtained from extension Google searching (both manaul and assisted by Gemini AI). I narowed my research down to only US standard propane tank sizes since that's what I use on our bus. I'll eventually bring over the remaining 6Kg, 11Kg, and 14Kg Euro tank sizes from ESPHome. Feel free to submit a PR here for additional tank presets that you think would be valuable.

This custom mopeka integration will override the native HA integration while keeping any preconfigured Mopeka devices intact. You will have to reconfigure your existing Mopeka devices to use the new tank presets and show the updated tank sensors. 



## Features

- Tank presets for horizontal and vertical style propane tanks in gal/lbs (US standard sizes only)
- Standard IBC tote presets for 275 gallon and 330 gallon sizes (available for all non-propane medium types)
- Option to define your own custom tank height in millimeters, and tank volume in gallons
- Automatic detection of top mount sensor models (TD40 and TD200) for correct sensor measuments (top mount sensors read through the air instead of liquid mediums)
- Updated config flow menu for tank configuration based on medium type selection and device detection (top mount sensors)
- Added background calculations to better handle horizontal propane tank geometry(hemisphere endcaps)
- Added two sensors for tank fill (percentage), and tank volume (gallons)
- Tank volume sensor is derived from the tank presets or from the custom tank config flow. 
- Added two diagnostic sensors for Medium type (currently configured medium), and Tank preset (currently configured tank preset)
 

## Installation (HACS)

1. Open HACS in Home Assistant.
2. Go to Integrations.
3. Open the three-dot menu and select Custom repositories.
4. Add `https://github.com/bb12489/mopeka-enhanced` as category `Integration`.
5. Search for `Mopeka Enhanced` in HACS and install it.
6. Restart Home Assistant.

After restart, add or reconfigure your Mopeka devices from Settings -> Devices & Services.


## Horizontal Tank Geometry



## Notes

- This custom component uses the `mopeka` domain and is intended to override the built-in core integration implementation.
- Keep only one active implementation for the domain to avoid confusion during troubleshooting.

## Acknowledgment

This custom component builds on the original Mopeka integration from Home Assistant Core.
Credit to the original upstream maintainer and codeowner, `@bdraco`, for the core integration foundation.

## Development

The integration code lives in `custom_components/mopeka`.

## License

This project is released under the Apache 2.0 license. See `LICENSE`.
