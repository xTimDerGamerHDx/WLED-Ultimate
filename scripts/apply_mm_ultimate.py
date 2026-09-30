#!/usr/bin/env python3
from pathlib import Path
import runpy
import sys

if len(sys.argv) != 2:
    raise SystemExit("usage: apply_mm_ultimate.py <wled-source-dir>")

source = Path(sys.argv[1])
usermods_list = source / "wled00" / "usermods_list.cpp"
ultimate_header = source / "usermods" / "WLED_Ultimate" / "usermod_wled_ultimate.h"
ui_v2_header = source / "usermods" / "WLED_Ultimate" / "ultimate_ui_v2.h"
ui_v21_header = source / "usermods" / "WLED_Ultimate" / "ultimate_ui_v21_patch.h"

if not usermods_list.exists():
    raise SystemExit(f"missing {usermods_list}")
if not ultimate_header.exists():
    raise SystemExit(f"missing {ultimate_header}")
if not ui_v2_header.exists():
    raise SystemExit(f"missing {ui_v2_header}")
if not ui_v21_header.exists():
    raise SystemExit(f"missing {ui_v21_header}")

# Wire the standalone Ultimate Audio Particle FX file into the MM control layer.
uh = ultimate_header.read_text(encoding="utf-8")
if '#include "ultimate_audio_fx.h"' not in uh:
    marker = '#include "wled.h"\n'
    if marker not in uh:
        raise SystemExit("unable to locate Ultimate wled.h include")
    uh = uh.replace(marker, marker + '#include "ultimate_audio_fx.h"\n', 1)

# Wire the shared modern frontend and the v2.1 enhancement bundle into every MM build.
if '#include "ultimate_ui_v2.h"' not in uh:
    marker = '#include "wled.h"\n'
    if marker not in uh:
        raise SystemExit("unable to locate Ultimate UI v2 include marker")
    uh = uh.replace(marker, marker + '#include "ultimate_ui_v2.h"\n', 1)
if '#include "ultimate_ui_v21_patch.h"' not in uh:
    marker = '#include "wled.h"\n'
    uh = uh.replace(marker, marker + '#include "ultimate_ui_v21_patch.h"\n', 1)

# Turn the shared v2 HTML into v2.1 and load the small enhancement script.
ui = ui_v2_header.read_text(encoding="utf-8")
ui = ui.replace('<title>WLED Ultimate UI v2</title>', '<title>WLED Ultimate UI v2.1</title>')
ui = ui.replace('Modern UI v2 · Preview', 'Modern UI v2.1 · Live')
ui = ui.replace('WLED Ultimate UI v2</div>', 'WLED Ultimate UI v2.1</div>')
ui = ui.replace('href="/ultimate">Ultimate v1', 'href="/ultimate-v1">Ultimate v1')
ui = ui.replace('V2 ist zusätzlich installiert. Nichts wird ersetzt.', 'V2.1 ist die Standard-Ultimate-Oberfläche. Die alte UI bleibt unter /ultimate-v1 erhalten.')
ui = ui.replace('Ultimate UI v2 Preview', 'Ultimate UI v2.1')
if '/ultimate-v21.js' not in ui:
    ui = ui.replace('</body>', '<script src="/ultimate-v21.js"></script>\n</body>', 1)
ui_v2_header.write_text(ui, encoding="utf-8")

# Live AudioReactive telemetry. These globals are visible because Ultimate is included
# after the normal MM usermod headers in the same translation unit.
if 'ultimateMmAudioTelemetryJson' not in uh:
    marker = 'class WLEDUltimateUsermod : public Usermod {\n'
    if marker not in uh:
        raise SystemExit("unable to locate MM Ultimate class")
    telemetry = r'''static String ultimateMmAudioTelemetryJson() {
#ifdef USERMOD_AUDIOREACTIVE
  uint8_t level = 0;
  for (uint8_t i = 0; i < 16; i++) if (fftResult[i] > level) level = fftResult[i];
  const uint8_t bass = max(fftResult[0], fftResult[1]);
  const uint8_t mids = max(fftResult[5], fftResult[7]);
  const uint8_t treble = max(fftResult[12], fftResult[15]);
  String json;
  json.reserve(300);
  json = F("{\"available\":true,\"source\":\"MM AudioReactive\",\"processing\":");
  json += disableSoundProcessing ? F("false") : F("true");
  json += F(",\"peak\":");
  json += samplePeak ? F("true") : F("false");
  json += F(",\"level\":"); json += level;
  json += F(",\"bass\":"); json += bass;
  json += F(",\"mids\":"); json += mids;
  json += F(",\"treble\":"); json += treble;
  json += F(",\"fft\":[");
  for (uint8_t i = 0; i < 16; i++) {
    if (i) json += ',';
    json += uint8_t(fftResult[i]);
  }
  json += F("]}");
  return json;
#else
  return F("{\"available\":false,\"source\":\"AudioReactive not compiled\",\"processing\":false,\"peak\":false,\"level\":0,\"bass\":0,\"mids\":0,\"treble\":0,\"fft\":[]}");
#endif
}

'''
    uh = uh.replace(marker, telemetry + marker, 1)

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

# Make UI v2.1 the normal Ultimate page, preserve v1 as fallback, retain v2 alias.
legacy_route = '''      server.on("/ultimate", HTTP_GET, [](AsyncWebServerRequest *request) {
        request->send_P(200, "text/html", WLED_ULTIMATE_PAGE);
      });
'''
if 'server.on("/ultimate-v1"' not in uh:
    if legacy_route not in uh:
        raise SystemExit("unable to locate Ultimate v1 route")
    routes = '''      server.on("/ultimate", HTTP_GET, [](AsyncWebServerRequest *request) {
        request->send_P(200, "text/html", WLED_ULTIMATE_V2_PAGE);
      });
      server.on("/ultimate-v1", HTTP_GET, [](AsyncWebServerRequest *request) {
        request->send_P(200, "text/html", WLED_ULTIMATE_PAGE);
      });
      server.on("/ultimate-v2", HTTP_GET, [](AsyncWebServerRequest *request) {
        request->send_P(200, "text/html", WLED_ULTIMATE_V2_PAGE);
      });
'''
    uh = uh.replace(legacy_route, routes, 1)

# Serve the v2.1 extension and real audio telemetry API.
if 'server.on("/ultimate-v21.js"' not in uh:
    marker = '      initDone = true;\n'
    routes = '''      server.on("/ultimate-v21.js", HTTP_GET, [](AsyncWebServerRequest *request) {
        request->send_P(200, "application/javascript", WLED_ULTIMATE_V21_JS);
      });
      server.on("/ultimate/api/audio", HTTP_GET, [](AsyncWebServerRequest *request) {
        request->send(200, "application/json", ultimateMmAudioTelemetryJson());
      });
'''
    if marker not in uh:
        raise SystemExit("unable to locate MM route insertion marker")
    uh = uh.replace(marker, routes + marker, 1)

# Make JSON info clearly advertise both interfaces and v2.1 control layer.
uh = uh.replace('F("Control Layer v1")', 'F("Control Layer v2.1")')
uh = uh.replace('createNestedArray("Ultimate UI")', 'createNestedArray("Ultimate UI v1")', 1)
uh = uh.replace('page.add(F("/ultimate"));', 'page.add(F("/ultimate-v1"));', 1)
if 'createNestedArray("Ultimate UI v2")' not in uh:
    marker = '      page.add(F("/ultimate-v1"));\n'
    if marker in uh:
        info = '''      JsonArray pageV2 = user.createNestedArray("Ultimate UI v2.1");
      pageV2.add(F("/ultimate"));
'''
        uh = uh.replace(marker, marker + info, 1)
else:
    uh = uh.replace('createNestedArray("Ultimate UI v2")', 'createNestedArray("Ultimate UI v2.1")')

ultimate_header.write_text(uh, encoding="utf-8")

text = usermods_list.read_text(encoding="utf-8")
include_block = '''\n#ifdef USERMOD_WLED_ULTIMATE\n#include "../usermods/WLED_Ultimate/usermod_wled_ultimate.h"\n#endif\n\n'''
register_block = '''\n#ifdef USERMOD_WLED_ULTIMATE\n  usermods.add(new WLEDUltimateUsermod("WLED Ultimate", true));\n#endif\n'''

if "usermod_wled_ultimate.h" not in text:
    marker = "\nvoid registerUsermods()\n"
    if marker not in text:
        raise SystemExit("unable to locate registerUsermods() include boundary")
    text = text.replace(marker, include_block + "void registerUsermods()\n", 1)

if "new WLEDUltimateUsermod" not in text:
    end = text.rfind("\n}\n")
    if end < 0:
        raise SystemExit("unable to locate final registerUsermods() brace")
    text = text[:end] + register_block + text[end:]

usermods_list.write_text(text, encoding="utf-8")
print("WLED Ultimate MM control layer + live AudioReactive telemetry + UI v2.1 registered")
runpy.run_path(str(Path(__file__).resolve().with_name("apply_audio_controls_v21.py")), run_name="__main__")
