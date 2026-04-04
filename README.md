# Mopeka Enhanced

Enhanced custom component version of Home Assistant's native Mopeka integration.

This repository packages the latest Mopeka integration enhancements so you can install updates through HACS without waiting for Home Assistant Core release cycles.

## Features

- Automatic top-mount sensor handling (TD40 and TD200)
- Medium-aware setup flow for better tank model selection
- Expanded tank presets including IBC tote options
- Calibrated level/volume behavior improvements from current enhancement branch

## Installation (HACS)

1. Open HACS in Home Assistant.
2. Go to Integrations.
3. Open the three-dot menu and select Custom repositories.
4. Add `https://github.com/bb12489/mopeka-enhanced` as category `Integration`.
5. Search for `Mopeka Enhanced` in HACS and install it.
6. Restart Home Assistant.

After restart, add or reconfigure your Mopeka devices from Settings -> Devices & Services.

## Notes

- This custom component uses the `mopeka` domain and is intended to override the built-in core integration implementation.
- Keep only one active implementation for the domain to avoid confusion during troubleshooting.

## Release Checklist (HACS)

Before creating a release, verify:

1. `custom_components/mopeka/manifest.json` has an updated `version` value (for example, `0.1.1`).
2. Create a matching git tag with `v` prefix (for example, `v0.1.1`).
3. Push the tag to GitHub.
4. Confirm the GitHub release workflow runs for that tag.
5. Confirm HACS shows the new version after the release is published.

Quick check: manifest version and tag should match except for the `v` prefix.
Example: manifest `0.1.1` <-> tag `v0.1.1`.

## Development

The integration code lives in `custom_components/mopeka`.

## License

This project is released under the Apache 2.0 license. See `LICENSE`.
