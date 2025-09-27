import os
import pandas as pd
import numpy as np
import streamlit as st

# ---------- CONFIG ----------
TITLE = "U.S. Federal Oil & Gas — Production & Disposition (2015–2025)"
CANDIDATES = [
    # Prefer stratified sample first (best UX on Streamlit Cloud)
    "data/sample_us_oil_gas_stratified_10k.csv",
    # Other sample sizes (optional)
    "data/sample_us_oil_gas_10000.csv",
    "data/sample_us_oil_gas_24000.csv",
    "data/sample_us_oil_gas_1000.csv",
    # Full cleaned dataset last (if present locally)
    "data/cleaned/us_oil_gas_cleaned.csv",
]

@st.cache_data
def first_existing(paths):
    for p in paths:
        if os.path.exists(p):
            return p
    raise FileNotFoundError(
        "No data file found. Add a sample CSV under data/ (e.g., sample_us_oil_gas_stratified_10k.csv)."
    )

@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    # Parse date if present; if not, we’ll try to infer year from columns
    parse_cols = ["production_date"] if "production_date" in pd.read_csv(path, nrows=0).columns else None
    df = pd.read_csv(path, parse_dates=parse_cols)
    # Ensure expected columns exist (gracefully degrade if not)
    if "year" not in df.columns:
        if "production_date" in df.columns:
            df["year"] = df["production_date"].dt.year
        else:
            st.warning("No 'year' or 'production_date' column found; creating a dummy year from index.")
            df["year"] = 2015
    # Fill missing essentials
    for col, default in [
        ("commodity", "Unknown"),
        ("state", "Unknown"),
        ("offshore_region", "Unknown"),
        ("disposition_code", "Unknown"),
        ("disposition_description", "Unknown"),
    ]:
        if col not in df.columns:
            df[col] = default
    if "volume" not in df.columns:
        st.error("Missing required 'volume' column.")
    return df

def main():
    st.set_page_config(page_title="ONRR Oil & Gas Dashboard", layout="wide")
    st.title(TITLE)

    data_path = first_existing(CANDIDATES)
    st.caption(f"Loaded data from: `{data_path}`")
    df = load_data(data_path)

    # ---------- Sidebar filters ----------
    st.sidebar.header("Filters")

    years = sorted([int(y) for y in df["year"].dropna().unique().tolist()])
    if len(years) >= 2 and min(years) < max(years):
        year_range = st.sidebar.slider(
            "Year range",
            int(min(years)),
            int(max(years)),
            (int(min(years)), int(max(years))),
        )
    else:
        only_year = years[0] if years else 2015
        st.sidebar.info(f"Only one year present in dataset: {only_year}")
        _ = st.sidebar.selectbox("Year", [only_year], index=0)
        year_range = (only_year, only_year)

    commodities = sorted(df["commodity"].dropna().unique().tolist())
    commodity_sel = st.sidebar.multiselect("Commodity", commodities, default=commodities)

    states = ["All"] + sorted(df["state"].dropna().unique().tolist())
    state_sel = st.sidebar.selectbox("State", states, index=0)

    show_withheld = st.sidebar.checkbox('Include "Withheld" state', value=True)

    # ---------- Apply filters ----------
    mask = df["year"].between(year_range[0], year_range[1]) & df["commodity"].isin(commodity_sel)
    if state_sel != "All":
        mask &= df["state"] == state_sel
    if not show_withheld:
        # handle missing safely
        mask &= df["state"].fillna("").str.lower() != "withheld"

    dff = df.loc[mask].copy()

    # ---------- KPI cards ----------
    total_vol = float(dff["volume"].sum()) if "volume" in dff else 0.0
    neg_rows = int((dff["volume"] < 0).sum()) if "volume" in dff else 0
    pos_rows = int((dff["volume"] >= 0).sum()) if "volume" in dff else 0

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Volume (Filtered)", f"{total_vol:,.0f}")
    c2.metric("Rows ≥ 0", f"{pos_rows:,}")
    c3.metric("Rows < 0 (Adjustments)", f"{neg_rows:,}")

    # ---------- Charts ----------
    st.subheader("Volume by Year")
    if {"year", "volume"}.issubset(dff.columns):
        by_year = dff.groupby("year", as_index=False)["volume"].sum()
        if not by_year.empty:
            st.line_chart(by_year.set_index("year"))
        else:
            st.info("No data in selected filters to show by-year chart.")
    else:
        st.warning("Missing 'year' or 'volume' to draw by-year chart.")

    st.subheader("Volume by Year & Commodity")
    if {"year", "commodity", "volume"}.issubset(dff.columns):
        by_year_comm = (
            dff.pivot_table(index="year", columns="commodity", values="volume", aggfunc="sum")
            .fillna(0)
            .sort_index()
        )
        if not by_year_comm.empty:
            st.line_chart(by_year_comm)
        else:
            st.info("No data in selected filters for year & commodity.")
    else:
        st.warning("Missing columns to draw year & commodity chart.")

    colA, colB = st.columns(2)

    with colA:
        st.subheader("Top States by Total Volume")
        if {"state", "volume"}.issubset(dff.columns):
            top_states = (
                dff[dff["state"].fillna("").str.lower() != "withheld"]
                .groupby("state", as_index=False)["volume"]
                .sum()
                .sort_values("volume", ascending=False)
                .head(12)
                .set_index("state")["volume"]
            )
            if not top_states.empty:
                st.bar_chart(top_states)
            else:
                st.info("No state data to display.")
        else:
            st.warning("Missing 'state' or 'volume' columns.")

    with colB:
        st.subheader("Top Disposition Categories")
        if {"disposition_description", "volume"}.issubset(dff.columns):
            top_disp = (
                dff.groupby("disposition_description", as_index=False)["volume"]
                .sum()
                .sort_values("volume", ascending=False)
                .head(12)
                .set_index("disposition_description")["volume"]
            )
            if not top_disp.empty:
                st.bar_chart(top_disp)
            else:
                st.info("No disposition data to display.")
        else:
            st.warning("Missing 'disposition_description' or 'volume' columns.")

    st.caption("Note: Negative volumes often reflect adjustments/true-ups in ONRR reporting.")

if __name__ == "__main__":
    main()
