"""
parse_workout.py
Scans logs/raw/*.txt for any files that don't yet have a corresponding
logs/json/*.json, parses them, and writes the JSON output.

Shorthand format:
  2026-03-24 | 1 | accumulation | 7 | Felt good, knee fine
  Squat: 100x5@8, 100x5@8.5, 102.5x5@9
  RDL: 80x8@7, 80x8@7.5
  Bench: 80x5@7, 82.5x5@8

Header fields (pipe-separated):
  date | week | phase | session_rpe | notes

Exercise lines:
  ExerciseName: weightxreps@rpe, ...
  - weight in kg (decimals allowed e.g. 102.5)
  - reps as integer
  - @rpe is optional (omit if not tracking per set)
"""

import json
import re
import sys
from pathlib import Path

RAW_DIR = Path("logs/raw")
JSON_DIR = Path("logs/json")
JSON_DIR.mkdir(parents=True, exist_ok=True)


def parse_set(set_str: str) -> dict:
    """Parse a single set string like '100x5@8.5' into a dict."""
    set_str = set_str.strip()
    rpe = None
    if "@" in set_str:
        set_str, rpe_str = set_str.split("@", 1)
        rpe = float(rpe_str)
    if "x" not in set_str:
        raise ValueError(f"Invalid set format: '{set_str}' — expected weightxreps")
    weight_str, reps_str = set_str.split("x", 1)
    return {
        "weight_kg": float(weight_str),
        "reps": int(reps_str),
        **({"rpe": rpe} if rpe is not None else {})
    }


def parse_exercise_line(line: str) -> dict:
    """Parse 'Squat: 100x5@8, 100x5@9' into an exercise dict."""
    name, sets_str = line.split(":", 1)
    sets = [parse_set(s) for s in sets_str.split(",") if s.strip()]
    return {"name": name.strip(), "sets": sets}


def parse_workout(text: str) -> dict:
    """Parse a full shorthand workout text block into a workout dict."""
    lines = [l.strip() for l in text.strip().splitlines() if l.strip()]
    if not lines:
        raise ValueError("Empty workout text")

    # --- Header ---
    header_parts = [p.strip() for p in lines[0].split("|")]
    if len(header_parts) < 4:
        raise ValueError(
            f"Header must have at least 4 pipe-separated fields: "
            f"date | week | phase | session_rpe | notes(optional)\n"
            f"Got: {lines[0]}"
        )

    date = header_parts[0]
    week = int(header_parts[1])
    phase = header_parts[2]
    session_rpe = float(header_parts[3])
    notes = header_parts[4] if len(header_parts) > 4 else ""

    # --- Exercises ---
    exercises = []
    errors = []
    for line in lines[1:]:
        if not line or line.startswith("#"):
            continue
        try:
            exercises.append(parse_exercise_line(line))
        except Exception as e:
            errors.append(f"  Line '{line}': {e}")

    if errors:
        raise ValueError("Exercise parse errors:\n" + "\n".join(errors))

    return {
        "date": date,
        "week": week,
        "phase": phase,
        "session_rpe": session_rpe,
        "notes": notes,
        "exercises": exercises
    }


def main():
    raw_files = list(RAW_DIR.glob("*.txt"))
    if not raw_files:
        print("No raw .txt files found in logs/raw/")
        return

    parsed_count = 0
    skipped_count = 0
    error_count = 0

    for txt_path in sorted(raw_files):
        json_path = JSON_DIR / (txt_path.stem + ".json")
        if json_path.exists():
            skipped_count += 1
            continue

        print(f"Parsing {txt_path.name}...")
        try:
            text = txt_path.read_text(encoding="utf-8")
            workout = parse_workout(text)
            json_path.write_text(
                json.dumps(workout, indent=2, ensure_ascii=False),
                encoding="utf-8"
            )
            print(f"  ✓ Written to {json_path}")
            parsed_count += 1
        except Exception as e:
            print(f"  ✗ Error: {e}", file=sys.stderr)
            error_count += 1

    print(f"\nDone. Parsed: {parsed_count}, Skipped: {skipped_count}, Errors: {error_count}")
    if error_count:
        sys.exit(1)


if __name__ == "__main__":
    main()
