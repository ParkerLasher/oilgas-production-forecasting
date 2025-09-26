import pandas as pd
import numpy as np

def clean_onrr(path_in: str) -> pd.DataFrame:
    df = pd.read_csv(path_in)
    df.columns = (df.columns.str.strip().str.lower()
                  .str.replace(" ", "_").str.replace("/", "_").str.replace("-", "_"))
    df["production_date"] = pd.to_datetime(df["production_date"], errors="coerce")
    df["year"]  = df["production_date"].dt.year
    df["month"] = df["production_date"].dt.month
    for col in ["state","county"]:
        if col in df.columns:
            df[col] = df[col].fillna("Withheld")
    # normalize categoricals
    for c in df.select_dtypes(include="object").columns:
        df[c] = df[c].apply(lambda x: x.strip().title() if isinstance(x,str) else x)
    # numeric fields
    for c in ["fips_code","disposition_code","volume"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c].astype(str).str.replace(",","").str.strip(), errors="coerce")
    return df
