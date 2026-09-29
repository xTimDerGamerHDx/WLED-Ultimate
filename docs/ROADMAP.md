# WLED Ultimate roadmap

## Phase 1 - build foundation

- [x] Separate MM and upstream-development build channels
- [x] ESP32 Ethernet builds
- [x] ESP32-S3 PSRAM builds
- [x] GitHub Actions binary artifacts
- [x] Tag-driven GitHub releases
- [ ] Verify all initial build targets in CI
- [ ] Add checksums and build metadata

## Phase 2 - WLED Ultimate integration

- [ ] Inventory MM-only sound-reactive changes not already present upstream
- [ ] Inventory Particle/PS effects and dependencies
- [ ] Port selected MM audio improvements onto the current WLED main branch
- [ ] Port selected MM Particle/PS improvements onto the current WLED main branch
- [ ] Resolve UI/config differences without replacing upstream settings blindly
- [ ] Add WLED Ultimate version/build information to the Info page

## Phase 3 - networking

- [ ] Verify Ethernet board profiles inherited from upstream/MM
- [ ] Verify Ethernet + Wi-Fi fallback behavior
- [ ] Test MQTT/Home Assistant over Ethernet
- [ ] Test DDP, E1.31 and Art-Net on Ethernet builds
- [ ] Add ESP32-S3 Ethernet targets when upstream board support is confirmed

## Phase 4 - audio

- [ ] I2S microphones
- [ ] INMP441 preset
- [ ] ICS-43434/ICS-43432 preset
- [ ] line-in preset
- [ ] UDP audio sync
- [ ] FFT/beat/peak validation
- [ ] AudioReactive 1D effects
- [ ] AudioReactive 2D effects
- [ ] Audio + Particle effects

## Phase 5 - performance

- [ ] PSRAM-aware buffers on ESP32-S3
- [ ] large strip stress test
- [ ] large 2D matrix stress test
- [ ] HUB75 test build
- [ ] memory telemetry
- [ ] watchdog/recovery testing

## Phase 6 - release

- [ ] Web installer manifest
- [ ] OTA binary naming
- [ ] stable/beta/dev channels
- [ ] changelog generation
- [ ] SHA-256 checksums
- [ ] signed/reproducible release metadata where practical

## Porting rule

WLED Ultimate must not blindly copy one upstream tree over another. MM-specific changes are ported as reviewable overlays/patches so that conflicts with future WLED versions remain visible and maintainable.
