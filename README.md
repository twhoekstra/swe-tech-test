# SWE Tech Test — Mock Recording

See `TEST_DESCRIPTION.md` for the exercise brief.

The mock recording is not included. Generate it locally with:

```bash
pip install zarr numpy
python generate_mock_recording.py
```

Output: `./mock48_2500hz_1.5h.zarr` — a **Zarr v3** directory store,
48 channels × 2.5 kHz × 1.5 h (= 13,500,000 samples per channel), `int16`.
Generation takes ~1 min on an M-series Mac.

## What's in the file

### Structure

```
mock48_2500hz_1.5h.zarr/
├── zarr.json               # group metadata + root attrs (see below)
├── current_data/           # (48, 13_500_000) int16 — ADC counts
└── voltage_data/           # (48, 13_500_000) int16 — ADC counts
```

### Root attributes

| Attr | Value | Meaning |
|---|---|---|
| `device_id` | `mock-48ch-001` | |
| `number_of_channels` | `48` | |
| `sample_rate_hz` | `2500.0` | |
| `duration_sec` | `5400` | = 1.5 h (13,500,000 samples per channel) |
| `current_units` | `"pA"` | |
| `current_range` | `2.0` | ± 2 nA full scale |
| `current_scale` | `0.061035…` | **pA per int16 unit** (= 2 nA / 32768) |
| `current_offset` | `0` | |
| `voltage_scale` | `0.0625` | **mV per int16 unit** |
| `voltage_offset` | `0` | |

To convert raw counts to physical units:
```python
current_pA = current_data[ch, a:b].astype("float32") * 0.06103515625
voltage_mV = voltage_data[ch, a:b].astype("float32") * 0.0625
```

## Reading the file

zarr-python:
```python
import zarr, numpy as np
f = zarr.open("mock48_2500hz_1.5h.zarr", mode="r")
pA = f["current_data"][0, 0:25000].astype("float32") * f.attrs["current_scale"]
```
