#!/usr/bin/env python3
from pathlib import Path
import sys

if len(sys.argv) != 2:
    raise SystemExit("usage: apply_wled17_ultimate.py <wled-source-dir>")

source = Path(sys.argv[1])
repo_root = Path(__file__).resolve().parents[1]
audio = source / "usermods" / "audioreactive" / "audio_reactive.cpp"
ultimate = source / "usermods" / "WLED_Ultimate" / "usermod_wled_ultimate.cpp"
ui_v2_source = repo_root / "overlay" / "mm" / "usermods" / "WLED_Ultimate" / "ultimate_ui_v2.h"
ui_v2_target = source / "usermods" / "WLED_Ultimate" / "ultimate_ui_v2.h"
ui_v21_source = repo_root / "overlay" / "mm" / "usermods" / "WLED_Ultimate" / "ultimate_ui_v21_patch.h"
ui_v21_target = source / "usermods" / "WLED_Ultimate" / "ultimate_ui_v21_patch.h"

if not audio.exists():
    raise SystemExit(f"missing {audio}")
if not ultimate.exists():
    raise SystemExit(f"missing {ultimate}")
if not ui_v2_source.exists():
    raise SystemExit(f"missing shared Ultimate UI v2 header {ui_v2_source}")
if not ui_v21_source.exists():
    raise SystemExit(f"missing shared Ultimate UI v2.1 patch {ui_v21_source}")

# UI v2.1 is shared by MM and 17dev so both channels expose the same frontend.
ui_v2_target.parent.mkdir(parents=True, exist_ok=True)
ui_text = ui_v2_source.read_text(encoding="utf-8")
ui_text = ui_text.replace('<title>WLED Ultimate UI v2</title>', '<title>WLED Ultimate UI v2.1</title>')
ui_text = ui_text.replace('Modern UI v2 · Preview', 'Modern UI v2.1 · Live')
ui_text = ui_text.replace('WLED Ultimate UI v2</div>', 'WLED Ultimate UI v2.1</div>')
ui_text = ui_text.replace('href="/ultimate">Ultimate v1', 'href="/ultimate-v1">Ultimate v1')
ui_text = ui_text.replace('V2 ist zusätzlich installiert. Nichts wird ersetzt.', 'V2.1 ist die Standard-Ultimate-Oberfläche. Die alte UI bleibt unter /ultimate-v1 erhalten.')
ui_text = ui_text.replace('Ultimate UI v2 Preview', 'Ultimate UI v2.1')
if '/ultimate-v21.js' not in ui_text:
    ui_text = ui_text.replace('</body>', '<script src="/ultimate-v21.js"></script>\n</body>', 1)
ui_v2_target.write_text(ui_text, encoding="utf-8")
ui_v21_target.write_text(ui_v21_source.read_text(encoding="utf-8"), encoding="utf-8")

# Export a minimal stable bridge from the AudioReactive translation unit.
audio_text = audio.read_text(encoding="utf-8")
bridge_tag = "WLED_ULTIMATE_AUDIO_BRIDGE"
if bridge_tag not in audio_text:
    audio_text += r'''

// WLED_ULTIMATE_AUDIO_BRIDGE
// Injected at build time by WLED Ultimate. Keeps upstream AudioReactive source
// untouched in the repository while exposing only the master controls Ultimate needs.
extern "C" void wledUltimate17SetAudioProcessing(bool enabled) {
  disableSoundProcessing = !enabled;
}

extern "C" void wledUltimate17SetAudioSync(bool enabled) {
  static uint8_t rememberedAudioSyncMode = 2; // receive is the safe fallback
  if (!enabled) {
    if (audioSyncEnabled != 0) rememberedAudioSyncMode = audioSyncEnabled;
    audioSyncEnabled = 0;
  } else if (audioSyncEnabled == 0) {
    audioSyncEnabled = rememberedAudioSyncMode ? rememberedAudioSyncMode : 2;
  } else {
    rememberedAudioSyncMode = audioSyncEnabled;
  }
}
'''
    audio.write_text(audio_text, encoding="utf-8")

u = ultimate.read_text(encoding="utf-8")

# WLED 17dev exposes inter-usermod access as a static UsermodManager API.
u = u.replace("usermods.getUMData(", "UsermodManager::getUMData(")

if "wledUltimate17SetAudioProcessing" not in u:
    marker = '#include "wled.h"\n'
    decl = '''#include "wled.h"\n\nextern "C" void wledUltimate17SetAudioProcessing(bool enabled);\nextern "C" void wledUltimate17SetAudioSync(bool enabled);\n'''
    if marker not in u:
        raise SystemExit("unable to locate 17dev Ultimate include marker")
    u = u.replace(marker, decl, 1)

if '#include "ultimate_ui_v2.h"' not in u:
    marker = '#include "wled.h"\n'
    if marker not in u:
        raise SystemExit("unable to locate 17dev UI v2 include marker")
    u = u.replace(marker, marker + '#include "ultimate_ui_v2.h"\n', 1)
if '#include "ultimate_ui_v21_patch.h"' not in u:
    marker = '#include "wled.h"\n'
    u = u.replace(marker, marker + '#include "ultimate_ui_v21_patch.h"\n', 1)

# Build real 16-band telemetry from the same AudioReactive shared data used by
# the Ultimate audio effects.
if 'ultimate17AudioTelemetryJson' not in u:
    marker = 'static void mode_ultimate17_audio_particles() {\n'
    if marker not in u:
        raise SystemExit("unable to locate 17dev audio telemetry insertion marker")
    telemetry = r'''static String ultimate17AudioTelemetryJson() {
  float volume = 0.0f;
  uint8_t *fft = nullptr;
  bool peak = false;
  if (!ultimate17GetAudio(volume, fft, peak) || fft == nullptr) {
    return F("{\"available\":false,\"source\":\"AudioReactive unavailable\",\"processing\":false,\"peak\":false,\"level\":0,\"bass\":0,\"mids\":0,\"treble\":0,\"fft\":[]}");
  }
  uint8_t level = 0;
  for (uint8_t i = 0; i < 16; i++) if (fft[i] > level) level = fft[i];
  const uint8_t bass = max(fft[0], fft[1]);
  const uint8_t mids = max(fft[5], fft[7]);
  const uint8_t treble = max(fft[12], fft[15]);
  String json;
  json.reserve(320);
  json = F("{\"available\":true,\"source\":\"WLED 17 AudioReactive\",\"processing\":");
  json += ultimate17AudioEngineMaster ? F("true") : F("false");
  json += F(",\"peak\":"); json += peak ? F("true") : F("false");
  json += F(",\"volume\":"); json += String(volume, 1);
  json += F(",\"level\":"); json += level;
  json += F(",\"bass\":"); json += bass;
  json += F(",\"mids\":"); json += mids;
  json += F(",\"treble\":"); json += treble;
  json += F(",\"fft\":[");
  for (uint8_t i = 0; i < 16; i++) {
    if (i) json += ',';
    json += fft[i];
  }
  json += F("]}");
  return json;
}

'''
    u = u.replace(marker, telemetry + marker, 1)

# Make UI v2.1 the normal Ultimate route, preserve old page at /ultimate-v1.
legacy_route = '''      server.on("/ultimate", HTTP_GET, [](AsyncWebServerRequest *request) {
        request->send_P(200, "text/html", WLED_ULTIMATE_PAGE);
      });
'''
if 'server.on("/ultimate-v1"' not in u:
    if legacy_route not in u:
        raise SystemExit("unable to locate 17dev Ultimate v1 route")
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
    u = u.replace(legacy_route, routes, 1)

# Serve the v2.1 enhancement script and real audio telemetry endpoint.
if 'server.on("/ultimate-v21.js"' not in u:
    marker = '      initDone = true;\n'
    routes = '''      server.on("/ultimate-v21.js", HTTP_GET, [](AsyncWebServerRequest *request) {
        request->send_P(200, "application/javascript", WLED_ULTIMATE_V21_JS);
      });
      server.on("/ultimate/api/audio", HTTP_GET, [](AsyncWebServerRequest *request) {
        request->send(200, "application/json", ultimate17AudioTelemetryJson());
      });
'''
    if marker not in u:
        raise SystemExit("unable to locate 17dev route insertion marker")
    u = u.replace(marker, routes + marker, 1)

# Make JSON info explicitly list both interfaces and the 2.1 control layer.
u = u.replace('F("17dev Control Layer v1")', 'F("17dev Control Layer v2.1")')
u = u.replace('createNestedArray("Ultimate UI")', 'createNestedArray("Ultimate UI v1")', 1)
u = u.replace('p.add(F("/ultimate"));', 'p.add(F("/ultimate-v1"));', 1)
if 'createNestedArray("Ultimate UI v2")' not in u and 'createNestedArray("Ultimate UI v2.1")' not in u:
    marker = '      p.add(F("/ultimate-v1"));\n'
    if marker in u:
        info = '''      JsonArray p2 = user.createNestedArray("Ultimate UI v2.1");
      p2.add(F("/ultimate"));
'''
        u = u.replace(marker, marker + info, 1)
else:
    u = u.replace('createNestedArray("Ultimate UI v2")', 'createNestedArray("Ultimate UI v2.1")')

# WLED 17dev no longer exposes the old doSerializeConfig global. Queue config
# writes from the JSON callback and perform serializeConfigToFS() later in loop().
if "saveConfigPending" not in u:
    marker = "    uint8_t highPerformanceFps = 60;\n"
    if marker not in u:
        raise SystemExit("unable to locate 17dev Ultimate member marker")
    u = u.replace(marker, marker + "    bool saveConfigPending = false;\n", 1)

u = u.replace("if (changed) doSerializeConfig = true;", "if (changed) saveConfigPending = true;")

if "lastMasterApply" not in u:
    marker = "    bool saveConfigPending = false;\n"
    if marker not in u:
        marker = "    uint8_t highPerformanceFps = 60;\n"
    u = u.replace(marker, marker + "    uint32_t lastMasterApply = 0;\n", 1)

if "wledUltimate17SetAudioProcessing(advancedAudioEngine);" not in u:
    marker = "    void applyRuntime() {\n"
    if marker not in u:
        raise SystemExit("unable to locate 17dev applyRuntime()")
    hook = "    void applyRuntime() {\n      wledUltimate17SetAudioProcessing(advancedAudioEngine);\n      wledUltimate17SetAudioSync(audioUdpSync);\n"
    u = u.replace(marker, hook, 1)

if "void loop() override" not in u:
    marker = "    void addToJsonInfo(JsonObject& root) override {\n"
    if marker not in u:
        raise SystemExit("unable to locate 17dev addToJsonInfo()")
    loop = '''    void loop() override {
      if (saveConfigPending) {
        saveConfigPending = false;
        serializeConfigToFS();
      }
      if (millis() - lastMasterApply >= 1000) {
        lastMasterApply = millis();
        wledUltimate17SetAudioProcessing(advancedAudioEngine);
        wledUltimate17SetAudioSync(audioUdpSync);
      }
    }

'''
    u = u.replace(marker, loop + marker, 1)
else:
    loop_marker = "    void loop() override {\n"
    if "saveConfigPending = false;\n        serializeConfigToFS();" not in u and loop_marker in u:
        u = u.replace(loop_marker, loop_marker + "      if (saveConfigPending) {\n        saveConfigPending = false;\n        serializeConfigToFS();\n      }\n", 1)

u = u.replace("serializeConfig();", "serializeConfigToFS();")
ultimate.write_text(u, encoding="utf-8")
print("WLED Ultimate 17dev bridge + live AudioReactive telemetry + UI v2.1 adapted")
