# COVID-19 India State Tracker

**Interactive data dashboard** built by Vasanth A (AI & Data Science, 2026 batch)

## What it does
- State-wise confirmed, recovered, death, active case rankings with interactive bar charts
- Wave analysis — visualises Wave 1, Wave 2 (Delta), Wave 3 (Omicron) with moving average overlay
- State deep-dive — donut breakdown, CFR, recovery rate, national rank for any state
- Insights dashboard — key findings, CFR comparison, data commentary

## Tech stack
| Layer | Tool |
|---|---|
| Frontend | Streamlit |
| Charts | Plotly Express + Graph Objects |
| Data | pandas, numpy |
| Deploy | Render.com (free) or Streamlit Cloud |

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy to Streamlit Cloud (2 minutes)
1. Push folder to GitHub repo `covid-india-tracker`
2. Go to share.streamlit.io → connect repo → select app.py → Deploy
3. Live URL: `vasanth-covid-india.streamlit.app`

## Upgrade with real data (bonus)
```python
import requests
URL = "https://data.covid19india.org/v4/min/timeseries.min.json"
data = requests.get(URL).json()
```
Connect this API for fully live, auto-updating data — impressive for interviews.

## Resume line
> "Built an interactive COVID-19 India State Tracker — wave analysis across 3 surges, state-wise CFR, Plotly choropleth maps — deployed live at [url]"
