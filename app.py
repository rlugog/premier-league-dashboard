import pandas as pd
import streamlit as st
import plotly.express as px

# --- Cargar y limpiar datos ---
df = pd.read_csv("PremierLeagueMatches.csv")

df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
df['Attendance'] = df['Attendance'].str.replace(',', '', regex=False).astype(float)

df.rename(columns={
    'Home Team': 'home_team',
    'Away Team': 'away_team',
    'homeScore': 'home_score',
    'awayScore': 'away_score',
    'homeXG': 'home_xg',
    'awayXG': 'away_xg',
    '*Additional Stats': 'link'
}, inplace=True)

# Separar partidos jugados (aquellos que tienen score)
df = df[df['home_score'].notna()]

# Eficiencia ofensiva y defensiva
off_eff = df.groupby('home_team')[['home_score', 'home_xg']].mean()
off_eff = (off_eff['home_score'] - off_eff['home_xg']).rename("ofensiva")

home_conc = df.groupby('home_team')['away_score'].mean()
away_conc = df.groupby('away_team')['home_score'].mean()
home_xg_conc = df.groupby('home_team')['away_xg'].mean()
away_xg_conc = df.groupby('away_team')['home_xg'].mean()
def_eff = home_conc.add(away_conc, fill_value=0) - home_xg_conc.add(away_xg_conc, fill_value=0)
def_eff = def_eff.rename("defensiva")

summary = pd.concat([off_eff, def_eff], axis=1)
summary["balance_total"] = summary["ofensiva"] - summary["defensiva"]
summary = summary.reset_index().rename(columns={"home_team": "Equipo"})

# --- Streamlit App ---
st.title("⚽ Dashboard Premier League: Eficiencia de Equipos")

# Gráfico 1
st.subheader("⚽ Eficiencia ofensiva (Goles - xG)")
fig1 = px.bar(summary, x="Equipo", y="ofensiva", color="ofensiva", color_continuous_scale="Greens")
fig1.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig1)

# Gráfico 2
st.subheader("🛡️ Eficiencia defensiva (Goles recibidos - xG concedido)")
fig2 = px.bar(summary, x="Equipo", y="defensiva", color="defensiva", color_continuous_scale="Reds_r")
fig2.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig2)

# Gráfico 3
st.subheader("📍 Mapa combinado de eficiencia ofensiva y defensiva")
fig3 = px.scatter(summary, x="ofensiva", y="defensiva", text="Equipo",
                  color="balance_total", color_continuous_scale="RdYlGn")
fig3.add_hline(y=0, line_dash="dash", line_color="gray")
fig3.add_vline(x=0, line_dash="dash", line_color="gray")
fig3.update_traces(textposition='top center')
st.plotly_chart(fig3)

