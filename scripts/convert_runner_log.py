import argparse
import re
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--log", required=True)
parser.add_argument("--warmup", type=float, default=60)
args = parser.parse_args()

source = Path(args.log).expanduser().resolve()

if not source.is_file():
    parser.error(f"File not found: {source}")

pattern = re.compile(r"^(\d+(?:\.\d+)?)\s+(.*)$")

events = []

with source.open(encoding="utf-8", errors="replace") as f:
    for line in f:
        match = pattern.match(line.strip())
        if match:
            events.append((
                float(match.group(1)),
                match.group(2)
            ))

first_request = next(
    (
        t for t, message in events
        if "Sent NTPv" in message and "request" in message
    ),
    None
)

if first_request is None:
    raise SystemExit("ERROR: No NTP requests found in log")

output = source.with_name(
    source.parent.name + "_timed.log"
)

with output.open("w", encoding="utf-8") as f:
    for timestamp, message in events:
        elapsed = max(0.0, timestamp - first_request)

        phase = (
            "WARMUP"
            if elapsed < args.warmup
            else "MEASURE"
        )

        f.write(
            f"[{elapsed:.6f}] [{phase}] {message}\n"
        )

print("Converted:", output)
print("Events:", len(events))
print("Warm-up seconds:", args.warmup)
print("Reference: first logged NTP request")
