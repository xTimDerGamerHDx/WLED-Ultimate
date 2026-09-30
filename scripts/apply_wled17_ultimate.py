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

if not audio.exists():
    raise SystemExit(f"missing {audio}")
if not ultimate.exists():
    raise SystemExit(f"missing {ultimate}")
if not ui_v2_source.exists():
    raise SystemExit(f"missing shared Ultimate UI v2 header {ui_v2_source}")

# UI v2 is shared by MM and 17dev so both channels expose the exact same frontend.
# It is copied into the active WLED source tree at build time; the original v1 UI
# remains inside each channel-specific usermod.
ui_v2_target.parent.mkdir(parents=True, exist_ok=True)
ui_v2_target.write_text(ui_v2_source.read_text(encoding="utf-8"), encoding="utf-8")

# Export a minimal stable bridge from the AudioReactive translation unit.
# The upstream variables are file-static, so the bridge must live in this file.
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

if 'server.on("/ultimate-v2"' not in u:
    marker = '      server.on("/ultimate", HTTP_GET, [](AsyncWebServerRequest *request) {\n'
    if marker not in u:
        raise SystemExit("unable to locate 17dev Ultimate v1 route")
    route = '''      server.on("/ultimate-v2", HTTP_GET, [](AsyncWebServerRequest *request) {
        request->send_P(200, "text/html", WLED_ULTIMATE_V2_PAGE);
      });
'''
    u = u.replace(marker, route + marker, 1)

if 'Ultimate UI v2' not in u:
    marker = '      p.add(F("/ultimate"));\n'
    if marker in u:
        info = '''      JsonArray p2 = user.createNestedArray("Ultimate UI v2");
      p2.add(F("/ultimate-v2"));
'''
        u = u.replace(marker, marker + info, 1)

# WLED 17dev no longer exposes the old doSerializeConfig global. Queue config
# writes from the JSON callback and perform serializeConfigToFS() later in loop(),
# avoiding filesystem writes from the network callback.
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
    # Keep the patch idempotent if a future overlay already contains loop().
    loop_marker = "    void loop() override {\n"
    if "saveConfigPending = false;\n        serializeConfigToFS();" not in u and loop_marker in u:
        u = u.replace(loop_marker, loop_marker + "      if (saveConfigPending) {\n        saveConfigPending = false;\n        serializeConfigToFS();\n      }\n", 1)

# If an earlier patch revision injected serializeConfig(), upgrade it too.
u = u.replace("serializeConfig();", "serializeConfigToFS();")

ultimate.write_text(u, encoding="utf-8")
print("WLED Ultimate 17dev bridge + UI v2 adapted to current UsermodManager + config APIs")
