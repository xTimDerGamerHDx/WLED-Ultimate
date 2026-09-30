#!/usr/bin/env python3
from pathlib import Path
import sys

if len(sys.argv) != 2:
    raise SystemExit("usage: apply_audio_controls_v21.py <wled-source-dir>")

source = Path(sys.argv[1])
repo_root = Path(__file__).resolve().parents[1]
controls_source = repo_root / "overlay" / "mm" / "usermods" / "WLED_Ultimate" / "ultimate_audio_controls_v21.h"
if not controls_source.exists():
    raise SystemExit(f"missing {controls_source}")


def wire_ui(ui_path: Path):
    if not ui_path.exists():
        raise SystemExit(f"missing {ui_path}")
    text = ui_path.read_text(encoding="utf-8")
    if '/ultimate-audio-controls-v21.js' not in text:
        marker = '<script src="/ultimate-v21.js"></script>'
        if marker not in text:
            raise SystemExit("unable to locate v2.1 script tag")
        text = text.replace(marker, marker + '\n<script src="/ultimate-audio-controls-v21.js"></script>', 1)
        ui_path.write_text(text, encoding="utf-8")


def wire_mm():
    ultimate = source / "usermods" / "WLED_Ultimate" / "usermod_wled_ultimate.h"
    ui = source / "usermods" / "WLED_Ultimate" / "ultimate_ui_v2.h"
    controls_target = source / "usermods" / "WLED_Ultimate" / "ultimate_audio_controls_v21.h"
    if not ultimate.exists():
        raise SystemExit(f"missing {ultimate}")
    controls_target.write_text(controls_source.read_text(encoding="utf-8"), encoding="utf-8")
    wire_ui(ui)

    u = ultimate.read_text(encoding="utf-8")
    if '#include "ultimate_audio_controls_v21.h"' not in u:
        marker = '#include "ultimate_ui_v21_patch.h"\n'
        if marker not in u:
            raise SystemExit("unable to locate MM UI v2.1 include")
        u = u.replace(marker, marker + '#include "ultimate_audio_controls_v21.h"\n', 1)

    if 'ultimateMmAudioConfigJson' not in u:
        marker = 'class WLEDUltimateUsermod : public Usermod {\n'
        if marker not in u:
            raise SystemExit("unable to locate MM Ultimate class")
        helper = r'''static String ultimateMmAudioConfigJson() {
#ifdef USERMOD_AUDIOREACTIVE
  String json;
  json.reserve(190);
  json = F("{\"available\":true,\"gain\":"); json += sampleGain;
  json += F(",\"squelch\":"); json += soundSquelch;
  json += F(",\"input\":"); json += inputLevel;
  json += F(",\"agc\":"); json += soundAgc;
  json += F(",\"fftScale\":"); json += FFTScalingMode;
  json += F(",\"sync\":"); json += audioSyncEnabled;
  json += F("}");
  return json;
#else
  return F("{\"available\":false,\"gain\":0,\"squelch\":0,\"input\":0,\"agc\":0,\"fftScale\":0,\"sync\":0}");
#endif
}

'''
        u = u.replace(marker, helper + marker, 1)

    if 'server.on("/ultimate-audio-controls-v21.js"' not in u:
        marker = '      initDone = true;\n'
        if marker not in u:
            raise SystemExit("unable to locate MM setup route marker")
        routes = r'''      server.on("/ultimate-audio-controls-v21.js", HTTP_GET, [](AsyncWebServerRequest *request) {
        request->send_P(200, "application/javascript", WLED_ULTIMATE_AUDIO_CONTROLS_V21_JS);
      });
      server.on("/ultimate/api/audio-config", HTTP_GET, [](AsyncWebServerRequest *request) {
        request->send(200, "application/json", ultimateMmAudioConfigJson());
      });
      server.on("/ultimate/api/audio-config", HTTP_POST, [this](AsyncWebServerRequest *request) {
#ifdef USERMOD_AUDIOREACTIVE
        bool changed = false;
        if (request->hasParam("gain", true)) { sampleGain = constrain(request->getParam("gain", true)->value().toInt(), 0, 255); changed = true; }
        if (request->hasParam("squelch", true)) { soundSquelch = constrain(request->getParam("squelch", true)->value().toInt(), 0, 255); changed = true; }
        if (request->hasParam("input", true)) { inputLevel = constrain(request->getParam("input", true)->value().toInt(), 0, 255); changed = true; }
        if (request->hasParam("agc", true)) { soundAgc = constrain(request->getParam("agc", true)->value().toInt(), 0, 3); changed = true; }
        if (request->hasParam("fftScale", true)) { FFTScalingMode = constrain(request->getParam("fftScale", true)->value().toInt(), 0, 3); changed = true; }
        if (request->hasParam("sync", true)) {
          uint8_t mode = constrain(request->getParam("sync", true)->value().toInt(), 0, 2);
          audioSyncEnabled = mode;
          audioUdpSync = mode != 0;
          if (mode != AUDIOSYNC_NONE) rememberedAudioSyncMode = mode;
          changed = true;
        }
        if (changed) doSerializeConfig = true;
#endif
        request->send(200, "application/json", ultimateMmAudioConfigJson());
      });
'''
        u = u.replace(marker, routes + marker, 1)

    ultimate.write_text(u, encoding="utf-8")
    print("Ultimate UI v2.1 AudioReactive controls wired for MoonModules")


def wire_17dev():
    audio = source / "usermods" / "audioreactive" / "audio_reactive.cpp"
    ultimate = source / "usermods" / "WLED_Ultimate" / "usermod_wled_ultimate.cpp"
    ui = source / "usermods" / "WLED_Ultimate" / "ultimate_ui_v2.h"
    controls_target = source / "usermods" / "WLED_Ultimate" / "ultimate_audio_controls_v21.h"
    if not audio.exists() or not ultimate.exists():
        raise SystemExit("missing WLED 17dev AudioReactive or Ultimate source")
    controls_target.write_text(controls_source.read_text(encoding="utf-8"), encoding="utf-8")
    wire_ui(ui)

    a = audio.read_text(encoding="utf-8")
    if 'WLED_ULTIMATE_AUDIO_TUNING_BRIDGE' not in a:
        a += r'''

// WLED_ULTIMATE_AUDIO_TUNING_BRIDGE
extern "C" void wledUltimate17GetAudioTuning(uint8_t *gain, uint8_t *squelch, uint8_t *input, uint8_t *agc, uint8_t *fftScale, uint8_t *syncMode) {
  if (gain) *gain = sampleGain;
  if (squelch) *squelch = soundSquelch;
  if (input) *input = inputLevel;
  if (agc) *agc = soundAgc;
  if (fftScale) *fftScale = FFTScalingMode;
  if (syncMode) *syncMode = audioSyncEnabled;
}

extern "C" void wledUltimate17SetAudioTuning(uint8_t gain, uint8_t squelch, uint8_t input, uint8_t agc, uint8_t fftScale, uint8_t syncMode) {
  sampleGain = gain;
  soundSquelch = squelch;
  inputLevel = input;
  soundAgc = agc > 3 ? 3 : agc;
  FFTScalingMode = fftScale > 3 ? 3 : fftScale;
  audioSyncEnabled = syncMode > 2 ? 2 : syncMode;
}
'''
        audio.write_text(a, encoding="utf-8")

    u = ultimate.read_text(encoding="utf-8")
    if '#include "ultimate_audio_controls_v21.h"' not in u:
        marker = '#include "ultimate_ui_v21_patch.h"\n'
        if marker not in u:
            raise SystemExit("unable to locate 17dev UI v2.1 include")
        u = u.replace(marker, marker + '#include "ultimate_audio_controls_v21.h"\n', 1)

    if 'wledUltimate17GetAudioTuning' not in u:
        marker = 'extern "C" void wledUltimate17SetAudioSync(bool enabled);\n'
        if marker not in u:
            raise SystemExit("unable to locate 17dev audio bridge declarations")
        decl = '''extern "C" void wledUltimate17GetAudioTuning(uint8_t *gain, uint8_t *squelch, uint8_t *input, uint8_t *agc, uint8_t *fftScale, uint8_t *syncMode);\nextern "C" void wledUltimate17SetAudioTuning(uint8_t gain, uint8_t squelch, uint8_t input, uint8_t agc, uint8_t fftScale, uint8_t syncMode);\n'''
        u = u.replace(marker, marker + decl, 1)

    if 'ultimate17AudioConfigJson' not in u:
        marker = 'static String ultimate17AudioTelemetryJson() {\n'
        if marker not in u:
            raise SystemExit("unable to locate 17dev telemetry helper")
        helper = r'''static String ultimate17AudioConfigJson() {
  uint8_t gain=0, squelch=0, input=0, agc=0, fftScale=0, syncMode=0;
  wledUltimate17GetAudioTuning(&gain, &squelch, &input, &agc, &fftScale, &syncMode);
  String json;
  json.reserve(190);
  json = F("{\"available\":true,\"gain\":"); json += gain;
  json += F(",\"squelch\":"); json += squelch;
  json += F(",\"input\":"); json += input;
  json += F(",\"agc\":"); json += agc;
  json += F(",\"fftScale\":"); json += fftScale;
  json += F(",\"sync\":"); json += syncMode;
  json += F("}");
  return json;
}

'''
        u = u.replace(marker, helper + marker, 1)

    if 'server.on("/ultimate-audio-controls-v21.js"' not in u:
        marker = '      initDone = true;\n'
        if marker not in u:
            raise SystemExit("unable to locate 17dev setup route marker")
        routes = r'''      server.on("/ultimate-audio-controls-v21.js", HTTP_GET, [](AsyncWebServerRequest *request) {
        request->send_P(200, "application/javascript", WLED_ULTIMATE_AUDIO_CONTROLS_V21_JS);
      });
      server.on("/ultimate/api/audio-config", HTTP_GET, [](AsyncWebServerRequest *request) {
        request->send(200, "application/json", ultimate17AudioConfigJson());
      });
      server.on("/ultimate/api/audio-config", HTTP_POST, [this](AsyncWebServerRequest *request) {
        uint8_t gain=0, squelch=0, input=0, agc=0, fftScale=0, syncMode=0;
        wledUltimate17GetAudioTuning(&gain, &squelch, &input, &agc, &fftScale, &syncMode);
        if (request->hasParam("gain", true)) gain = constrain(request->getParam("gain", true)->value().toInt(), 0, 255);
        if (request->hasParam("squelch", true)) squelch = constrain(request->getParam("squelch", true)->value().toInt(), 0, 255);
        if (request->hasParam("input", true)) input = constrain(request->getParam("input", true)->value().toInt(), 0, 255);
        if (request->hasParam("agc", true)) agc = constrain(request->getParam("agc", true)->value().toInt(), 0, 3);
        if (request->hasParam("fftScale", true)) fftScale = constrain(request->getParam("fftScale", true)->value().toInt(), 0, 3);
        if (request->hasParam("sync", true)) syncMode = constrain(request->getParam("sync", true)->value().toInt(), 0, 2);
        wledUltimate17SetAudioTuning(gain, squelch, input, agc, fftScale, syncMode);
        audioUdpSync = syncMode != 0;
        saveConfigPending = true;
        request->send(200, "application/json", ultimate17AudioConfigJson());
      });
'''
        u = u.replace(marker, routes + marker, 1)

    ultimate.write_text(u, encoding="utf-8")
    print("Ultimate UI v2.1 AudioReactive controls wired for WLED 17dev")


# WLED 17dev also contains wled00/, so detect it by the Ultimate .cpp and the
# upstream AudioReactive translation unit before falling back to MoonModules.
if (source / "usermods" / "WLED_Ultimate" / "usermod_wled_ultimate.cpp").exists() and (source / "usermods" / "audioreactive" / "audio_reactive.cpp").exists():
    wire_17dev()
elif (source / "usermods" / "WLED_Ultimate" / "usermod_wled_ultimate.h").exists() and (source / "wled00" / "usermods_list.cpp").exists():
    wire_mm()
else:
    raise SystemExit("unable to detect WLED-MM or WLED 17dev source tree")
