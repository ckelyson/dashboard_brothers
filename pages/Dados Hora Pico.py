import streamlit as st
import folium
import pandas as pd
import matplotlib.pyplot as plt

# Configuração de layout para ocupar toda a tela
st.set_page_config(layout="wide")

# Título principal
st.title("📍 Mapa Interativo de Horários de Pico de Vendas")

# Função para criar e exibir o mapa com filtro de horário de pico
def exibir_mapa(file_name, titulo, mapa_id):
    # Ler o arquivo CSV
    data = pd.read_csv(file_name, delimiter=';', encoding='latin-1', skiprows=1, names=["Localizacao", "Datetime", "Cliente"])
    data['Datetime'] = pd.to_datetime(data['Datetime'], errors='coerce')
    data.dropna(subset=['Datetime'], inplace=True)
    data['Data'] = data['Datetime'].dt.date
    data['Hora'] = data['Datetime'].dt.hour

    # Remover a linha que exclui dados com Cliente vazio
    # data = data.dropna(subset=['Cliente'])  # Remova ou comente essa linha para incluir todos os registros

    # Opção de filtro: uma data específica ou intervalo de datas
    filtro_data_opcao = st.radio(
        f"Tipo de filtro para {titulo}:",
        ("Uma data específica", "Período de datas"),
        key=f"filtro_data_{titulo}"
    )

    if filtro_data_opcao == "Uma data específica":
        # Filtro de data
        datas_unicas = sorted(data['Data'].unique())
        data_selecionada = st.date_input(
            f"Selecione uma data:",
            min_value=min(datas_unicas),
            max_value=max(datas_unicas),
            value=min(datas_unicas),
            key=f"data_{titulo}"
        )
        data_filtrada = data[data['Data'] == data_selecionada]

    else:  # Período de datas
        datas_unicas = sorted(data['Data'].unique())
        data_inicio, data_fim = st.date_input(
            f"Selecione o período de datas:",
            [min(datas_unicas), max(datas_unicas)],
            min_value=min(datas_unicas),
            max_value=max(datas_unicas),
            key=f"periodo_data_{titulo}"
        )
        data_filtrada = data[(data['Data'] >= data_inicio) & (data['Data'] <= data_fim)]

    # Verificar se há dados após o filtro de data
    if data_filtrada.empty:
        st.info("Nenhum dado encontrado com os filtros de data selecionados.")
        return

    # Determinar os horários de pico
    vendas_por_hora = data_filtrada.groupby(['Hora']).size()

    # Opção de filtro: intervalo de horas
    hora_inicio = int(vendas_por_hora.index.min())  # Começo do intervalo de horas
    hora_fim = int(vendas_por_hora.index.max())  # Fim do intervalo de horas

    # Definir o intervalo de horas selecionado como o intervalo completo por padrão
    hora_inicio, hora_fim = st.slider(
        f"Selecione o intervalo de horas:",
        min_value=hora_inicio,
        max_value=hora_fim,
        value=(hora_inicio, hora_fim),
        step=1,
        key=f"periodo_hora_{titulo}"
    )

    data_filtrada = data_filtrada[(data_filtrada['Hora'] >= hora_inicio) & (data_filtrada['Hora'] <= hora_fim)]

    # Verificar se há dados após o filtro de hora
    if data_filtrada.empty:
        st.info("Nenhum dado encontrado com os filtros selecionados.")
        return

    # Separar coordenadas
    data_filtrada[['Latitude', 'Longitude']] = data_filtrada['Localizacao'].str.split(',', expand=True)
    data_filtrada['Latitude'] = pd.to_numeric(data_filtrada['Latitude'], errors='coerce')
    data_filtrada['Longitude'] = pd.to_numeric(data_filtrada['Longitude'], errors='coerce')
    data_filtrada.dropna(subset=['Latitude', 'Longitude'], inplace=True)

    # Criar o mapa
    latitude_mean = data_filtrada['Latitude'].mean()
    longitude_mean = data_filtrada['Longitude'].mean()
    mapa = folium.Map(location=[latitude_mean, longitude_mean], zoom_start=12)

    # Adicionar marcadores
    for _, row in data_filtrada.iterrows():
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=f"Data e Hora: {row['Datetime']}<br>Cliente: {row['Cliente']}<br>Hora: {row['Hora']}",
            icon=folium.Icon(color='blue', icon='info-sign')
        ).add_to(mapa)

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

    # Gráfico de quantidade de vendas por hora
    vendas_por_hora = data_filtrada.groupby(['Hora']).size()
    fig, ax = plt.subplots(figsize=(10, 6))

    # Estilo de barras douradas e fundo temático
    vendas_por_hora.plot(kind='bar', ax=ax, color='#FFD700', edgecolor='black')

    # Adicionar os valores das vendas acima das barras
    for i, v in enumerate(vendas_por_hora):
        ax.text(i, v + 0.1, str(v), ha='center', va='bottom', fontsize=10, fontweight='bold', color='black')

    ax.set_title('Quantidade de Vendas por Hora', fontsize=18, fontweight='bold', color='#D2691E')  # Título em cor laranja
    ax.set_xlabel('Hora', fontsize=14, fontweight='bold', color='#D2691E')  # Cor do rótulo X
    ax.set_ylabel('Número de Vendas', fontsize=14, fontweight='bold', color='#D2691E')  # Cor do rótulo Y
    ax.set_xticklabels(vendas_por_hora.index, rotation=45)
    
    # Estilizando o gráfico
    ax.spines['top'].set_color('#D2691E')
    ax.spines['right'].set_color('#D2691E')
    ax.spines['bottom'].set_color('#D2691E')
    ax.spines['left'].set_color('#D2691E')

    # Exibir o gráfico estilizado
    st.pyplot(fig)

# Exibir um mapa (somente um)
arquivo = ("coordenadas_unificadas.csv", "Mapa - SELECIONE A DATA E HORÁRIO DE PICO")
exibir_mapa(arquivo[0], arquivo[1], mapa_id="mapa_1")
