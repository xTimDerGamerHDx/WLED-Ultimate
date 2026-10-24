# WLED Ultimate v3 Platform

Ultimate v3 is built on the validated v2.1 branch and keeps `/ultimate-v1` as a recovery UI.

## Modules

- Audio Lab: presets, auto calibration, adaptive gain, FFT EQ, beat/BPM/mood detection
- Studio: effect builder, scene generator, smart random, palette extraction, particle controls
- Shows: timeline, DJ mode and browser-runtime automation engine
- Multi-WLED: device manager, group control, state clone and sync delay profiles
- Diagnostics: self-test, performance profiles, LED test patterns, pixel locator and network tests
- Backup & Update: JSON backup/restore, OTA links, recovery paths and theme/kiosk mode
- Capability gates for PSRAM, Ethernet, audio, particles and optional board features

## Safety / platform limits

Features that require support below the usermod layer (true OTA A/B rollback, server-wide API authentication, multiple physical microphone channels, full 3D geometry rendering) are capability-gated instead of being simulated. The UI never claims they are active when the firmware does not expose the required capability.

## Compatibility

- MoonModules/WLED-MM
- WLED 17dev
- ESP32 and ESP32-S3 profiles from the existing 10-target build matrix
