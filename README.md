# Mopeka Enhanced

## Intro

This is an enhanced version of Home Assistant's native Mopeka integration by `@bdraco`. It continues to use the mopeka_ble_iot library to interface with the sensors. No changes have been made there. 

The code changes I have made are mainly to add tank presets, calculations for horizontal tank geometry, custom tank sizes, and new sensors. In the past you would have had only the tank level sensor that displays inches, and it was up to you to create the proper template sensors to display percentage or gallons. No longer!

This custom Mopeka integration will override the native HA integration while keeping any preconfigured Mopeka devices intact. You will have to reconfigure your existing Mopeka devices to use the new tank presets and show the updated tank sensors.

## AI Disclaimer

Was this vibecoded? Yup!

I'm not a developer, but I am an IT Systems Engineer, so I have a good grasp on what I'm doing. The heavy lifting was done with Github Copilot (Claude Opus/Sonnet) in VScode using the Home Assistant dev container environment. The research and verification however was done by me. 

All HA and HACS standards have been followed, and all coding tests passed. Real world sensor readings using the integration enhancements were conducted on my 40 lb vertical propane tank, 100 lb horizontal propane tank, and my 330 gallon IBC tote (fresh water). The readings matched the Mopka app so well that I deemed this viable to share with the rest of the world. 

I 100% welcome others to improve upon this work. Find any mistakes I made, make things more efficient, or add additional tank presets. Maybe some day we can get these changes merged into the HA core integration!

## Features

- 🛢️ Tank presets for horizontal and vertical style propane tanks in gal/lbs (US standard sizes only)
- 🚰 Standard IBC tote presets for 275 gallon and 330 gallon sizes (available for all non-propane medium types)
- 📏 Option to define your own custom tank height in millimeters, and tank volume in gallons
- 📡 Automatic detection of top mount sensor models (TD40 and TD200) for correct sensor measurements (top mount sensors read through the air instead of liquid mediums)
- 🧭 Updated config flow menu for tank configuration based on medium type selection and device detection (top mount sensors)
- 🧮 Added background calculations to better handle horizontal propane tank geometry (hemisphere endcaps)
- 📊 Added two sensors for tank fill (percentage), and tank volume (gallons)
- 📊 Added two diagnostic sensors for Medium type (currently configured medium), and Tank preset (currently configured tank preset)

## Screenshots

### Sensors

<img src="images/screenshots/sensors.png" alt="Sensors view" width="75%" />

### Propane Presets

<img src="images/screenshots/propane_presets.png" alt="Propane presets" width="75%" />

### IBC Presets

<img src="images/screenshots/ibc_presets.png" alt="IBC presets" width="75%" />

### Custom Tanks

<img src="images/screenshots/custom%20tanks.png" alt="Custom tanks" width="75%" />

## A word on tank Presets

I've taken the 20 lb, 30 lb, and 40 lb vertical tank measurements from the Mopeka ESPHome component, as I believe they may have pulled them from the official Mopeka app. The rest of the tank measurements were obtained from extension Google searching (both manual and assisted by Gemini AI). I narrowed my research down to only US standard propane tank sizes since that's what I use on our bus. I'll eventually bring over the remaining 6Kg, 11Kg, and 14Kg Euro tank sizes from ESPHome. Feel free to submit a PR here for additional tank presets that you think would be valuable.


## Horizontal Tank Geometry

For horizontal propane presets, tank fill is calculated with non-linear geometry from the integration code in `custom_components/mopeka/sensor.py`.

The key formula uses the circular segment area of a horizontal cylinder cross-section:

$$
A(h) = r^2 \cdot \arccos\left(\frac{r-h}{r}\right) - (r-h) \cdot \sqrt{2rh-h^2}
$$

where:

- $h$ is measured liquid height in mm
- $r = \frac{\text{diameter}}{2}$
- normalized fraction is:

$$
f(h) = \frac{A(h)}{\pi r^2}
$$

The integration then adjusts for the configured empty offset (`empty_mm`) and computes fill percentage as:

$$
\mathrm{fill\_pct} = \frac{f(h_{reading}) - f(h_{empty})}{1 - f(h_{empty})} \times 100
$$

### Worked example (500 gal horizontal preset)

Using preset values from the integration:

- `empty_mm = 38.1`
- `full_mm (diameter) = 939.8`
- sample reading `h_reading = 469.9`

Computed values:

- $f(h_{empty}) = 0.01369$
- $f(h_{reading}) = 0.5$
- Fill percentage = 49.31%

If total configured capacity is 500 gal, then tank volume is:

$$
\mathrm{volume} = 0.4931 \times 500 = 246.53\,\mathrm{gal}
$$

### Why this matters (especially with hemispherical endcaps)

Horizontal tanks are not linear: a 10 mm change near the bottom does not represent the same volume change as 10 mm near the middle. A simple linear height-to-percent conversion would over/under-estimate fuel at different fill levels.

Many horizontal propane tanks also have rounded/hemispherical endcaps, which further separate true volume from a naive linear model. This integration improves practical accuracy by using non-linear cylindrical geometry for fill percentage and then applying the configured tank capacity for final gallons.


## Installation (HACS)

1. Open HACS in Home Assistant.
2. Go to Integrations.
3. Open the three-dot menu and select Custom repositories.
4. Add `https://github.com/bb12489/mopeka-enhanced` as category `Integration`.
5. Search for `Mopeka Enhanced` in HACS and install it.
6. Restart Home Assistant.

After restart, add or reconfigure your Mopeka devices from Settings -> Devices & Services.

## Acknowledgment

This custom component builds on the original Mopeka integration from Home Assistant Core.
Credit to the original upstream maintainer and codeowner, `@bdraco`, for the core integration foundation.

## Development

The integration code lives in `custom_components/mopeka`.

## License

This project is released under the Apache 2.0 license. See `LICENSE`.
