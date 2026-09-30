#pragma once

#include "wled.h"

#ifdef USERMOD_AUDIOREACTIVE

static bool ultimateParticleFxMaster = true;
static bool ultimateAudioParticleFxMaster = true;

static uint16_t mode_ultimate_audio_particles() {
  if (!ultimateParticleFxMaster || !ultimateAudioParticleFxMaster || disableSoundProcessing) {
    SEGMENT.fadeToBlackBy(96);
    return FRAMETIME;
  }

  const uint8_t bass = max(fftResult[0], fftResult[1]);
  const uint8_t mids = max(fftResult[5], fftResult[7]);
  const uint8_t treble = max(fftResult[12], fftResult[15]);

  uint8_t fade = 12 + ((255 - SEGMENT.intensity) >> 2);
  SEGMENT.fadeToBlackBy(fade);

  uint8_t particleCount = 1 + (bass >> 5) + (mids >> 6);
  if (samplePeak) particleCount += 5;
  if (particleCount > 12) particleCount = 12;

  const uint16_t len = SEGLEN;
  if (len == 0) return FRAMETIME;

  for (uint8_t i = 0; i < particleCount; i++) {
    uint32_t phase = (millis() * (2U + (SEGMENT.speed >> 6))) + (i * 977U) + (bass * 17U) + (treble * 7U);
    uint16_t pos = phase % len;
    uint8_t pal = uint8_t(bass + (i * 23U) + (treble >> 1));
    uint8_t bri = qadd8(72, max(bass, max(mids, treble)));
    uint32_t color = SEGMENT.color_from_palette(pal, false, true, 0, bri);
    SEGMENT.addPixelColor(pos, color, true);
    if (samplePeak && len > 2) {
      SEGMENT.addPixelColor((pos + 1) % len, color, true);
      SEGMENT.addPixelColor((pos + len - 1) % len, color, true);
    }
  }

  return FRAMETIME;
}

static const char _data_ultimate_audio_particles[] PROGMEM =
  "Ultimate Audio Particles@Motion,Trail;!,!;!;1;pal=11";

static uint16_t mode_ultimate_audio_spectrum() {
  if (!ultimateParticleFxMaster || !ultimateAudioParticleFxMaster || disableSoundProcessing) {
    SEGMENT.fadeToBlackBy(96);
    return FRAMETIME;
  }

  const uint16_t len = SEGLEN;
  if (len == 0) return FRAMETIME;

  SEGMENT.fadeToBlackBy(80);
  uint8_t threshold = 8 + ((255 - SEGMENT.intensity) >> 3);

  for (uint16_t i = 0; i < len; i++) {
    uint8_t bin = (uint32_t(i) * NUM_GEQ_CHANNELS) / len;
    if (bin >= NUM_GEQ_CHANNELS) bin = NUM_GEQ_CHANNELS - 1;
    uint8_t level = fftResult[bin];
    if (level > threshold) {
      uint8_t bri = qadd8(48, level);
      uint32_t color = SEGMENT.color_from_palette(bin * 16U, false, true, 0, bri);
      SEGMENT.setPixelColor(i, color);
    }
  }

  if (samplePeak) {
    uint16_t center = len >> 1;
    SEGMENT.setPixelColor(center, SEGMENT.color_from_palette(255, false, true, 0, 255));
  }

  return FRAMETIME;
}

static const char _data_ultimate_audio_spectrum[] PROGMEM =
  "Ultimate Audio Spectrum@Speed,Sensitivity;!,!;!;1;pal=71";

static inline void registerWLEDUltimateAudioFx() {
  strip.addEffect(255, &mode_ultimate_audio_particles, _data_ultimate_audio_particles);
  strip.addEffect(255, &mode_ultimate_audio_spectrum, _data_ultimate_audio_spectrum);
}

#endif
