#pragma once

#include "wled.h"

class WLEDUltimateUsermod : public Usermod {
  private:
    bool advancedAudioEngine = true;
    bool particleFx = true;
    bool audioParticleFx = true;
    bool wledMmEffects = true;
    bool ethernet = true;
    bool wifiFallback = true;
    bool audioUdpSync = true;
    bool highPerformanceMode = true;
    bool psramLedBuffer = false;
    bool experimentalEffects = true;
    uint8_t highPerformanceFps = 60;

    bool psramAvailable() const {
#if defined(BOARD_HAS_PSRAM) || defined(WLED_USE_PSRAM) || defined(WLED_USE_PSRAM_JSON)
      return true;
#else
      return false;
#endif
    }

    void applyRuntimeSettings() {
      // First runtime-wired Ultimate option. The remaining switches are
      // persistent control-plane flags and are connected to their subsystems
      // incrementally so the UI/API contract remains stable.
      if (highPerformanceMode) {
        uint8_t fps = highPerformanceFps;
        if (fps < 20) fps = 20;
        if (fps > 120) fps = 120;
        strip.setTargetFps(fps);
      } else {
        strip.setTargetFps(42);
      }

      if (!psramAvailable()) psramLedBuffer = false;
    }

  public:
    WLEDUltimateUsermod(const char *name, bool enabled) : Usermod(name, enabled) {}

    void setup() override {
      applyRuntimeSettings();
      initDone = true;
    }

    void addToJsonInfo(JsonObject& root) override {
      JsonObject user = root["u"];
      if (user.isNull()) user = root.createNestedObject("u");

      JsonArray version = user.createNestedArray("WLED Ultimate");
      version.add(F("Control Layer v1"));

      JsonArray perf = user.createNestedArray("Ultimate High Performance");
      perf.add(highPerformanceMode ? F("ON") : F("OFF"));

      JsonArray psram = user.createNestedArray("Ultimate PSRAM Buffer");
      if (!psramAvailable()) psram.add(F("Unavailable"));
      else psram.add(psramLedBuffer ? F("ON") : F("OFF"));

#ifdef WLED_ULTIMATE_GLEDOPTO_GL_C_618WL
      JsonArray board = user.createNestedArray("Ultimate Board");
      board.add(F("Gledopto GL-C-618WL"));
#endif
    }

    void addToJsonState(JsonObject& root) override {
      JsonObject ultimate = root["ultimate"];
      if (ultimate.isNull()) ultimate = root.createNestedObject("ultimate");

      ultimate["advancedAudioEngine"] = advancedAudioEngine;
      ultimate["particleFx"] = particleFx;
      ultimate["audioParticleFx"] = audioParticleFx;
      ultimate["wledMmEffects"] = wledMmEffects;
      ultimate["ethernet"] = ethernet;
      ultimate["wifiFallback"] = wifiFallback;
      ultimate["audioUdpSync"] = audioUdpSync;
      ultimate["highPerformanceMode"] = highPerformanceMode;
      ultimate["highPerformanceFps"] = highPerformanceFps;
      ultimate["psramLedBuffer"] = psramLedBuffer;
      ultimate["psramAvailable"] = psramAvailable();
      ultimate["experimentalEffects"] = experimentalEffects;
    }

    void readFromJsonState(JsonObject& root) override {
      if (!initDone) return;
      JsonObject ultimate = root["ultimate"];
      if (ultimate.isNull()) return;

      advancedAudioEngine = ultimate["advancedAudioEngine"] | advancedAudioEngine;
      particleFx = ultimate["particleFx"] | particleFx;
      audioParticleFx = ultimate["audioParticleFx"] | audioParticleFx;
      wledMmEffects = ultimate["wledMmEffects"] | wledMmEffects;
      ethernet = ultimate["ethernet"] | ethernet;
      wifiFallback = ultimate["wifiFallback"] | wifiFallback;
      audioUdpSync = ultimate["audioUdpSync"] | audioUdpSync;
      highPerformanceMode = ultimate["highPerformanceMode"] | highPerformanceMode;
      highPerformanceFps = ultimate["highPerformanceFps"] | highPerformanceFps;
      psramLedBuffer = ultimate["psramLedBuffer"] | psramLedBuffer;
      experimentalEffects = ultimate["experimentalEffects"] | experimentalEffects;
      applyRuntimeSettings();
    }

    void addToConfig(JsonObject& root) override {
      Usermod::addToConfig(root);
      JsonObject top = root[FPSTR(_name)];

      top["Advanced Audio Engine"] = advancedAudioEngine;
      top["Particle FX"] = particleFx;
      top["Audio Particle FX"] = audioParticleFx;
      top["WLED-MM Effects"] = wledMmEffects;
      top["Ethernet"] = ethernet;
      top["WiFi fallback"] = wifiFallback;
      top["Audio UDP Sync"] = audioUdpSync;
      top["High Performance Mode"] = highPerformanceMode;
      top["High Performance FPS"] = highPerformanceFps;
      top["PSRAM LED Buffer"] = psramLedBuffer;
      top["Experimental Effects"] = experimentalEffects;
    }

    bool readFromConfig(JsonObject& root) override {
      bool configComplete = Usermod::readFromConfig(root);
      JsonObject top = root[FPSTR(_name)];

      configComplete &= getJsonValue(top["Advanced Audio Engine"], advancedAudioEngine, true);
      configComplete &= getJsonValue(top["Particle FX"], particleFx, true);
      configComplete &= getJsonValue(top["Audio Particle FX"], audioParticleFx, true);
      configComplete &= getJsonValue(top["WLED-MM Effects"], wledMmEffects, true);
      configComplete &= getJsonValue(top["Ethernet"], ethernet, true);
      configComplete &= getJsonValue(top["WiFi fallback"], wifiFallback, true);
      configComplete &= getJsonValue(top["Audio UDP Sync"], audioUdpSync, true);
      configComplete &= getJsonValue(top["High Performance Mode"], highPerformanceMode, true);
      configComplete &= getJsonValue(top["High Performance FPS"], highPerformanceFps, 60);
      configComplete &= getJsonValue(top["PSRAM LED Buffer"], psramLedBuffer, false);
      configComplete &= getJsonValue(top["Experimental Effects"], experimentalEffects, true);

      if (initDone) applyRuntimeSettings();
      return configComplete;
    }
};
