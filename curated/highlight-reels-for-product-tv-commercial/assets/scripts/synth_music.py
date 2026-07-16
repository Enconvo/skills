#!/usr/bin/env python3
"""
EnConvo launch-film score — 42s, tech/shader aesthetic, music only.
Beat-locked to the storyboard: transitions 9.4 / 20.0 / 30.4s, cut impacts
at 0.4 / 9.9 / 20.4 / 30.9 / 35.9, beat-in at the SmartBar reveal (9.8s),
big resolve on the close (35.6-42).  Pure numpy/scipy, deterministic.
"""
import numpy as np
from scipy.signal import butter, lfilter
from scipy.io import wavfile

SR = 44100
DUR = 42.0
N = int(SR * DUR)
t = np.arange(N) / SR
rng = np.random.default_rng(7)


def lp(x, fc, order=4):
    b, a = butter(order, np.clip(fc / (SR / 2), 1e-4, 0.999), btype="low")
    return lfilter(b, a, x)


def hp(x, fc, order=4):
    b, a = butter(order, np.clip(fc / (SR / 2), 1e-4, 0.999), btype="high")
    return lfilter(b, a, x)


def bp(x, lo, hi, order=4):
    b, a = butter(order, [np.clip(lo / (SR / 2), 1e-4, 0.999),
                          np.clip(hi / (SR / 2), 1e-4, 0.999)], btype="band")
    return lfilter(b, a, x)


def env_seg(points):
    """piecewise-linear envelope over time from (time, value) points."""
    ts = np.array([p[0] for p in points])
    vs = np.array([p[1] for p in points])
    return np.interp(t, ts, vs)


def saw(freq, phase=0.0):
    K = max(1, min(14, int((SR / 2) / freq)))
    out = np.zeros(N)
    for k in range(1, K + 1):
        out += np.sin(2 * np.pi * k * freq * t + phase) / k
    return out * (2 / np.pi)


def sine(freq, phase=0.0):
    return np.sin(2 * np.pi * freq * t + phase)


# ---------------------------------------------------------------- chord pad
# A major add9 voicing (bright, premium): A2 E3 A3 B3 C#4 E4  (+ air C#5/E5)
NOTES = [110.00, 164.81, 220.00, 246.94, 277.18, 329.63, 554.37, 659.25]
WEIGHT = [1.0, 0.85, 0.8, 0.6, 0.7, 0.6, 0.28, 0.22]


def build_pad(detune):
    v = np.zeros(N)
    for f, w in zip(NOTES, WEIGHT):
        v += w * saw(f * detune, phase=rng.uniform(0, 2 * np.pi))
    return v / sum(WEIGHT)


padL = build_pad(1.0000)
padR = build_pad(1.0022)  # subtle detune for stereo width

# brightness opens up across the film: crossfade dark<->bright filtered pad
bright_mix = env_seg([(0, 0.06), (5, 0.14), (9.8, 0.42), (20, 0.6),
                      (30.9, 0.9), (36, 0.6), (42, 0.4)])


def shape_pad(v):
    dark = lp(v, 780)
    brite = lp(v, 4200)
    return dark * (1 - bright_mix) + brite * bright_mix


padL = shape_pad(padL)
padR = shape_pad(padR)

# slow breathing tremolo on the pad
trem = 0.86 + 0.14 * np.sin(2 * np.pi * 0.16 * t)
padL *= trem
padR *= trem * (0.88 + 0.12 * np.sin(2 * np.pi * 0.16 * t + 0.9))

# overall pad dynamics per section
pad_dyn = env_seg([(0, 0.0), (0.5, 0.5), (5.0, 0.72), (9.8, 0.95),
                   (20.0, 1.0), (30.9, 1.0), (35.6, 1.0), (38.5, 0.8),
                   (41.4, 0.32), (42.0, 0.0)])
padL *= pad_dyn
padR *= pad_dyn

# ---------------------------------------------------------------- sub bass
sub = 0.9 * sine(55.0) + 0.25 * sine(110.0)
sub_dyn = env_seg([(0, 0.0), (1.0, 0.35), (9.8, 0.9), (20.4, 1.0),
                   (30.9, 1.0), (36.0, 0.9), (40.5, 0.45), (42.0, 0.0)])
# gentle beat pump on the sub after the beat comes in
BPM = 110.0
beat = 60.0 / BPM
pump = np.ones(N)
for bt in np.arange(9.8, 36.0, beat):
    i0 = int(bt * SR)
    seg = np.arange(0, int(0.9 * beat * SR))
    if i0 + len(seg) > N:
        seg = seg[: N - i0]
    pump[i0:i0 + len(seg)] = 0.55 + 0.45 * (seg / (0.9 * beat * SR))
sub = lp(sub, 140) * sub_dyn * pump

# ---------------------------------------------------------------- arp pluck
arp_notes = [220.00, 277.18, 329.63, 493.88, 329.63, 277.18]
pluckL = np.zeros(N)
pluckR = np.zeros(N)
ai = 0
for bt in np.arange(9.8, 35.2, beat / 2):  # 8th-note motion
    f = arp_notes[ai % len(arp_notes)]
    ai += 1
    length = int(0.42 * beat * SR)
    idx = np.arange(length)
    tt = idx / SR
    penv = np.exp(-tt * 12.0) * (1 - np.exp(-tt * 400.0))  # pluck ADSR
    tone = (np.sin(2 * np.pi * f * tt) + 0.5 * np.sin(2 * np.pi * 2 * f * tt)) * penv
    i0 = int(bt * SR)
    if i0 + length > N:
        length = N - i0
        tone = tone[:length]
    if ai % 2 == 0:
        pluckL[i0:i0 + length] += tone
        pluckR[i0:i0 + length] += tone * 0.5
    else:
        pluckR[i0:i0 + length] += tone
        pluckL[i0:i0 + length] += tone * 0.5
pluck_dyn = env_seg([(9.8, 0.0), (10.4, 0.5), (20.0, 0.62), (30.9, 0.72),
                     (34.8, 0.6), (35.2, 0.0)])
pluckL = hp(pluckL, 180) * pluck_dyn
pluckR = hp(pluckR, 180) * pluck_dyn

# ---------------------------------------------------------------- air shimmer
air = hp(rng.standard_normal(N), 6000)
air_dyn = env_seg([(0, 0.0), (2, 0.15), (9.8, 0.28), (30.9, 0.4),
                   (36, 0.25), (42, 0.0)])
air = air * air_dyn * (0.6 + 0.4 * np.sin(2 * np.pi * 0.1 * t))

# ---------------------------------------------------------------- risers
riser = np.zeros(N)


def add_riser(t0, t1, peak=1.0):
    i0, i1 = int(t0 * SR), int(t1 * SR)
    L = i1 - i0
    tt = np.arange(L) / SR
    ramp = (tt / (t1 - t0)) ** 2.2
    noise = rng.standard_normal(L)
    noise = noise * ramp
    # rising pitched sweep 240 -> 2600 Hz
    f = 240 * (2600 / 240) ** (tt / (t1 - t0))
    ph = 2 * np.pi * np.cumsum(f) / SR
    swoosh = 0.5 * np.sin(ph) * ramp
    seg = bp(noise, 700, 6500) + swoosh
    seg *= peak / (np.max(np.abs(seg)) + 1e-9)
    riser[i0:i1] += seg


add_riser(8.4, 9.9, 0.9)
add_riser(19.0, 20.4, 0.9)
add_riser(29.4, 30.9, 1.0)
add_riser(34.6, 35.9, 0.7)

# ---------------------------------------------------------------- impacts
impact = np.zeros(N)


def add_impact(t0, gain=1.0, tail=1.4):
    i0 = int(t0 * SR)
    L = int(tail * SR)
    if i0 + L > N:
        L = N - i0
    tt = np.arange(L) / SR
    # boom: pitch drops 95 -> 38 Hz in 160ms then holds
    fdrop = 38 + (95 - 38) * np.exp(-tt / 0.06)
    ph = 2 * np.pi * np.cumsum(fdrop) / SR
    boom = np.sin(ph) * np.exp(-tt / 0.5)
    # transient crack
    crack = hp(rng.standard_normal(L), 2500) * np.exp(-tt / 0.05) * 0.5
    seg = (boom + crack) * gain
    impact[i0:i0 + L] += seg[:L]


add_impact(0.42, 0.7, 1.6)
add_impact(9.9, 0.9)
add_impact(20.4, 0.95)
add_impact(30.9, 1.0)
add_impact(35.9, 1.05, 2.2)  # close hit, long tail

# ---------------------------------------------------------------- reverb (Schroeder)
def comb(x, delay_ms, g):
    d = int(delay_ms / 1000 * SR)
    y = np.zeros(len(x))
    buf = np.zeros(d)
    idx = 0
    # vector-friendly feedback comb
    b = [1.0]
    a = np.zeros(d + 1)
    a[0] = 1.0
    a[d] = -g
    return lfilter([1.0], a, x)


def allpass(x, delay_ms, g=0.7):
    d = int(delay_ms / 1000 * SR)
    a = np.zeros(d + 1)
    a[0] = 1.0
    a[d] = -g
    b = np.zeros(d + 1)
    b[0] = -g
    b[d] = 1.0
    return lfilter(b, a, x)


def reverb(x):
    c = (comb(x, 29.7, 0.78) + comb(x, 37.1, 0.74)
         + comb(x, 41.1, 0.71) + comb(x, 43.7, 0.68)) / 4.0
    c = allpass(c, 5.0, 0.7)
    c = allpass(c, 1.7, 0.7)
    return lp(c, 5500)


send = 0.55 * (padL + padR) * 0.5 + 0.6 * impact + 0.3 * riser
wetL = reverb(send * 1.0)
wetR = reverb(send * 0.94 + 0.05 * rng.standard_normal(N) * 0)

# ---------------------------------------------------------------- mix
L = (0.62 * padL + 0.9 * sub + 0.5 * pluckL + 0.12 * air
     + 0.55 * riser + 0.9 * impact + 0.26 * wetL)
R = (0.62 * padR + 0.9 * sub + 0.5 * pluckR + 0.12 * air
     + 0.55 * riser + 0.9 * impact + 0.26 * wetR)

# bus glue (soft saturation) + master


def master(x):
    x = np.tanh(x * 1.15) / 1.15
    x = hp(x, 28)          # clean rumble
    return x


L = master(L)
R = master(R)

# fades
fi = int(0.15 * SR)
fo = int(1.1 * SR)
fade_in = np.ones(N)
fade_in[:fi] = np.linspace(0, 1, fi)
fade_out = np.ones(N)
fade_out[-fo:] = np.linspace(1, 0, fo)
L *= fade_in * fade_out
R *= fade_in * fade_out

# peak normalize to -1 dBFS
pk = max(np.max(np.abs(L)), np.max(np.abs(R))) + 1e-9
target = 10 ** (-1.0 / 20)
L *= target / pk
R *= target / pk

stereo = np.stack([L, R], axis=1)
stereo_i16 = np.int16(np.clip(stereo, -1, 1) * 32767)
wavfile.write("assets/audio/score.wav", SR, stereo_i16)
rms = np.sqrt(np.mean(stereo ** 2))
print(f"wrote assets/audio/score.wav  dur={DUR}s  peak={20*np.log10(pk*target/pk):.2f}dB  rms={20*np.log10(rms+1e-9):.2f}dBFS")
"""
"""
