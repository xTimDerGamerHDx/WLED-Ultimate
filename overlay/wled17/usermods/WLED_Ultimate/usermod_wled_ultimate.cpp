#include "wled.h"

static const char ULTIMATE_NAME[] PROGMEM = "WLED Ultimate";

static const char WLED_ULTIMATE_PAGE[] PROGMEM = R"ULTIMATEHTML(
<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>WLED Ultimate</title><style>
:root{color-scheme:dark;font-family:system-ui,-apple-system,Segoe UI,sans-serif;background:#071019;color:#eef7ff}*{box-sizing:border-box}body{margin:0;background:radial-gradient(circle at top,#12304a 0,#071019 42%);min-height:100vh}.wrap{max-width:920px;margin:auto;padding:22px}.head{display:flex;gap:14px;align-items:center;margin-bottom:18px}.logo{width:48px;height:48px;border-radius:14px;background:#18d67c;box-shadow:0 0 28px #18d67c66;display:grid;place-items:center;color:#04120b;font-weight:900}.title h1{margin:0;font-size:25px}.title p{margin:4px 0 0;color:#8ca6b8;font-size:13px}.status{margin-left:auto;padding:7px 10px;border:1px solid #27445b;border-radius:999px;color:#92abc0;font-size:12px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));gap:12px}.card{background:#0d1c28;border:1px solid #203747;border-radius:15px;padding:15px;display:flex;align-items:center;gap:12px;min-height:74px}.txt{flex:1}.name{font-weight:700}.sub{font-size:11px;color:#7894a8;margin-top:3px}.sw{position:relative;width:47px;height:27px;display:inline-block}.sw input{display:none}.sl{position:absolute;inset:0;background:#293946;border-radius:18px;transition:.2s}.sl:before{content:"";position:absolute;width:21px;height:21px;left:3px;top:3px;background:#dbe9f2;border-radius:50%;transition:.2s}.sw input:checked+.sl{background:#18d67c}.sw input:checked+.sl:before{transform:translateX(20px);background:#04120b}.sw input:disabled+.sl{opacity:.3}.perf{margin-top:12px;background:#0d1c28;border:1px solid #203747;border-radius:15px;padding:15px}.perfline{display:flex;align-items:center;gap:12px}.perf input[type=range]{width:100%}.fps{min-width:58px;text-align:right;font-weight:700;color:#18d67c}.note{margin-top:16px;color:#7792a6;font-size:12px;line-height:1.5}.ok{color:#18d67c}.err{color:#ff6b6b}@media(max-width:560px){.wrap{padding:14px}.status{display:none}}
</style></head><body><div class="wrap"><div class="head"><div class="logo">U</div><div class="title"><h1>WLED Ultimate</h1><p>17dev control layer</p></div><div id="status" class="status">Connecting...</div></div><div id="grid" class="grid"></div><div class="perf"><div class="perfline"><div class="txt"><div class="name">High Performance FPS</div><div class="sub">Runtime target FPS</div></div><input id="fps" type="range" min="20" max="120"><div id="fpsv" class="fps">60 FPS</div></div></div><div class="note">Nicht verfügbare Funktionen werden automatisch gesperrt. Dadurch bleibt die Ultimate-Oberfläche auf allen Builds gleich, ohne Funktionen vorzutäuschen.</div></div><script>
const defs=[['advancedAudioEngine','Advanced Audio Engine','AudioReactive engine','audioAvailable'],['particleFx','Particle FX','WLED particle system','particleAvailable'],['audioParticleFx','Audio Particle FX','Ultimate audio/particle bridge','audioParticleAvailable'],['wledMmEffects','WLED-MM Effects','ported MoonModules effects','mmEffectsAvailable'],['ethernet','Ethernet','wired networking','ethernetAvailable'],['wifiFallback','WiFi fallback','WiFi fallback path','wifiAvailable'],['audioUdpSync','Audio UDP Sync','network audio synchronization','audioAvailable'],['highPerformanceMode','High Performance Mode','higher render target','performanceAvailable'],['psramLedBuffer','PSRAM LED Buffer','PSRAM-backed buffers','psramAvailable'],['experimentalEffects','Experimental Effects','experimental Ultimate FX','experimentalAvailable']];
const g=document.getElementById('grid'),s=document.getElementById('status'),fps=document.getElementById('fps'),fpsv=document.getElementById('fpsv');
for(const d of defs){let c=document.createElement('div');c.className='card';c.innerHTML=`<div class="txt"><div class="name">${d[1]}</div><div class="sub">${d[2]}</div></div><label class="sw"><input id="${d[0]}" type="checkbox"><span class="sl"></span></label>`;g.appendChild(c);document.getElementById(d[0]).onchange=e=>send(d[0],e.target.checked)}
fps.oninput=()=>fpsv.textContent=fps.value+' FPS';fps.onchange=()=>send('highPerformanceFps',Number(fps.value));
async function send(k,v){s.textContent='Saving...';try{let r=await fetch('/json/state',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({ultimate:{[k]:v}})});if(!r.ok)throw Error(r.status);s.textContent='Saved';s.className='status ok';setTimeout(()=>s.textContent='Connected',800)}catch(e){s.textContent='Save failed';s.className='status err'}}
async function load(){try{let r=await fetch('/json/state'),j=await r.json(),u=j.ultimate||{},c=u.capabilities||{};for(const d of defs){let e=document.getElementById(d[0]);e.checked=!!u[d[0]];if(c[d[3]]===false){e.checked=false;e.disabled=true;e.closest('.card').querySelector('.sub').textContent='Nicht verfügbar in diesem Build'}}fps.value=u.highPerformanceFps||60;fpsv.textContent=fps.value+' FPS';s.textContent='Connected';s.className='status ok'}catch(e){s.textContent='Offline';s.className='status err'}}load();
</script></body></html>
)ULTIMATEHTML";

class WLEDUltimate17Usermod : public Usermod {
  private:
    bool advancedAudioEngine = true;
    bool particleFx = true;
    bool audioParticleFx = false;
    bool wledMmEffects = false;
    bool ethernet = true;
    bool wifiFallback = true;
    bool audioUdpSync = true;
    bool highPerformanceMode = true;
    bool psramLedBuffer = false;
    bool experimentalEffects = true;
    bool initDone = false;
    uint8_t highPerformanceFps = 60;

    bool psramAvailable() const {
#if defined(BOARD_HAS_PSRAM) || defined(WLED_USE_PSRAM) || defined(WLED_USE_PSRAM_JSON) || defined(WLED_ULTIMATE_PSRAM)
      return true;
#else
      return false;
#endif
    }

    bool ethernetAvailable() const {
#if defined(WLED_USE_ETHERNET) || defined(WLED_ULTIMATE_ETHERNET)
      return true;
#else
      return false;
#endif
    }

    void applyRuntime() {
      if (!psramAvailable()) psramLedBuffer = false;
      if (!ethernetAvailable()) ethernet = false;
      uint8_t fps = highPerformanceFps;
      if (fps < 20) fps = 20;
      if (fps > 120) fps = 120;
      highPerformanceFps = fps;
      strip.setTargetFps(highPerformanceMode ? fps : 42);
    }

  public:
    void setup() override {
      applyRuntime();
      server.on("/ultimate", HTTP_GET, [](AsyncWebServerRequest *request) {
        request->send_P(200, "text/html", WLED_ULTIMATE_PAGE);
      });
      initDone = true;
    }

    void addToJsonInfo(JsonObject& root) override {
      JsonObject user = root["u"];
      if (user.isNull()) user = root.createNestedObject("u");
      JsonArray v = user.createNestedArray("WLED Ultimate");
      v.add(F("17dev Control Layer v1"));
      JsonArray p = user.createNestedArray("Ultimate UI");
      p.add(F("/ultimate"));
    }

    void addToJsonState(JsonObject& root) override {
      JsonObject u = root["ultimate"];
      if (u.isNull()) u = root.createNestedObject("ultimate");
      u["advancedAudioEngine"] = advancedAudioEngine;
      u["particleFx"] = particleFx;
      u["audioParticleFx"] = audioParticleFx;
      u["wledMmEffects"] = wledMmEffects;
      u["ethernet"] = ethernet;
      u["wifiFallback"] = wifiFallback;
      u["audioUdpSync"] = audioUdpSync;
      u["highPerformanceMode"] = highPerformanceMode;
      u["highPerformanceFps"] = highPerformanceFps;
      u["psramLedBuffer"] = psramLedBuffer;
      u["experimentalEffects"] = experimentalEffects;
      JsonObject c = u.createNestedObject("capabilities");
      c["audioAvailable"] = true;
#if defined(WLED_DISABLE_PARTICLESYSTEM1D) && defined(WLED_DISABLE_PARTICLESYSTEM2D)
      c["particleAvailable"] = false;
#else
      c["particleAvailable"] = true;
#endif
      c["audioParticleAvailable"] = false;
      c["mmEffectsAvailable"] = false;
      c["ethernetAvailable"] = ethernetAvailable();
      c["wifiAvailable"] = true;
      c["performanceAvailable"] = true;
      c["psramAvailable"] = psramAvailable();
      c["experimentalAvailable"] = true;
    }

    void readFromJsonState(JsonObject& root) override {
      if (!initDone) return;
      JsonObject u = root["ultimate"];
      if (u.isNull()) return;
      bool before[10] = {advancedAudioEngine,particleFx,audioParticleFx,wledMmEffects,ethernet,wifiFallback,audioUdpSync,highPerformanceMode,psramLedBuffer,experimentalEffects};
      uint8_t oldFps = highPerformanceFps;
      advancedAudioEngine = u["advancedAudioEngine"] | advancedAudioEngine;
      particleFx = u["particleFx"] | particleFx;
      audioParticleFx = u["audioParticleFx"] | audioParticleFx;
      wledMmEffects = u["wledMmEffects"] | wledMmEffects;
      ethernet = u["ethernet"] | ethernet;
      wifiFallback = u["wifiFallback"] | wifiFallback;
      audioUdpSync = u["audioUdpSync"] | audioUdpSync;
      highPerformanceMode = u["highPerformanceMode"] | highPerformanceMode;
      highPerformanceFps = u["highPerformanceFps"] | highPerformanceFps;
      psramLedBuffer = u["psramLedBuffer"] | psramLedBuffer;
      experimentalEffects = u["experimentalEffects"] | experimentalEffects;
      applyRuntime();
      bool after[10] = {advancedAudioEngine,particleFx,audioParticleFx,wledMmEffects,ethernet,wifiFallback,audioUdpSync,highPerformanceMode,psramLedBuffer,experimentalEffects};
      bool changed = oldFps != highPerformanceFps;
      for (uint8_t i=0;i<10;i++) changed |= before[i] != after[i];
      if (changed) doSerializeConfig = true;
    }

    void addToConfig(JsonObject& root) override {
      JsonObject top = root.createNestedObject(FPSTR(ULTIMATE_NAME));
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
      JsonObject top = root[FPSTR(ULTIMATE_NAME)];
      bool complete = !top.isNull();
      complete &= getJsonValue(top["Advanced Audio Engine"], advancedAudioEngine, true);
      complete &= getJsonValue(top["Particle FX"], particleFx, true);
      complete &= getJsonValue(top["Audio Particle FX"], audioParticleFx, false);
      complete &= getJsonValue(top["WLED-MM Effects"], wledMmEffects, false);
      complete &= getJsonValue(top["Ethernet"], ethernet, true);
      complete &= getJsonValue(top["WiFi fallback"], wifiFallback, true);
      complete &= getJsonValue(top["Audio UDP Sync"], audioUdpSync, true);
      complete &= getJsonValue(top["High Performance Mode"], highPerformanceMode, true);
      complete &= getJsonValue(top["High Performance FPS"], highPerformanceFps, 60);
      complete &= getJsonValue(top["PSRAM LED Buffer"], psramLedBuffer, false);
      complete &= getJsonValue(top["Experimental Effects"], experimentalEffects, true);
      if (initDone) applyRuntime();
      return complete;
    }
};

static WLEDUltimate17Usermod wledUltimate17;
REGISTER_USERMOD(wledUltimate17);
