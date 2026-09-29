# WLED Ultimate

WLED Ultimate is a custom firmware project that combines the current WLED development line with selected MoonModules/WLED-MM features, with a focus on sound-reactive effects, Particle/PS effects, Ethernet, ESP32-S3/PSRAM and large LED installations.

> Status: early development. Development builds are experimental and should be tested before production use.

## Build channels

### Ultimate-MM

Functional integration baseline based on `MoonModules/WLED-MM:mdev`. This channel is intended to provide the MM audio/effect stack and Ethernet-capable ESP32 builds immediately while WLED Ultimate integration work continues.

Targets:

- ESP32 4 MB
- ESP32 4 MB + Ethernet
- **Gledopto Elite 4D-EXMU / GL-C-618WL** (dedicated Ethernet + board defaults)
- ESP32 16 MB + Ethernet
- ESP32-S3 8 MB + OPI PSRAM
- ESP32-S3 16 MB + PSRAM/HUB75

Board-specific documentation:

- [`docs/boards/gledopto-gl-c-618wl.md`](docs/boards/gledopto-gl-c-618wl.md)

### Ultimate-17dev

Experimental channel based on `wled/WLED:main`. This repository treats current upstream `main` as the development base toward the next WLED generation rather than labeling it as a stable WLED 17 release.

Targets:

- ESP32 AudioReactive V4
- ESP32 Ethernet AudioReactive V4
- ESP32-S3 8 MB OPI
- ESP32-S3 16 MB OPI

## Ultimate goals

- WLED upstream core
- WLED-MM sound-reactive/audio enhancements
- Particle / PS effects
- Ethernet + Wi-Fi fallback
- ESP32-S3 + PSRAM optimized builds
- dedicated controller profiles
- 1D and 2D effects
- HUB75-capable build variants
- MQTT / Home Assistant
- DDP / E1.31 / Art-Net where supported by the selected upstream
- OTA-friendly release binaries
- automated GitHub Actions builds

## Repository layout

```text
.github/workflows/      CI firmware builds
config/                 PlatformIO overrides for each build channel
docs/                   architecture, board and porting notes
overlay/                 WLED Ultimate source overlays/patches
scripts/                 sync/merge/validation helpers
```

## Build locally

The CI workflow checks out the selected upstream source and injects the appropriate WLED Ultimate PlatformIO override. That keeps this repository small and makes upstream synchronization auditable.

### Ultimate-MM

```bash
git clone https://github.com/MoonModules/WLED-MM.git --branch mdev source
cp config/platformio_override.mm.ini source/platformio_override.ini
cd source
pio run -e ultimate_esp32_4mb
```

Gledopto GL-C-618WL:

```bash
pio run -e ultimate_gledopto_gl_c_618wl
```

### Ultimate-17dev

```bash
git clone https://github.com/wled/WLED.git --branch main source
cp config/platformio_override.wled17.ini source/platformio_override.ini
cd source
pio run -e ultimate_wled17_esp32_eth
```

## Upstream projects

WLED Ultimate is derived from and tracks:

- WLED: https://github.com/wled/WLED
- WLED-MM: https://github.com/MoonModules/WLED-MM

Both upstream projects are licensed under EUPL-1.2. WLED Ultimate will preserve upstream attribution and licensing for all derived code.

## Safety

Always verify LED voltage, power injection, fuse sizing, grounding and controller pin assignments before connecting large LED installations. Firmware cannot protect against incorrectly sized wiring or power supplies.
