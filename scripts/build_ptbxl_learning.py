#!/usr/bin/env python3
"""Build a browser-friendly ECG learning JSON from PTB-XL and ECG-QA.

Required inputs:
  --ptbxl-dir: PTB-XL root containing ptbxl_database.csv and scp_statements.csv
  --ecgqa-dir: ECG-QA ptbxl directory containing template/paraphrased JSON files

Optional waveform export requires wfdb and the PTB-XL records100/records500 files.
The script does not redistribute raw PTB-XL signals; it writes mapped metadata and
optionally down-sampled waveform points for records available on the local machine.
"""
from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path
from typing import Any

import pandas as pd


def load_qa(ecgqa_dir: Path, split: str, question_set: str) -> list[dict[str, Any]]:
    pattern = ecgqa_dir / question_set / split / "*.json"
    rows: list[dict[str, Any]] = []
    for filename in sorted(glob.glob(str(pattern))):
        with open(filename, encoding="utf-8") as handle:
            rows.extend(json.load(handle))
    return rows


def read_waveform(record_path: Path, max_points: int) -> dict[str, Any] | None:
    try:
        import numpy as np
        import wfdb
    except ImportError:
        return None
    try:
        record = wfdb.rdrecord(str(record_path))
        signal = record.p_signal
        if signal is None or signal.size == 0:
            return None
        lead_names = list(record.sig_name)
        lead_index = lead_names.index("II") if "II" in lead_names else 0
        y = signal[:, lead_index]
        indexes = np.linspace(0, len(y) - 1, min(max_points, len(y))).astype(int)
        sampled = y[indexes]
        finite = sampled[np.isfinite(sampled)]
        if finite.size == 0:
            return None
        sampled = np.nan_to_num(sampled, nan=float(np.median(finite)))
        return {
            "lead": lead_names[lead_index],
            "sampling_rate": int(record.fs),
            "points": [round(float(value), 5) for value in sampled],
        }
    except Exception as exc:  # one malformed record must not stop the build
        print(f"waveform skipped: {record_path}: {exc}")
        return None


def build(args: argparse.Namespace) -> None:
    ptbxl_dir = Path(args.ptbxl_dir).expanduser().resolve()
    ecgqa_dir = Path(args.ecgqa_dir).expanduser().resolve()
    database = pd.read_csv(ptbxl_dir / "ptbxl_database.csv", index_col="ecg_id")
    qa_rows = load_qa(ecgqa_dir, args.split, args.question_set)

    output: list[dict[str, Any]] = []
    seen: set[tuple[int, int]] = set()
    for qa in qa_rows:
        ecg_ids = qa.get("ecg_id") or []
        if len(ecg_ids) != 1 or not ecg_ids[0] in database.index:
            continue
        ecg_id = int(ecg_ids[0])
        key = (ecg_id, int(qa.get("question_id", -1)))
        if key in seen:
            continue
        seen.add(key)
        row = database.loc[ecg_id]
        filename = row.get("filename_hr" if args.resolution == 500 else "filename_lr")
        item: dict[str, Any] = {
            "id": f"ptbxl-{ecg_id}-{qa.get('sample_id', len(output))}",
            "source": "PTB-XL + ECG-QA",
            "ecg_id": ecg_id,
            "question": qa.get("question", ""),
            "answers": qa.get("answer", []),
            "attribute_type": qa.get("attribute_type"),
            "attributes": qa.get("attribute") or [],
            "scp_codes": row.get("scp_codes", "{}"),
            "record_path": str(filename),
        }
        if args.include_waveforms and filename:
            waveform = read_waveform(ptbxl_dir / str(filename), args.max_points)
            if waveform:
                item["waveform"] = waveform
        output.append(item)
        if len(output) >= args.limit:
            break

    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {len(output)} mapped records to {destination}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ptbxl-dir", required=True)
    parser.add_argument("--ecgqa-dir", required=True)
    parser.add_argument("--output", default="data/ptbxl-mapped.json")
    parser.add_argument("--split", choices=["train", "valid", "test"], default="test")
    parser.add_argument("--question-set", choices=["template", "paraphrased"], default="template")
    parser.add_argument("--resolution", choices=[100, 500], type=int, default=100)
    parser.add_argument("--limit", type=int, default=500)
    parser.add_argument("--max-points", type=int, default=1200)
    parser.add_argument("--include-waveforms", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    build(parse_args())
