# WLED 17dev overlay

Files placed below this directory are copied on top of `wled/WLED:main` before PlatformIO builds the Ultimate-17dev channel.

This is where WLED-MM functionality will be ported in controlled pieces instead of replacing the WLED source tree wholesale.

Port order:

1. build/version integration
2. audio-reactive deltas not already upstream
3. Particle/PS effect deltas
4. UI/config additions required by those features
5. performance and PSRAM-specific improvements
6. Ethernet-specific fixes or presets

Every port should record its WLED-MM source commit or source file so future upstream updates can be reconciled cleanly.
