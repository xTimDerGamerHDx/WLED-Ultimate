# Gledopto Elite 4D-EXMU / GL-C-618WL

Dedicated WLED Ultimate-MM target:

```text
ultimate_gledopto_gl_c_618wl
```

This target is intended for the **Gledopto Elite 4D-EXMU Advanced WLED Controller, model GL-C-618WL**.

## WLED Ultimate features

- MoonModules/WLED-MM `mdev` base
- AudioReactive / sound-reactive effects
- Particle / PS effects provided by the MM base
- Ethernet support
- Wi-Fi fallback through WLED
- MQTT / Home Assistant support inherited from WLED-MM
- DDP / E1.31 / Art-Net support inherited from WLED-MM where enabled/supported
- OTA support inherited from WLED-MM

## Hardware pinout

| Function | GPIO | Notes |
|---|---:|---|
| LED output 1 | 16 | Digital LED data |
| LED output 2 | 12 | Digital LED data |
| LED output 3 | 4 | Digital LED data |
| LED output 4 | 2 | Digital LED data |
| Extra GPIO | 13 | Exposed auxiliary GPIO |
| Function button | 17 | Firmware default via `BTNPIN=17` |
| Relay | 18 | Active-low / inverted, firmware default |
| PDM microphone DATA / SD | 32 | Generic PDM microphone |
| PDM microphone WS / CLK | 15 | Generic PDM microphone |

## Ethernet

The controller uses the WLED **Gledopto Series with Ethernet** profile.

WLED board type:

```text
WLED_ETH_GLEDOPTO = 13
```

The WLED/MM Ethernet table defines the profile as:

| Setting | Value |
|---|---|
| PHY | LAN8720 |
| PHY address | 1 |
| PHY power | GPIO5 |
| MDC | GPIO23 |
| MDIO | GPIO33 |
| Clock | GPIO0 input |

The WLED Ultimate build sets:

```text
WLED_ETH_DEFAULT=13
```

so a fresh configuration starts with the correct Gledopto Ethernet hardware profile.

## Audio configuration

The GL-C-618WL has a built-in Generic PDM microphone. In the AudioReactive settings use:

```text
Microphone type: Generic PDM
SD / DATA: GPIO32
WS / CLK: GPIO15
```

Audio sensitivity/gain and squelch remain runtime settings because the correct values depend on the enclosure, placement and desired response.

## LED outputs

The firmware knows the board target, but LED lengths are deliberately not hard-coded. The number and type of LEDs connected to each output are installation-specific.

Configure up to four digital LED buses with these data pins:

```text
Output 1: GPIO16
Output 2: GPIO12
Output 3: GPIO4
Output 4: GPIO2
```

Set the LED type, LED count, color order, start index and power limit for the actual strips connected to the controller.

## Relay and button defaults

The dedicated target compiles with:

```text
BTNPIN=17
RLYPIN=18
RLYMDE=0
```

This gives a fresh WLED configuration the controller's hardware button and active-low/inverted relay pin as defaults.

## Build locally

```bash
git clone https://github.com/MoonModules/WLED-MM.git --branch mdev source
cp config/platformio_override.mm.ini source/platformio_override.ini
cd source
pio run -e ultimate_gledopto_gl_c_618wl
```

## Important upgrade note

WLED normally preserves `cfg.json` across OTA upgrades. Existing hardware settings can therefore override compile-time defaults. If this controller was previously configured with another firmware/build, verify Ethernet, LED buses, relay, button and microphone settings after the first WLED Ultimate flash.

## Electrical safety

Use the controller only within its documented input/output limits. Match the controller supply voltage to the LED strip voltage and size wiring, fusing and power injection for the actual LED load.
