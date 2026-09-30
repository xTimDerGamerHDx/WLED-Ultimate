#!/usr/bin/env python3
from pathlib import Path
import sys

if len(sys.argv) != 2:
    raise SystemExit("usage: apply_mm_ultimate.py <wled-source-dir>")

source = Path(sys.argv[1])
usermods_list = source / "wled00" / "usermods_list.cpp"
ultimate_header = source / "usermods" / "WLED_Ultimate" / "usermod_wled_ultimate.h"
ui_v2_header = source / "usermods" / "WLED_Ultimate" / "ultimate_ui_v2.h"

if not usermods_list.exists():
    raise SystemExit(f"missing {usermods_list}")
if not ultimate_header.exists():
    raise SystemExit(f"missing {ultimate_header}")
if not ui_v2_header.exists():
    raise SystemExit(f"missing {ui_v2_header}")

# Wire the standalone Ultimate Audio Particle FX file into the MM control layer.
# Keeping this transformation in the overlay helper avoids patching upstream MM
# files and makes the integration deterministic for every MM target.
uh = ultimate_header.read_text(encoding="utf-8")
if '#include "ultimate_audio_fx.h"' not in uh:
    marker = '#include "wled.h"\n'
    if marker not in uh:
        raise SystemExit("unable to locate Ultimate wled.h include")
    uh = uh.replace(marker, marker + '#include "ultimate_audio_fx.h"\n', 1)

# Ultimate UI v2 is an additional page. The existing /ultimate page remains
# untouched as a fallback and the stock WLED UI continues to live at /.
if '#include "ultimate_ui_v2.h"' not in uh:
    marker = '#include "wled.h"\n'
    if marker not in uh:
        raise SystemExit("unable to locate Ultimate UI v2 include marker")
    uh = uh.replace(marker, marker + '#include "ultimate_ui_v2.h"\n', 1)

master_hook = '''#ifdef USERMOD_AUDIOREACTIVE
      ultimateParticleFxMaster = particleFx;
      ultimateAudioParticleFxMaster = audioParticleFx;
#endif
'''
if "ultimateAudioParticleFxMaster = audioParticleFx" not in uh:
    marker = "    void applyRuntimeSettings() {\n      applyAudioMasters();\n"
    if marker not in uh:
        raise SystemExit("unable to locate applyRuntimeSettings() hook")
    uh = uh.replace(marker, marker + master_hook, 1)

if "registerWLEDUltimateAudioFx();" not in uh:
    marker = "      applyRuntimeSettings();\n      server.on(\"/ultimate\""
    if marker not in uh:
        raise SystemExit("unable to locate Ultimate setup registration hook")
    replacement = "      applyRuntimeSettings();\n#ifdef USERMOD_AUDIOREACTIVE\n      registerWLEDUltimateAudioFx();\n#endif\n      server.on(\"/ultimate\""
    uh = uh.replace(marker, replacement, 1)

if 'server.on("/ultimate-v2"' not in uh:
    marker = '      server.on("/ultimate", HTTP_GET, [](AsyncWebServerRequest *request) {\n'
    if marker not in uh:
        raise SystemExit("unable to locate Ultimate v1 route")
    route = '''      server.on("/ultimate-v2", HTTP_GET, [](AsyncWebServerRequest *request) {
        request->send_P(200, "text/html", WLED_ULTIMATE_V2_PAGE);
      });
'''
    uh = uh.replace(marker, route + marker, 1)

if 'Ultimate UI v2' not in uh:
    marker = '      page.add(F("/ultimate"));\n'
    if marker in uh:
        info = '''      JsonArray pageV2 = user.createNestedArray("Ultimate UI v2");
      pageV2.add(F("/ultimate-v2"));
'''
        uh = uh.replace(marker, marker + info, 1)

ultimate_header.write_text(uh, encoding="utf-8")

text = usermods_list.read_text(encoding="utf-8")

include_block = '''\n#ifdef USERMOD_WLED_ULTIMATE\n#include "../usermods/WLED_Ultimate/usermod_wled_ultimate.h"\n#endif\n\n'''
register_block = '''\n#ifdef USERMOD_WLED_ULTIMATE\n  usermods.add(new WLEDUltimateUsermod("WLED Ultimate", true));\n#endif\n'''

# Include Ultimate after normal MM usermod headers so AudioReactive's internal
# state and FFT data are visible in the same translation unit.
if "usermod_wled_ultimate.h" not in text:
    marker = "\nvoid registerUsermods()\n"
    if marker not in text:
        raise SystemExit("unable to locate registerUsermods() include boundary")
    text = text.replace(marker, include_block + "void registerUsermods()\n", 1)

# Register Ultimate last so subsystem usermods load their persisted settings first.
if "new WLEDUltimateUsermod" not in text:
    end = text.rfind("\n}\n")
    if end < 0:
        raise SystemExit("unable to locate final registerUsermods() brace")
    text = text[:end] + register_block + text[end:]

usermods_list.write_text(text, encoding="utf-8")
print("WLED Ultimate MM control layer + Audio Particle FX + UI v2 registered")
