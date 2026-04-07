"""
parse_workout.py
Parses shorthand workout .txt files in logs/raw/ into JSON in logs/json/.

Handles both STRENGTH and ENDURANCE (RUN) formats for SPARTAN.

Strength Format:
  2026-03-24 | 1 | accumulation | Optional notes here
  Squat: 100x5, 100x5, 102.5x5

Run Format:
  2026-04-07 | run | interval | Optional notes here
  5mi | 45:30 | 9:06/mi | 155bpm
  Intervals: 8x400m @ 6:00/mi pace, 60s rest
"""

import json
import sys
from pathlib import Path

RAW_DIR = Path("logs/raw")
JSON_DIR = Path("logs/json")
JSON_DIR.mkdir(parents=True, exist_ok=True)

def parse_set(set_str: str) -> dict:
    set_str = set_str.strip()
    if "x" not in set_str:
        raise ValueError(f"Invalid set '{set_str}' — expected weightxreps e.g. 100x5")
    weight_str, reps_str = set_str.split("x", 1)
    return {
        "weight_kg": float(weight_str.strip()),
        "reps": int(reps_str.strip())
    }

def group_consecutive_sets(sets: list) -> list:
    if not sets:
        return []
    grouped = []
    current = dict(sets[0])
    run = 1
    for s in sets[1:]:
        if s["weight_kg"] == current["weight_kg"] and s["reps"] == current["reps"]:
            run += 1
        else:
            entry = {"weight_kg": current["weight_kg"], "reps": current["reps"]}
            if run > 1:
                entry["count"] = run
            grouped.append(entry)
            current = dict(s)
            run = 1
    entry = {"weight_kg": current["weight_kg"], "reps": current["reps"]}
    if run > 1:
        entry["count"] = run
    grouped.append(entry)
    return grouped

def parse_exercise_line(line: str) -> dict:
    if ":" not in line:
        raise ValueError(f"Exercise line missing colon: '{line}'")
    name, sets_str = line.split(":", 1)
    raw_sets = [parse_set(s) for s in sets_str.split(",") if s.strip()]
    if not raw_sets:
        raise ValueError(f"No sets found for '{name.strip()}'")
    grouped = group_consecutive_sets(raw_sets)
    return {"name": name.strip(), "sets": grouped}

def parse_run_body(lines: list) -> dict:
    if not lines:
        return {"distance": "", "time": "", "pace": "", "hr": "", "intervals": []}
    
    # First line of body represents core metrics split by pipe
    metrics_line = lines[0]
    metrics = [m.strip() for m in metrics_line.split("|")]
    
    distance = metrics[0] if len(metrics) > 0 else ""
    time = metrics[1] if len(metrics) > 1 else ""
    pace = metrics[2] if len(metrics) > 2 else ""
    hr = metrics[3] if len(metrics) > 3 else ""
    
    # Any subsequent lines are saved as details/intervals
    intervals = []
    if len(lines) > 1:
        intervals = [l.strip() for l in lines[1:] if l.strip()]
        
    return {
        "distance": distance,
        "time": time,
        "pace": pace,
        "hr": hr,
        "intervals": intervals
    }

def parse_workout(text: str) -> dict:
    lines = [l.strip() for l in text.strip().splitlines() if l.strip()]
    if not lines:
        raise ValueError("Empty document")

    parts = [p.strip() for p in lines[0].split("|")]
    if len(parts) < 3:
        raise ValueError(f"Header requires at least 3 segments separated by pipe.\nGot: {lines[0]}")

    date = parts[0]
    is_run = parts[1].lower() == "run"

    if is_run:
        run_type = parts[2]
        notes = parts[3] if len(parts) > 3 else ""
        
        body_data = parse_run_body(lines[1:])
        return {
            "date": date,
            "type": "run",
            "run_type": run_type,
            "notes": notes,
            **body_data
        }
    else:
        week = int(parts[1])
        phase = parts[2]
        notes = parts[3] if len(parts) > 3 else ""

        exercises = []
        errors = []
        for line in lines[1:]:
            if not line or line.startswith("#"):
                continue
            try:
                exercises.append(parse_exercise_line(line))
            except Exception as e:
                errors.append(f"  '{line}': {e}")

        if errors:
            raise ValueError("Parse errors:\n" + "\n".join(errors))

        return {
            "date": date, 
            "type": "weights", 
            "week": week, 
            "phase": phase, 
            "notes": notes, 
            "exercises": exercises
        }

def main():
    raw_files = sorted(RAW_DIR.glob("*.txt"))
    if not raw_files:
        print("No .txt files found in logs/raw/")
        return

    parsed = skipped = errors = 0
    force = "--force" in sys.argv

    for txt_path in raw_files:
        json_path = JSON_DIR / (txt_path.stem + ".json")
        if json_path.exists() and not force:
            skipped += 1
            continue

        print(f"Parsing {txt_path.name}...")
        try:
            text = txt_path.read_text(encoding="utf-8")
            workout = parse_workout(text)
            json_path.write_text(json.dumps(workout, indent=2), encoding="utf-8")
            print(f"  ✓ {json_path.name}")
            parsed += 1
        except Exception as e:
            print(f"  ✗ Error: {e}", file=sys.stderr)
            errors += 1

    print(f"\nParsed: {parsed}  Skipped: {skipped}  Errors: {errors}")
    if errors:
        sys.exit(1)

if __name__ == "__main__":
    main()