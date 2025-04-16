import streamlit as st
import folium
import pandas as pd
from folium.plugins import HeatMap

# Configuração de layout para ocupar toda a tela
st.set_page_config(layout="wide")

# Título principal
st.title("📍 Mapa Interativo por Data ou Período")

# Função para criar e exibir o mapa com filtro de data ou período
def exibir_mapa(file_name, titulo, mapa_id):
    # Ler o arquivo CSV
    data = pd.read_csv(file_name, delimiter=';', encoding='latin-1', skiprows=1, names=["Localizacao", "Datetime", "Cliente"])
    data['Datetime'] = pd.to_datetime(data['Datetime'], errors='coerce')
    data.dropna(subset=['Datetime'], inplace=True)
    data['Data'] = data['Datetime'].dt.date

    datas_unicas = sorted(data['Data'].unique())
    if not datas_unicas:
        st.warning(f"Nenhuma data válida encontrada no arquivo: {titulo}")
        return

    st.subheader(f"{titulo}")

    # Opção de filtro: uma data ou período
    filtro_opcao = st.radio(
        f"Tipo de filtro para {titulo}:",
        ("Uma data específica", "Período de datas"),
        key=f"filtro_{titulo}"
    )

    if filtro_opcao == "Uma data específica":
        data_selecionada = st.date_input(
            f"Selecione uma data:",
            min_value=min(datas_unicas),
            max_value=max(datas_unicas),
            value=min(datas_unicas),
            key=f"data_{titulo}"
        )
        data_filtrada = data[data['Data'] == data_selecionada]

    else:  # Período de datas
        data_inicio, data_fim = st.date_input(
            f"Selecione o período:",
            [min(datas_unicas), max(datas_unicas)],
            min_value=min(datas_unicas),
            max_value=max(datas_unicas),
            key=f"periodo_{titulo}"
        )

        if isinstance(data_inicio, list) or isinstance(data_fim, list):
            st.warning("Por favor, selecione um intervalo válido.")
            return

        data_filtrada = data[(data['Data'] >= data_inicio) & (data['Data'] <= data_fim)]

    # Separar coordenadas
    data_filtrada[['Latitude', 'Longitude']] = data_filtrada['Localizacao'].str.split(',', expand=True)
    data_filtrada['Latitude'] = pd.to_numeric(data_filtrada['Latitude'], errors='coerce')
    data_filtrada['Longitude'] = pd.to_numeric(data_filtrada['Longitude'], errors='coerce')
    data_filtrada.dropna(subset=['Latitude', 'Longitude'], inplace=True)

    if data_filtrada.empty:
        st.info("Nenhum dado encontrado com os filtros selecionados.")
        return

    # Criar o mapa
    latitude_mean = data_filtrada['Latitude'].mean()
    longitude_mean = data_filtrada['Longitude'].mean()
    mapa = folium.Map(location=[latitude_mean, longitude_mean], zoom_start=12)

    # Opção de visualização: Marcadores ou Mapa de Calor
    visualizacao = st.radio("Tipo de visualização:", ("Marcadores", "Mapa de Calor"), horizontal=True, key=f"vis_{titulo}")

    if visualizacao == "Marcadores":
        # Adicionar marcadores
        for _, row in data_filtrada.iterrows():
            folium.Marker(
                location=[row['Latitude'], row['Longitude']],
                popup=f"Data e Hora: {row['Datetime']}<br>Cliente: {row['Cliente']}",
                icon=folium.Icon(color='blue', icon='info-sign')
            ).add_to(mapa)
    elif visualizacao == "Mapa de Calor":
        # Adicionar mapa de calor
        heat_data = data_filtrada[['Latitude', 'Longitude']].dropna().values.tolist()
        HeatMap(heat_data).add_to(mapa)

    # Exibir o mapa no Streamlit com CSS para tela cheia e responsiva
    st.components.v1.html(
        f"""
        <style>
            .folium-map-wrapper-{mapa_id} {{
                width: 100%;  /* Ocupa 100% da largura da tela */
                height: 45vh;  /* Ocupa 45% da altura da tela para cada mapa */
                margin: 0;
                padding: 0;
            }}
            html, body {{
                height: 100%;
                margin: 0;
                padding: 0;
            }}
        </style>
        <div class="folium-map-wrapper-{mapa_id}">
            {mapa._repr_html_()}
        </div>
        """,
        height=850,
        scrolling=False
    )

# Exibir um mapa (somente um)
arquivo = ("coordenadas_unificadas.csv", "Mapa - SELECIONE A DATA")
exibir_mapa(arquivo[0], arquivo[1], mapa_id="mapa_1")
