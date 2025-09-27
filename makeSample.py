import os
import pandas as pd

# -----------------------------
# SETTINGS (edit these easily)
# -----------------------------
SRC = "data/cleaned/us_oil_gas_cleaned_full_size.csv"   # full cleaned dataset
OUT = "data/us_oil_gas_cleaned.csv" # sample output file
TARGET_ROWS = 240000                           # <-- change this to adjust size
RANDOM_STATE = 42                             # reproducibility

# -----------------------------
# BUILD SAMPLE
# -----------------------------
assert os.path.exists(SRC), f"❌ Source file not found: {SRC}"
df = pd.read_csv(SRC, parse_dates=["production_date"])

# Ensure year column exists
if "year" not in df.columns:
    if "production_date" in df.columns:
        df["year"] = df["production_date"].dt.year
    else:
        raise ValueError("No 'year' or 'production_date' column found in source CSV.")

years = sorted(df["year"].dropna().unique().tolist())
if not years:
    raise ValueError("No valid years found in source CSV.")

# Evenly sample rows per year
per_year = max(1, TARGET_ROWS // len(years))
parts = []
for y in years:
    g = df[df["year"] == y]
    if len(g) <= per_year:
        take = g
    else:
        take = g.sample(n=per_year, random_state=RANDOM_STATE)
    parts.append(take)

sample = pd.concat(parts, axis=0).sort_values("production_date")

# Trim if slightly over target
if len(sample) > TARGET_ROWS:
    sample = sample.sample(n=TARGET_ROWS, random_state=RANDOM_STATE).sort_values("production_date")

# Save
os.makedirs(os.path.dirname(OUT), exist_ok=True)
sample.to_csv(OUT, index=False)

print(f"✅ Wrote {OUT} with {len(sample):,} rows across {len(years)} years")
