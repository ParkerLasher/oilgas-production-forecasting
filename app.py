import pandas as pd
import numpy as np
import streamlit as st

# --------- CONFIG ---------
CLEANED = "data/cleaned/us_oil_gas_cleaned.csv"
TITLE = "U.S. Federal Oil & Gas — Production & Disposition (2015–2025)"

@st.cache_data
def load_data(path):
    df = pd.read_csv(path, parse_dates=["production_date"])
    # Ensure expected columns exist
    expected = {"production_date","year","month","commodity","state","offshore_region",
                "disposition_code","disposition_description","volume"}
    missing = expected - set(df.columns)
    if missing:
        st.warning(f"Missing columns (ok if not applicable): {missing}")
    return df

def main():
    st.set_page_config(page_title="ONRR Oil & Gas Dashboard", layout="wide")
    st.title(TITLE)
    df = load_data(CLEANED)

    # --- Sidebar filters
    st.sidebar.header("Filters")
    years = sorted(df["year"].dropna().unique().tolist())
    year_range = st.sidebar.slider("Year range", int(min(years)), int(max(years)), (int(min(years)), int(max(years))))
    commodities = sorted(df["commodity"].dropna().unique().tolist())
    commodity_sel = st.sidebar.multiselect("Commodity", commodities, default=commodities)
    states = ["All"] + sorted(df["state"].dropna().unique().tolist())
    state_sel = st.sidebar.selectbox("State", states, index=0)
    show_withheld = st.sidebar.checkbox('Include "Withheld" state', value=True)

    # --- Apply filters
    m = (df["year"].between(year_range[0], year_range[1])) & (df["commodity"].isin(commodity_sel))
    if state_sel != "All":
        m &= (df["state"] == state_sel)
    if not show_withheld:
        m &= (df["state"].str.lower() != "withheld")
    dff = df.loc[m].copy()

    # --- KPI cards
    total_vol = dff["volume"].sum()
    neg_rows = int((dff["volume"] < 0).sum())
    pos_rows = int((dff["volume"] >= 0).sum())
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Volume (Filtered)", f"{total_vol:,.0f}")
    col2.metric("Rows ≥ 0", f"{pos_rows:,}")
    col3.metric("Rows < 0 (Adjustments)", f"{neg_rows:,}")

    # --- Charts
    st.subheader("Volume by Year")
    by_year = dff.groupby("year")["volume"].sum().reset_index()
    st.line_chart(by_year.set_index("year"))

    st.subheader("Volume by Year & Commodity")
    by_year_comm = dff.pivot_table(index="year", columns="commodity", values="volume", aggfunc="sum").fillna(0)
    st.line_chart(by_year_comm)

    colA, colB = st.columns(2)
    with colA:
        st.subheader("Top States by Total Volume")
        if "state" in dff:
            top_states = (dff[dff["state"].str.lower() != "withheld"]
                          .groupby("state")["volume"].sum().sort_values(ascending=False).head(12))
            st.bar_chart(top_states)
    with colB:
        st.subheader("Top Disposition Categories")
        if "disposition_description" in dff:
            top_disp = (dff.groupby("disposition_description")["volume"]
                          .sum().sort_values(ascending=False).head(12))
            st.bar_chart(top_disp)

    st.caption("Note: Negative volumes often reflect adjustments/true-ups in ONRR reporting.")

if __name__ == "__main__":
    main()
