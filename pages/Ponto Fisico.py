import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import locale

# Configura o locale para português
try:
    locale.setlocale(locale.LC_TIME, 'pt_BR.utf8')
except:
    locale.setlocale(locale.LC_TIME, 'pt_BR')

st.set_page_config(layout="wide")
st.title("💰 Lucro e Vendas por Dia — Filtro por Data e Horário")

# Carrega os dados
df = pd.read_csv("Brothers_Burguer_filtrado_15-03-2025.csv")

# Ajustes iniciais
df["Data"] = pd.to_datetime(df["Data"])
df["Hora"] = df["Data"].dt.hour
df["Dia_Semana"] = df["Data"].dt.strftime('%A')  # Dia da semana
df["Data"] = df["Data"].dt.date
df["Valor"] = df["Valor"].astype(float)

# Filtro de data
filtro_tipo = st.radio("Tipo de filtro de data:", ["Uma data específica", "Duas datas específicas", "Período de datas"])
datas_disponiveis = sorted(df["Data"].unique())

if filtro_tipo == "Uma data específica":
    data_escolhida = st.date_input(
        "Selecione a data:",
        min_value=min(datas_disponiveis),
        max_value=max(datas_disponiveis),
        value=min(datas_disponiveis)
    )
    df_filtrado = df[df["Data"] == data_escolhida]
    mostrar_grafico_detalhado = True

elif filtro_tipo == "Duas datas específicas":
    col1, col2 = st.columns(2)
    with col1:
        data1 = st.date_input(
            "Data 1:",
            min_value=min(datas_disponiveis),
            max_value=max(datas_disponiveis),
            value=datas_disponiveis[0]
        )
    with col2:
        data2 = st.date_input(
            "Data 2:",
            min_value=min(datas_disponiveis),
            max_value=max(datas_disponiveis),
            value=datas_disponiveis[-1]
        )
    df_filtrado = df[df["Data"].isin([data1, data2])]
    mostrar_grafico_detalhado = False  # gráfico detalhado por hora desativado nesse modo

else:
    data_inicio, data_fim = st.date_input(
        "Selecione o intervalo de datas:",
        [min(datas_disponiveis), max(datas_disponiveis)],
        min_value=min(datas_disponiveis),
        max_value=max(datas_disponiveis)
    )
    df_filtrado = df[(df["Data"] >= data_inicio) & (df["Data"] <= data_fim)]
    mostrar_grafico_detalhado = False

# Filtro de horário — de 16h até 23h
hora_inicio, hora_fim = st.slider(
    "Selecione o intervalo de horário:",
    min_value=16,
    max_value=23,
    value=(16, 23),
    step=1
)

# Filtra pelo horário
df_filtrado = df_filtrado[(df_filtrado["Hora"] >= hora_inicio) & (df_filtrado["Hora"] <= hora_fim)]

# Verifica dados
if df_filtrado.empty:
    st.warning("Nenhum dado encontrado com os filtros aplicados.")
else:
    # Agrupa por data
    resumo = df_filtrado.groupby("Data").agg(
        Quantidade_Vendas=("Valor", "count"),
        Lucro_Total=("Valor", "sum")
    ).reset_index()

    resumo["Dia_Semana"] = pd.to_datetime(resumo["Data"]).dt.strftime('%A').str.capitalize()
    resumo["Data_Dia"] = resumo["Data"].astype(str) + " (" + resumo["Dia_Semana"] + ")"

    # Gráfico de lucro por dia
    fig, ax = plt.subplots(figsize=(10, 5))
    resumo.set_index("Data_Dia")["Lucro_Total"].plot(kind='bar', color='#32CD32', edgecolor='black', ax=ax)
    ax.set_title(f"Lucro por Dia ({hora_inicio}h às {hora_fim+1}h)", fontsize=16, fontweight='bold')
    ax.set_xlabel("Data (Dia da Semana)", fontsize=12)
    ax.set_ylabel("Lucro (R$)", fontsize=12)
    ax.set_xticklabels(resumo["Data_Dia"], rotation=45, ha='right')

    for i, v in enumerate(resumo["Lucro_Total"]):
     ax.text(i, v + (v * 0.02), f"R${v:.2f}", ha='center', fontsize=6, color='black')


    st.pyplot(fig)

    # Tabela com os dados
    st.subheader("📊 Tabela de Lucro e Vendas")
    st.dataframe(resumo.drop(columns=["Data_Dia"]), use_container_width=True)

    # Gráfico detalhado por hora (apenas quando for uma data específica)
    if mostrar_grafico_detalhado:
        st.subheader("📈 Vendas por Horário")
        por_hora = df_filtrado.groupby("Hora").agg(
            Quantidade_Vendas=("Valor", "count"),
            Lucro=("Valor", "sum")
        ).reset_index()

        fig2, ax2 = plt.subplots(figsize=(10, 5))
        por_hora.set_index("Hora")["Quantidade_Vendas"].plot(kind='bar', ax=ax2, color='#FFD700', edgecolor='black')
        ax2.set_title("Quantidade de Vendas por Hora", fontsize=14)
        ax2.set_xlabel("Hora")
        ax2.set_ylabel("Nº de Vendas")

        for i, v in enumerate(por_hora["Quantidade_Vendas"]):
            ax2.text(i, v + 0.1, str(v), ha='center', fontsize=10)

        st.pyplot(fig2)
