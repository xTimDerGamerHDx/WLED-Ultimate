#!/usr/bin/env python3
from pathlib import Path
import sys

if len(sys.argv) != 2:
    raise SystemExit("usage: apply_platform_v3.py <wled-source-dir>")

source = Path(sys.argv[1])
repo_root = Path(__file__).resolve().parents[1]
platform_source = repo_root / "overlay" / "mm" / "usermods" / "WLED_Ultimate" / "ultimate_platform_v3.h"
extra_source = repo_root / "overlay" / "mm" / "usermods" / "WLED_Ultimate" / "ultimate_platform_v3_extra.h"

if not platform_source.exists():
    raise SystemExit(f"missing {platform_source}")
if not extra_source.exists():
    raise SystemExit(f"missing {extra_source}")

def wire_ui(ui: Path):
    if not ui.exists():
        raise SystemExit(f"missing {ui}")
    text = ui.read_text(encoding="utf-8")
    text = text.replace('<title>WLED Ultimate UI v2.1</title>', '<title>WLED Ultimate UI v3</title>')
    text = text.replace('Modern UI v2.1 · Live', 'Ultimate Platform v3')
    text = text.replace('WLED Ultimate UI v2.1</div>', 'WLED Ultimate Platform v3</div>')
    text = text.replace('Ultimate UI v2.1', 'Ultimate Platform v3')
    if '/ultimate-platform-v3.js' not in text:
        marker = '<script src="/ultimate-audio-controls-v21.js"></script>'
        if marker not in text:
            raise SystemExit("unable to locate audio controls script tag")
        text = text.replace(marker, marker + '\n<script src="/ultimate-platform-v3.js"></script>', 1)
    if '/ultimate-platform-v3-extra.js' not in text:
        text = text.replace('<script src="/ultimate-platform-v3.js"></script>', '<script src="/ultimate-platform-v3.js"></script>\n<script src="/ultimate-platform-v3-extra.js"></script>', 1)
    if 'rel="manifest"' not in text:
        text = text.replace('</head>', '<link rel="manifest" href="/ultimate-manifest.json">\n</head>', 1)
    ui.write_text(text, encoding="utf-8")

def add_common_routes(u: str) -> str:
    if 'server.on("/ultimate-platform-v3.js"' in u:
        return u
    marker = '      initDone = true;\n'
    if marker not in u:
        raise SystemExit("unable to locate Ultimate v3 route marker")
    routes = '''      server.on("/ultimate-platform-v3.js", HTTP_GET, [](AsyncWebServerRequest *request) {
        AsyncWebServerResponse *response = request->beginResponse_P(200, "application/javascript", WLED_ULTIMATE_PLATFORM_V3_JS);
        response->addHeader("Cache-Control", "no-cache");
        request->send(response);
      });
      server.on("/ultimate-platform-v3-extra.js", HTTP_GET, [](AsyncWebServerRequest *request) {
        request->send_P(200, "application/javascript", WLED_ULTIMATE_PLATFORM_V3_EXTRA_JS);
      });
      server.on("/ultimate-manifest.json", HTTP_GET, [](AsyncWebServerRequest *request) {
        request->send_P(200, "application/manifest+json", WLED_ULTIMATE_MANIFEST_V3);
      });
      server.on("/ultimate-sw.js", HTTP_GET, [](AsyncWebServerRequest *request) {
        AsyncWebServerResponse *response = request->beginResponse_P(200, "application/javascript", WLED_ULTIMATE_SW_V3);
        response->addHeader("Cache-Control", "no-cache");
        response->addHeader("Service-Worker-Allowed", "/");
        request->send(response);
      });
'''
    return u.replace(marker, routes + marker, 1)

def wire_mm():
    ultimate = source / "usermods" / "WLED_Ultimate" / "usermod_wled_ultimate.h"
    ui = source / "usermods" / "WLED_Ultimate" / "ultimate_ui_v2.h"
    target = source / "usermods" / "WLED_Ultimate" / "ultimate_platform_v3.h"
    extra_target = source / "usermods" / "WLED_Ultimate" / "ultimate_platform_v3_extra.h"
    if not ultimate.exists():
        raise SystemExit(f"missing {ultimate}")
    target.write_text(platform_source.read_text(encoding="utf-8"), encoding="utf-8")
    extra_target.write_text(extra_source.read_text(encoding="utf-8"), encoding="utf-8")
    wire_ui(ui)
    u = ultimate.read_text(encoding="utf-8")
    if '#include "ultimate_platform_v3.h"' not in u:
        marker = '#include "ultimate_audio_controls_v21.h"\n'
        if marker not in u:
            raise SystemExit("unable to locate MM platform include marker")
        u = u.replace(marker, marker + '#include "ultimate_platform_v3.h"\n#include "ultimate_platform_v3_extra.h"\n', 1)
    u = add_common_routes(u)
    u = u.replace('F("Control Layer v2.1")', 'F("Control Layer v3")')
    u = u.replace('createNestedArray("Ultimate UI v2.1")', 'createNestedArray("Ultimate Platform v3")')
    ultimate.write_text(u, encoding="utf-8")
    print("Ultimate Platform v3 wired for MoonModules")

def wire_17dev():
    ultimate = source / "usermods" / "WLED_Ultimate" / "usermod_wled_ultimate.cpp"
    ui = source / "usermods" / "WLED_Ultimate" / "ultimate_ui_v2.h"
    target = source / "usermods" / "WLED_Ultimate" / "ultimate_platform_v3.h"
    extra_target = source / "usermods" / "WLED_Ultimate" / "ultimate_platform_v3_extra.h"
    if not ultimate.exists():
        raise SystemExit(f"missing {ultimate}")
    target.write_text(platform_source.read_text(encoding="utf-8"), encoding="utf-8")
    extra_target.write_text(extra_source.read_text(encoding="utf-8"), encoding="utf-8")
    wire_ui(ui)
    u = ultimate.read_text(encoding="utf-8")
    if '#include "ultimate_platform_v3.h"' not in u:
        marker = '#include "ultimate_audio_controls_v21.h"\n'
        if marker not in u:
            raise SystemExit("unable to locate 17dev platform include marker")
        u = u.replace(marker, marker + '#include "ultimate_platform_v3.h"\n#include "ultimate_platform_v3_extra.h"\n', 1)
    u = add_common_routes(u)
    u = u.replace('F("17dev Control Layer v2.1")', 'F("17dev Control Layer v3")')
    u = u.replace('createNestedArray("Ultimate UI v2.1")', 'createNestedArray("Ultimate Platform v3")')
    ultimate.write_text(u, encoding="utf-8")
    print("Ultimate Platform v3 wired for WLED 17dev")

if (source / "usermods" / "WLED_Ultimate" / "usermod_wled_ultimate.cpp").exists():
    wire_17dev()
elif (source / "usermods" / "WLED_Ultimate" / "usermod_wled_ultimate.h").exists():
    wire_mm()
else:
    raise SystemExit("unable to detect WLED Ultimate source tree")
