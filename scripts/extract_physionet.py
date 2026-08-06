"""Build compact browser-ready reference strips from PhysioNet MIT-BIH records."""
import json
import numpy as np
import wfdb

CASES = {
    "sinus": ("100", 0, "MIT-BIH 100 · MLII"),
    "af": ("202", 18 * 60 + 59, "MIT-BIH 202 · AF onset · MLII"),
    "flutter": ("202", 25 * 60 + 58, "MIT-BIH 202 · atrial flutter · MLII"),
    "vt": ("203", 5 * 60, "MIT-BIH 203 · ventricular tachycardia · MLII"),
}

output = {}
for key, (record_name, start_seconds, label) in CASES.items():
    fs = 360
    record = wfdb.rdrecord(
        record_name,
        sampfrom=int(start_seconds * fs),
        sampto=int((start_seconds + 8) * fs),
        channels=[0],
        pn_dir="mitdb",
    )
    signal = record.p_signal[:, 0]
    signal = signal - np.median(signal)
    scale = np.percentile(np.abs(signal), 98) or 1
    signal = np.clip(signal / scale, -1.35, 1.35)
    # 120 Hz is sufficient for a compact educational monitor strip.
    signal = signal[::3]
    output[key] = {"fs": 120, "label": label, "samples": np.round(signal, 4).tolist()}

with open("docs/real-signals.js", "w", encoding="utf-8", newline="\n") as handle:
    handle.write("window.REAL_ECG=")
    json.dump(output, handle, ensure_ascii=False, separators=(",", ":"))
    handle.write(";\n")
