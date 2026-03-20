import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="COVID-19 India Tracker",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .metric-card{background:#f8f9fa;border-radius:12px;padding:1rem;text-align:center;border:1px solid #e9ecef}
    .big-num{font-size:1.8rem;font-weight:700;font-family:monospace}
    .red{color:#E24B4A}.green{color:#1D9E75}.gray{color:#888780}.amber{color:#EF9F27}
    div[data-testid="metric-container"]{background:#f8f9fa;border-radius:12px;padding:0.8rem;border:1px solid #e9ecef}
    .stPlotlyChart{border-radius:12px;overflow:hidden}
</style>
""", unsafe_allow_html=True)

# ── Data ──────────────────────────────────────────────────────
STATE_DATA = {
    'Maharashtra':   {'confirmed':7924032,'recovered':7837681,'deaths':147855,'active':38496},
    'Kerala':        {'confirmed':6670934,'recovered':6614447,'deaths':70106, 'active':86381},
    'Karnataka':     {'confirmed':3985369,'recovered':3945052,'deaths':40197, 'active':120},
    'Tamil Nadu':    {'confirmed':3462736,'recovered':3427781,'deaths':38025, 'active':930},
    'Delhi':         {'confirmed':1985077,'recovered':1963420,'deaths':26521, 'active':1136},
    'Uttar Pradesh': {'confirmed':2094072,'recovered':2063937,'deaths':23693, 'active':442},
    'Andhra Pradesh':{'confirmed':2325484,'recovered':2300069,'deaths':14740, 'active':675},
    'West Bengal':   {'confirmed':2112278,'recovered':2091508,'deaths':21213, 'active':1557},
    'Rajasthan':     {'confirmed':1296154,'recovered':1284891,'deaths':9941,  'active':1322},
    'Gujarat':       {'confirmed':1245582,'recovered':1230817,'deaths':10942, 'active':1823},
    'Madhya Pradesh':{'confirmed':1043091,'recovered':1032891,'deaths':10736, 'active':464},
    'Bihar':         {'confirmed':838087, 'recovered':833012, 'deaths':12253, 'active':822},
    'Chhattisgarh':  {'confirmed':1163289,'recovered':1149621,'deaths':13618, 'active':50},
    'Haryana':       {'confirmed':1046380,'recovered':1035261,'deaths':10669, 'active':450},
    'Odisha':        {'confirmed':1283919,'recovered':1273944,'deaths':9141,  'active':834},
    'Telangana':     {'confirmed':827374, 'recovered':820310, 'deaths':4111,  'active':953},
    'Jharkhand':     {'confirmed':437718, 'recovered':432745, 'deaths':5289,  'active':284},
    'Assam':         {'confirmed':724980, 'recovered':718012, 'deaths':6895,  'active':273},
    'Punjab':        {'confirmed':761733, 'recovered':747527, 'deaths':17848, 'active':358},
    'Himachal Pradesh':{'confirmed':296416,'recovered':293127,'deaths':4196,  'active':93},
}

df = pd.DataFrame(STATE_DATA).T.reset_index()
df.columns = ['State','Confirmed','Recovered','Deaths','Active']
df['CFR'] = (df['Deaths'] / df['Confirmed'] * 100).round(2)
df['Recovery Rate'] = (df['Recovered'] / df['Confirmed'] * 100).round(2)

def gen_wave_data(state='India'):
    scale = 1000000 if state=='India' else {'Maharashtra':250000,'Kerala':200000,'Karnataka':90000,
        'Tamil Nadu':85000,'Delhi':120000,'Uttar Pradesh':60000,'West Bengal':65000}.get(state,50000)
    months = pd.date_range('2020-03-01', periods=28, freq='MS')
    w1 = np.array([max(0, scale*np.exp(-0.5*((i-6)*0.6)**2)) if 2<=i<=8 else 0 for i in range(28)])
    w2 = np.array([max(0, scale*2.8*np.exp(-0.5*((i-16)*0.6)**2)) if 10<=i<=18 else 0 for i in range(28)])
    w3 = np.array([max(0, scale*1.5*np.exp(-0.5*((i-22)*0.7)**2)) if 20<=i<=26 else 0 for i in range(28)])
    total = w1 + w2 + w3
    ma = pd.Series(total).rolling(3, min_periods=1).mean().values
    return pd.DataFrame({'Date':months,'Wave1':w1.astype(int),'Wave2':w2.astype(int),
                         'Wave3':w3.astype(int),'Total':total.astype(int),'MA7':ma.astype(int)})

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## COVID-19 India Tracker")
    st.markdown("**Built by:** Vasanth A  \n**Stack:** Python · Pandas · Plotly · Streamlit")
    st.divider()
    metric = st.selectbox("Primary metric", ['Confirmed','Recovered','Deaths','Active','CFR','Recovery Rate'])
    selected_states = st.multiselect("Filter states", df['State'].tolist(), default=df['State'].tolist()[:10])
    st.divider()
    st.markdown("""
**Data source:** [covid19india.org](https://covid19india.org)  
**Period:** March 2020 – March 2022  
**GitHub:** [github.com/vasanth-a](https://github.com)
    """)

# ── Header ────────────────────────────────────────────────────
st.title("🇮🇳 COVID-19 India State Tracker")
st.caption("Interactive state-wise dashboard · Wave analysis · Case fatality trends · 2020–2022")

# ── KPIs ──────────────────────────────────────────────────────
c1,c2,c3,c4,c5 = st.columns(5)
c1.metric("Total Confirmed", "4.47 Cr", delta=None)
c2.metric("Total Recovered", "4.42 Cr", "98.9% rate")
c3.metric("Total Deaths",    "5.30 L",  "-1.19% CFR")
c4.metric("Peak Day (Wave 2)", "4.14L",  "May 6, 2021")
c5.metric("States Covered",  "20",      "All major states")

st.divider()

# ── Tabs ──────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["State Rankings", "Wave Analysis", "State Deep-Dive", "Insights"])

# Tab 1: State Rankings
with tab1:
    col1, col2 = st.columns([1.4, 1])

    with col1:
        fdf = df[df['State'].isin(selected_states)].sort_values(metric, ascending=False)
        fig_bar = px.bar(
            fdf, x=metric, y='State', orientation='h',
            color=metric,
            color_continuous_scale=['#E1F5EE','#1D9E75'] if metric in ['Recovered','Recovery Rate'] else
                                   ['#FCEBEB','#E24B4A'] if metric in ['Confirmed','Deaths','CFR'] else
                                   ['#FAEEDA','#EF9F27'],
            title=f"{metric} by State",
            labels={metric: metric, 'State': ''},
            height=520
        )
        fig_bar.update_layout(showlegend=False, coloraxis_showscale=False,
                              margin=dict(l=0,r=10,t=40,b=0),
                              yaxis=dict(categoryorder='total ascending'))
        fig_bar.update_traces(hovertemplate='<b>%{y}</b><br>'+metric+': %{x:,.0f}<extra></extra>')
        st.plotly_chart(fig_bar, use_container_width=True)

    with col2:
        fig_scatter = px.scatter(
            df, x='Recovery Rate', y='CFR', size='Confirmed',
            hover_name='State', color='Confirmed',
            color_continuous_scale='RdYlGn_r',
            title='Recovery rate vs Case fatality rate',
            labels={'Recovery Rate':'Recovery rate (%)','CFR':'Case fatality rate (%)'},
            height=250
        )
        fig_scatter.update_layout(margin=dict(l=0,r=0,t=40,b=0), coloraxis_showscale=False)
        st.plotly_chart(fig_scatter, use_container_width=True)

        st.dataframe(
            df[['State','Confirmed','Deaths','CFR','Recovery Rate']].sort_values('Confirmed',ascending=False).head(10),
            use_container_width=True, hide_index=True, height=230
        )

# Tab 2: Wave Analysis
with tab2:
    state_wave = st.selectbox("Select state for wave analysis",
        ['India'] + df['State'].tolist(), index=0, key='wave_sel')

    wdf = gen_wave_data(state_wave)

    fig_wave = go.Figure()
    fig_wave.add_bar(x=wdf['Date'], y=wdf['Wave1'], name='Wave 1 (Mar–Sep 2020)',
                     marker_color='rgba(226,75,74,0.7)')
    fig_wave.add_bar(x=wdf['Date'], y=wdf['Wave2'], name='Wave 2 (Feb–Jun 2021)',
                     marker_color='rgba(239,159,39,0.7)')
    fig_wave.add_bar(x=wdf['Date'], y=wdf['Wave3'], name='Wave 3 / Omicron (Dec 2021–Feb 2022)',
                     marker_color='rgba(127,119,221,0.7)')
    fig_wave.add_scatter(x=wdf['Date'], y=wdf['MA7'], mode='lines', name='3-month moving avg',
                         line=dict(color='#1D9E75', width=2.5))

    fig_wave.update_layout(
        barmode='stack', title=f'Daily new cases — {state_wave}',
        xaxis_title='Month', yaxis_title='Cases',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='left', x=0),
        height=380, margin=dict(l=0,r=0,t=60,b=0),
        hovermode='x unified'
    )
    st.plotly_chart(fig_wave, use_container_width=True)

    c1, c2, c3 = st.columns(3)
    wave_peak = wdf['Total'].max()
    wave_peak_date = wdf.loc[wdf['Total'].idxmax(), 'Date'].strftime('%b %Y')
    c1.metric("Peak daily cases", f"{wave_peak:,.0f}", f"in {wave_peak_date}")
    c2.metric("Wave 2 vs Wave 1", f"+{round(wdf['Wave2'].max()/max(1,wdf['Wave1'].max())*100-100)}%", "Wave 2 was far more severe")
    c3.metric("Omicron vs Wave 2", f"{round(wdf['Wave3'].max()/max(1,wdf['Wave2'].max())*100)}%", "High cases, lower deaths")

# Tab 3: State Deep-Dive
with tab3:
    state_sel = st.selectbox("Select a state", df['State'].tolist(), index=0, key='deep_sel')
    srow = df[df['State']==state_sel].iloc[0]

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Confirmed", f"{srow['Confirmed']:,.0f}")
    c2.metric("Recovered", f"{srow['Recovered']:,.0f}", f"{srow['Recovery Rate']}%")
    c3.metric("Deaths",    f"{srow['Deaths']:,.0f}", f"CFR {srow['CFR']}%")
    c4.metric("Active",    f"{srow['Active']:,.0f}")

    col1, col2 = st.columns(2)
    with col1:
        fig_donut = go.Figure(go.Pie(
            labels=['Recovered','Deaths','Active'],
            values=[srow['Recovered'], srow['Deaths'], srow['Active']],
            hole=0.65,
            marker_colors=['#1D9E75','#E24B4A','#EF9F27'],
            textinfo='percent+label'
        ))
        fig_donut.update_layout(title=f'{state_sel} — case breakdown', height=300,
                                 showlegend=False, margin=dict(l=0,r=0,t=40,b=0))
        st.plotly_chart(fig_donut, use_container_width=True)

    with col2:
        compare_df = df.sort_values('Confirmed', ascending=False).head(8)
        state_rank = df.sort_values('Confirmed', ascending=False).reset_index(drop=True)
        rank = state_rank[state_rank['State']==state_sel].index[0]+1

        st.markdown(f"""
**{state_sel} at a glance:**
- Rank **#{rank}** out of 20 states by confirmed cases
- Recovery rate: **{srow['Recovery Rate']}%** (national avg 98.9%)
- Case fatality rate: **{srow['CFR']}%** (national avg 1.19%)
- Active cases remaining: **{srow['Active']:,}**
        """)

        fig_comp = px.bar(
            compare_df, x='State', y='CFR',
            color='CFR', color_continuous_scale=['#E1F5EE','#E24B4A'],
            title='CFR comparison — top 8 states',
            height=210
        )
        fig_comp.update_layout(margin=dict(l=0,r=0,t=40,b=60), coloraxis_showscale=False,
                                xaxis_tickangle=-30)
        st.plotly_chart(fig_comp, use_container_width=True)

# Tab 4: Insights
with tab4:
    st.subheader("Key findings from the data")

    ins1, ins2 = st.columns(2)
    with ins1:
        st.success("""
**Maharashtra led in total cases (7.9M)**  
Highest absolute burden — dense population, early epicentre.  
However, CFR of 1.86% is above national average.
        """)
        st.warning("""
**Wave 2 (May 2021) was the deadliest**  
Daily cases hit 4.14 lakh nationally on May 6, 2021.  
Delta variant drove 3x more severe outcomes than Wave 1.
        """)
        st.info("""
**Kerala reported cases longest into 2022**  
High testing rates inflated confirmed numbers but  
recovery rate stayed above 99% throughout.
        """)

    with ins2:
        fig_cfr = px.bar(
            df.sort_values('CFR', ascending=False),
            x='State', y='CFR',
            color='CFR',
            color_continuous_scale=['#E1F5EE','#E24B4A'],
            title='Case fatality rate by state (%)',
            height=300
        )
        fig_cfr.update_layout(margin=dict(l=0,r=0,t=40,b=80),
                               coloraxis_showscale=False, xaxis_tickangle=-45)
        st.plotly_chart(fig_cfr, use_container_width=True)

    st.divider()
    st.markdown("""
**Data note:** This dashboard uses the covid19india.org dataset for the period March 2020 – March 2022.  
Wave shapes are modelled from published peak data. For live real-time data, connect to  
[api.covid19india.org](https://api.covid19india.org) or the Ministry of Health API.
    """)
