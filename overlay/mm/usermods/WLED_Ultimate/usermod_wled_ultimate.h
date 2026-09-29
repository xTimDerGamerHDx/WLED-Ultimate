#pragma once

#include "wled.h"

static const char WLED_ULTIMATE_PAGE[] PROGMEM = R"ULTIMATEHTML(
<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<title>WLED Ultimate</title><style>
:root{color-scheme:dark;font-family:system-ui,-apple-system,Segoe UI,sans-serif;background:#071019;color:#eef7ff}*{box-sizing:border-box}body{margin:0;background:radial-gradient(circle at top,#12304a 0,#071019 42%);min-height:100vh}.wrap{max-width:920px;margin:auto;padding:22px}.head{display:flex;gap:14px;align-items:center;margin-bottom:18px}.logo{width:48px;height:48px;border-radius:14px;background:#18d67c;box-shadow:0 0 28px #18d67c66;display:grid;place-items:center;color:#04120b;font-weight:900}.title h1{margin:0;font-size:25px}.title p{margin:4px 0 0;color:#8ca6b8;font-size:13px}.status{margin-left:auto;padding:7px 10px;border:1px solid #27445b;border-radius:999px;color:#92abc0;font-size:12px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));gap:12px}.card{background:#0d1c28;border:1px solid #203747;border-radius:15px;padding:15px;display:flex;align-items:center;gap:12px;min-height:74px}.card:hover{border-color:#35627e}.txt{flex:1}.name{font-weight:700}.sub{font-size:11px;color:#7894a8;margin-top:3px}.sw{position:relative;width:47px;height:27px;display:inline-block}.sw input{display:none}.sl{position:absolute;inset:0;background:#293946;border-radius:18px;transition:.2s}.sl:before{content:"";position:absolute;width:21px;height:21px;left:3px;top:3px;background:#dbe9f2;border-radius:50%;transition:.2s}.sw input:checked+.sl{background:#18d67c}.sw input:checked+.sl:before{transform:translateX(20px);background:#04120b}.sw input:disabled+.sl{opacity:.35}.perf{margin-top:12px;background:#0d1c28;border:1px solid #203747;border-radius:15px;padding:15px}.perfline{display:flex;align-items:center;gap:12px}.perf input[type=range]{width:100%}.fps{min-width:58px;text-align:right;font-weight:700;color:#18d67c}.note{margin-top:16px;color:#7792a6;font-size:12px;line-height:1.5}.ok{color:#18d67c}.err{color:#ff6b6b}@media(max-width:560px){.wrap{padding:14px}.status{display:none}}
</style></head><body><div class="wrap"><div class="head"><div class="logo">U</div><div class="title"><h1>WLED Ultimate</h1><p>MoonModules control layer</p></div><div id="status" class="status">Connecting...</div></div><div id="grid" class="grid"></div><div class="perf"><div class="perfline"><div class="txt"><div class="name">High Performance FPS</div><div class="sub">Applied immediately while High Performance Mode is enabled</div></div><input id="fps" type="range" min="20" max="120" step="1"><div id="fpsv" class="fps">60 FPS</div></div></div><div class="note">High Performance Mode is runtime-wired now. The remaining switches are persistent Ultimate control flags and are being connected to the Audio, Particle, Network and PSRAM subsystems without changing this UI/API contract.</div></div><script>
const defs=[['advancedAudioEngine','Advanced Audio Engine','FFT / AudioReactive control'],['particleFx','Particle FX','Particle-system effects'],['audioParticleFx','Audio Particle FX','Audio-driven particle bridge'],['wledMmEffects','WLED-MM Effects','MoonModules effect set'],['ethernet','Ethernet','Wired network control'],['wifiFallback','WiFi fallback','Fallback network path'],['audioUdpSync','Audio UDP Sync','Network audio synchronization'],['highPerformanceMode','High Performance Mode','Higher target render rate'],['psramLedBuffer','PSRAM LED Buffer','PSRAM-backed LED buffering'],['experimentalEffects','Experimental Effects','Experimental effect group']];
const grid=document.getElementById('grid'),statusEl=document.getElementById('status'),fps=document.getElementById('fps'),fpsv=document.getElementById('fpsv');
for(const d of defs){let c=document.createElement('div');c.className='card';c.innerHTML=`<div class="txt"><div class="name">${d[1]}</div><div class="sub">${d[2]}</div></div><label class="sw"><input id="${d[0]}" type="checkbox"><span class="sl"></span></label>`;grid.appendChild(c);document.getElementById(d[0]).addEventListener('change',e=>send(d[0],e.target.checked));}
fps.addEventListener('input',()=>fpsv.textContent=fps.value+' FPS');fps.addEventListener('change',()=>send('highPerformanceFps',Number(fps.value)));
async function send(k,v){statusEl.textContent='Saving...';try{let r=await fetch('/json/state',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({ultimate:{[k]:v}})});if(!r.ok)throw Error(r.status);statusEl.textContent='Saved';statusEl.className='status ok';setTimeout(()=>statusEl.textContent='Connected',900);}catch(e){statusEl.textContent='Save failed';statusEl.className='status err';}}
async function load(){try{let r=await fetch('/json/state');let j=await r.json(),u=j.ultimate||{};for(const d of defs)document.getElementById(d[0]).checked=!!u[d[0]];fps.value=u.highPerformanceFps||60;fpsv.textContent=fps.value+' FPS';let p=document.getElementById('psramLedBuffer');if(u.psramAvailable===false){p.checked=false;p.disabled=true;p.closest('.card').querySelector('.sub').textContent='Not available on this hardware';}statusEl.textContent='Connected';statusEl.className='status ok';}catch(e){statusEl.textContent='Offline';statusEl.className='status err';}}
load();
</script></body></html>
)ULTIMATEHTML";

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
#if defined(BOARD_HAS_PSRAM) || defined(WLED_USE_PSRAM) || defined(WLED_USE_PSRAM_JSON) || defined(WLED_ULTIMATE_PSRAM)
      return true;
#else
      return false;
#endif
    }

    void applyRuntimeSettings() {
      if (highPerformanceMode) {
        uint8_t fps = highPerformanceFps;
        if (fps < 20) fps = 20;
        if (fps > 120) fps = 120;
        highPerformanceFps = fps;
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
      server.on("/ultimate", HTTP_GET, [](AsyncWebServerRequest *request) {
        request->send_P(200, "text/html", WLED_ULTIMATE_PAGE);
      });
      initDone = true;
    }

    void addToJsonInfo(JsonObject& root) override {
      JsonObject user = root["u"];
      if (user.isNull()) user = root.createNestedObject("u");
      JsonArray version = user.createNestedArray("WLED Ultimate");
      version.add(F("Control Layer v1"));
      JsonArray page = user.createNestedArray("Ultimate UI");
      page.add(F("/ultimate"));
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

      bool oldAdvancedAudioEngine = advancedAudioEngine;
      bool oldParticleFx = particleFx;
      bool oldAudioParticleFx = audioParticleFx;
      bool oldWledMmEffects = wledMmEffects;
      bool oldEthernet = ethernet;
      bool oldWifiFallback = wifiFallback;
      bool oldAudioUdpSync = audioUdpSync;
      bool oldHighPerformanceMode = highPerformanceMode;
      bool oldPsramLedBuffer = psramLedBuffer;
      bool oldExperimentalEffects = experimentalEffects;
      uint8_t oldHighPerformanceFps = highPerformanceFps;

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

      bool changed = oldAdvancedAudioEngine != advancedAudioEngine || oldParticleFx != particleFx ||
        oldAudioParticleFx != audioParticleFx || oldWledMmEffects != wledMmEffects ||
        oldEthernet != ethernet || oldWifiFallback != wifiFallback || oldAudioUdpSync != audioUdpSync ||
        oldHighPerformanceMode != highPerformanceMode || oldHighPerformanceFps != highPerformanceFps ||
        oldPsramLedBuffer != psramLedBuffer || oldExperimentalEffects != experimentalEffects;
      if (changed) doSerializeConfig = true;
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
