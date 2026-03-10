# DOCSIS 3.1 OFDM/OFDMA Throughput Estimator

A professional, browser-based calculator for estimating downstream OFDM and upstream OFDMA channel throughput based on the DOCSIS 3.1 Physical Layer Specification (CM-SP-PHYv3.1).

**Live demo:** [bradyvolpe.github.io/ofdmEstimator](https://bradyvolpe.github.io/ofdmEstimator/)

---

## Overview

DOCSIS 3.1 introduced OFDM (downstream) and OFDMA (upstream) as the foundational PHY technology for multi-gigabit cable broadband. Unlike legacy SC-QAM channels, OFDM/OFDMA channels carry hundreds to thousands of individually-modulated subcarriers, enabling adaptive modulation profiles, per-subcarrier exclusion, and dramatically higher spectral efficiency.

This estimator implements the key capacity equations from the DOCSIS 3.1 PHY spec, accounting for:

- Symbol timing (FFT period + cyclic prefix)
- PLC (Physical Layer Link Channel) subcarrier overhead
- Continuous pilots and scattered pilots
- LDPC FEC (code rate ≈ 0.877)
- NCP (Next Codeword Pointer) framing overhead
- Guard bands and exclusion notches

---

## Features

- **Self-contained, zero-dependency HTML** — works offline, deployable to GitHub Pages
- **OFDM Downstream tab** with real-time calculation
- **OFDMA Upstream tab** with minislot-based capacity model
- **Tooltips** on every parameter with spec references
- **Input validation** with clear error states
- **DOCSIS 3.1 Defaults** reset button
- **Professional dark UI** — Inter typography, dark `#0d1117` background

---

## Technical Background

### OFDM Downstream (CM-SP-PHYv3.1 §7)

| Parameter | Value |
|---|---|
| Max channel width | 192 MHz |
| Subcarrier spacing | 25 kHz or 50 kHz |
| FFT size | 4096 (50 kHz) or 8192 (25 kHz) points |
| Sample rate | 204.8 Msps |
| Symbol period (50 kHz) | 20 µs + CP |
| Cyclic prefix (typical) | 512 samples = 2.5 µs |
| Modulation | QPSK through 4096-QAM (2–12 bits/symbol) |
| LDPC codeword size | 16200 bits |
| LDPC info bits | 14216 bits (code rate ≈ 0.877) |
| PLC subcarriers | 8 (50 kHz) or 16 (25 kHz) |
| Continuous pilots | `clamp(⌈48 × BW / 190⌉, 8, 120) + 8` |
| Scattered pilots | 1 per 128 subcarriers |
| NCP modulation | 64-QAM (6 bits/symbol) |
| NCP size | 48 bits / 8 subcarriers per miniblock |

### OFDMA Upstream (CM-SP-PHYv3.1 §8)

| Parameter | Value |
|---|---|
| Max channel width | 96 MHz (low-split) to 684 MHz (ultra-high-split) |
| Subcarrier spacing | 6.25, 25, or 50 kHz |
| Sample rate | 102.4 Msps |
| Cyclic prefix (typical) | 192 samples = 1.875 µs |
| Minislot subcarriers (Q) | 8 (50 kHz) or 16 (25 kHz) |
| Symbols per minislot (K) | 36 (most common profile) |
| Modulation | QPSK through 4096-QAM |

---

## Key Formulas

### Downstream Throughput

```
T_sym   = 1 / f_sc                           (symbol period, µs)
T_cp    = N_cp / f_s                          (CP duration, µs)
T_total = T_sym + T_cp                        (total symbol period)

Active_SCs = (BW - Guard - Exclude) × 1000 / f_sc  (in kHz)
PLC_SCs    = 8  (50 kHz) or 16 (25 kHz)
Cont_pilots = clamp(⌈48 × BW_occ / 190⌉, 8, 120) + 8
Scat_pilots = ⌈(Active_SCs - PLC_SCs) / 128⌉
Eff_SCs     = Active_SCs - PLC_SCs - Cont_pilots - Scat_pilots

CW_full     = ⌊(Eff_SCs × mod) / 16200⌋
Info_bits   = CW_full × 14216 + shortened_CW_data
Throughput  = Info_bits / (T_total × 1000)   (Gbps)
```

### Upstream Throughput

```
Active_SCs    = BW × 1000 / f_sc - Guard_SCs - Exclude_SCs
Minislots     = ⌊Active_SCs / Q⌋ × efficiency_factor
Data_SCs/MS   = K × Q - pilot_overhead
Bits/MS       = Data_SCs/MS × mod
Throughput    = Minislots × Bits/MS / (K × T_total)  (Mbps)
```

---

## Accuracy Notes

The canonical downstream case — **192 MHz, 50 kHz spacing, 4096-QAM, 512-sample CP, 1 MHz guard, 0 excluded** — yields approximately **1.72 Gbps** with this model. This correctly accounts for:

- 3725 effective data subcarriers (after PLC, pilots, guard)
- 2 full LDPC codewords + 1 shortened codeword per symbol
- NCP framing overhead (8 subcarriers per codeword at 64-QAM)
- LDPC code rate of 14216/16200 ≈ 0.877

CableLabs occasionally cites ~1.89 Gbps in simplified capacity analyses. That figure omits NCP and LDPC overhead, treating the channel as raw modulation capacity. Our model is more conservative and reflects actual PHY behavior.

For reference: 3825 raw SCs × 12 bits × (1/22.5 µs) = **2.04 Gbps raw**, of which ~85% becomes payload after FEC and overhead — consistent with ~1.72 Gbps.

---

## Repository Structure

```
ofdmEstimator/
├── index.html          — Single-file DOCSIS 3.1 estimator (GitHub Pages)
├── README.md           — This file
├── reference/
│   ├── ofdm_estimation.py    — Python OFDM downstream backend (reference)
│   └── ofdma_estimation.py   — Python OFDMA upstream backend (reference)
└── LICENSE
```

---

## Author

**Brady Volpe, MSEE**  
[The Volpe Firm, Inc.](https://volpefirm.com) — DOCSIS, RF Engineering, Cable Broadband Consulting  
[brady.volpe@volpefirm.com](mailto:brady.volpe@volpefirm.com)

---

## Contributors

- Jason Patterson (RocNet Supply)
- Wesley Norris (@repnop)
- @snmpstack

---

## References

- CableLabs DOCSIS 3.1 Physical Layer Specification: CM-SP-PHYv3.1
- CableLabs DOCSIS 3.1 MAC and Upper Layer Protocols Interface Specification: CM-SP-MULPIv3.1
- [CableLabs Specifications](https://www.cablelabs.com/specifications/)

---

## License

MIT License

Copyright (c) 2024 Brady Volpe / The Volpe Firm, Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
