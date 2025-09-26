# U.S. Federal Oil & Gas Analysis & Forecasting (2015–2025)

# Exploratory Data Analysis & Forecasting
This notebook combines EDA (Step 3) and Forecasting (Step 4).  
Normally, these might be split into separate notebooks, but here they are kept together for narrative flow.

---

### Deliverables
- **Jupyter Notebooks** → Contain the full technical workflow (data cleaning, EDA, and Prophet forecasting). These are intended for a technical audience who want to see the methodology and modeling steps.  
- **Streamlit Dashboard** → Provides an interactive, business-friendly tool to explore historical trends by year, commodity, state, and disposition category. Forecasting results are kept in the notebooks, since they are more technical and model-driven.

---

## 📌 Overview
This project analyzes and forecasts **U.S. federal oil and natural gas production** using official data from the U.S. Department of the Interior’s Office of Natural Resources Revenue (ONRR).

The workflow demonstrates the full data science lifecycle:
1. **Data Cleaning** — Preparing raw ONRR monthly production & disposition data.
2. **Exploratory Data Analysis (EDA)** — Visualizing trends by year, commodity, state, offshore region, and disposition category.
3. **Forecasting** — Using Facebook **Prophet** to project monthly production volumes into 2027.
4. **Dashboarding** — Interactive **Streamlit app** for non-technical users to explore the data and forecasts.

This project is designed to showcase end-to-end **data engineering, analytics, and machine learning** skills relevant to real-world business scenarios.

---

## 🗂️ Dataset
- **Source**: [ONRR Monthly Production Disposition Data](https://www.onrr.gov/)  
- **Coverage**: 2015–2025, federal lands, offshore regions, and Native American lands (location withheld for privacy).  
- **License**: Public domain (CC0).  
- **Size**: ~90 MB raw CSVs → ~45 MB cleaned CSV.

---

## ⚙️ Tech Stack
- **Languages**: Python (Pandas, NumPy, Matplotlib, Seaborn)  
- **Modeling**: Facebook Prophet (time series forecasting)  
- **Dashboard**: Streamlit  
- **Environment**: Conda + Jupyter Notebook  
- **Version Control**: Git & GitHub  

---

## Distribution of Reported Volumes (Univariate EDA)
Note: Most reported volumes cluster near zero, which creates a skewed distribution. This motivated deeper analysis by commodity and geography (see charts below).

---

## 📊 Project Structure
oil-analysis/
├── notebooks/
│ ├── datacleaner.ipynb # Data cleaning logic
│ ├── dataAnalysis.ipynb # Exploratory Data Analysis + Prophet forecasting
│ └── 04_forecasting.ipynb # Prophet forecasting
├── app.py # Streamlit dashboard
├── data/
│ ├── raw/ # Original ONRR CSVs
│ └── cleaned/ # Cleaned dataset
├── README.md # Project documentation
└── requirements.txt # Dependencies

---

## 🚀 How to Run

### 1. Clone the repo
```bash```
git clone https://github.com/<your-username>/oilgas-analysis.git
cd oilgas-analysis

### 2. Setting up environment
conda create -n oilgas python=3.11 -y
conda activate oilgas
pip install -r requirements.txt

### Run Notebooks
Launch Jupyter and open notebooks inside notebooks/:
jupyter lab

### Run Dashboard
streamlit run app.py

### Open Browser
http://localhost:8501










