
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# -------------------- Configuração da Página --------------------
st.set_page_config(page_title="Simulador de Despesa com Pessoal (LRF)", layout="wide")

# -------------------- Título --------------------
st.title("Simulador de Despesa com Pessoal (LRF) - Limites Máximo/Prudencial/Alerta")

# -------------------- Entradas --------------------
col1, col2 = st.columns(2)
with col1:
    receita_corrente_liquida = st.number_input("Receita Corrente Líquida (R$)", value=1000000.0, step=10000.0)
with col2:
    despesa_pessoal = st.number_input("Despesa Atual com Pessoal (R$)", value=500000.0, step=10000.0)

# Limites da LRF
limite_max = 0.60 * receita_corrente_liquida
limite_prud = 0.575 * receita_corrente_liquida
limite_alerta = 0.54 * receita_corrente_liquida

# -------------------- Simulações --------------------
st.sidebar.header("Simulações")
aumento_despesa = st.sidebar.number_input("Variação na Despesa (%)", value=0.0, step=1.0)
aumento_receita = st.sidebar.number_input("Variação na Receita (%)", value=0.0, step=1.0)

despesa_simulada = despesa_pessoal * (1 + aumento_despesa / 100)
receita_simulada = receita_corrente_liquida * (1 + aumento_receita / 100)

# -------------------- Cálculos --------------------
margem_atual = receita_corrente_liquida - despesa_pessoal
margem_simulada = receita_simulada - despesa_simulada

perc_atual = despesa_pessoal / receita_corrente_liquida
perc_simulado = despesa_simulada / receita_simulada

# -------------------- Tabela --------------------
df = pd.DataFrame({
    "Situação": ["Atual", "Simulada"],
    "Receita (R$)": [receita_corrente_liquida, receita_simulada],
    "Despesa (R$)": [despesa_pessoal, despesa_simulada],
    "% Despesa/Receita": [f"{perc_atual:.2%}", f"{perc_simulado:.2%}"],
    "Margem (R$)": [margem_atual, margem_simulada]
})
st.subheader("📊 Situação Atual x Simulada")
st.dataframe(df, use_container_width=True)

# -------------------- Gráfico Gauge --------------------
st.subheader("🧭 Limite de Despesa com Pessoal (Gauge)")
fig_gauge = go.Figure(go.Indicator(
    mode="gauge+number+delta",
    value=perc_simulado * 100,
    delta={"reference": perc_atual * 100, "increasing": {"color": "red"}, "decreasing": {"color": "green"}},
    gauge={
        "axis": {"range": [0, 100]},
        "bar": {"color": "blue"},
        "steps": [
            {"range": [0, limite_alerta/receita_simulada*100], "color": "lightgreen"},
            {"range": [limite_alerta/receita_simulada*100, limite_prud/receita_simulada*100], "color": "yellow"},
            {"range": [limite_prud/receita_simulada*100, limite_max/receita_simulada*100], "color": "orange"},
            {"range": [limite_max/receita_simulada*100, 100], "color": "red"}
        ]
    },
    title={"text": "Percentual da Despesa sobre Receita (%)"}
))
st.plotly_chart(fig_gauge, use_container_width=True)

# -------------------- Gráfico de Comparação --------------------
st.subheader("📈 Comparação Receita x Despesa (Atual x Simulada)")
fig_comp = go.Figure()
fig_comp.add_trace(go.Bar(x=["Atual"], y=[despesa_pessoal], name="Despesa Atual", marker_color="red"))
fig_comp.add_trace(go.Bar(x=["Atual"], y=[receita_corrente_liquida], name="Receita Atual", marker_color="green"))
fig_comp.add_trace(go.Bar(x=["Simulada"], y=[despesa_simulada], name="Despesa Simulada", marker_color="orange"))
fig_comp.add_trace(go.Bar(x=["Simulada"], y=[receita_simulada], name="Receita Simulada", marker_color="blue"))
fig_comp.update_layout(barmode="group", xaxis_title="Situação", yaxis_title="Valores (R$)")
st.plotly_chart(fig_comp, use_container_width=True)

# -------------------- Gráfico de Linha --------------------
st.subheader("📉 Evolução da Relação Despesa/Receita")
fig_line = px.line(x=["Atual", "Simulada"], y=[perc_atual*100, perc_simulado*100],
                   labels={"x": "Situação", "y": "% Despesa/Receita"},
                   markers=True)
st.plotly_chart(fig_line, use_container_width=True)

# -------------------- Recomendações --------------------
st.subheader("📌 Recomendações")
def recomendacoes(despesa, receita, limite, nome):
    if despesa <= limite:
        return f"✅ Situação dentro do limite {nome}."
    else:
        excesso = despesa - limite
        perc = excesso / receita * 100
        return f"⚠️ Necessário reduzir **{excesso:,.2f} R$ ({perc:.2f}%)** para respeitar o limite {nome}."

st.write(recomendacoes(despesa_simulada, receita_simulada, limite_max, "Máximo"))
st.write(recomendacoes(despesa_simulada, receita_simulada, limite_prud, "Prudencial"))
st.write(recomendacoes(despesa_simulada, receita_simulada, limite_alerta, "Alerta"))
