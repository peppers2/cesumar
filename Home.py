import streamlit as st
import pandas as pd
import folium
import warnings
import time
from PIL import Image
warnings.filterwarnings("ignore")


# CONFIGURAÇÃO DO LAYOUT DA PAGINA
st.set_page_config(page_title="Painel de Devolução", layout="wide")

# TITULO DA PAGINA
st.title("🚚 Painel de Tratativa de Anomalias")
st.write("Projeto desenvolvido: Pedro Siqueira - RA: 23462442-4 - Unicesumar")



# IMPORTAÇÃO DA BASE DE DADOS
caminho = 'base.xlsx'

@st.cache_data
def importacao(caminho):
    df = pd.read_excel(caminho)
    return df

df = importacao(caminho)

########
#
#TRATAMENTO DE DADOS
#
########
df['mapa'] = df['Chave_Mapa'].astype(str).str.replace('761656-', '', regex=True)
df['Mapa-Cliente'] = df['mapa'].astype(str) + " - " + df['Cod_Cliente'].astype(str)
df['Dia_Entrega'] = pd.to_datetime(df['tour_date'], errors='coerce', format='%Y%m%d')
df['Dia_Entrega'] = df['Dia_Entrega'].dt.date




colunas = ['arrived_at', 'assistants_quantity', 'Chave_Mapa', 'Cod_Cliente',    
           'driver_external_id', 'estimated_time_arrival', 'estimated_time_departure',
           'finished_at', 'last_reason_rescheduled', 'last_reason_waiting_modulation',
           'last_timestamp_on_the_way', 'last_timestamp_rescheduled', 'optimized_order',
           'original_order', 'poc_external_id', 'poc_latitude', 'poc_longitude',
           'poc_name', 'status', 'total_delivered_value', 'total_delivered_vol',
           'total_refused_value', 'total_refused_vol', 'total_value', 'total_weight_kg',
           'tour_date', 'tour_display_id', 'tour_display_id_Original',
           'Contagem de Tour_Trip_ID', 'Soma de trip_display_id', 'trip_end_timestamp',
           'trip_start_timestamp', 'vehicle_license_plate', 'visit_order',
           'volume_hectoliters_sum', 'volume_packages', 'within_radius',
           'diff_departure_arrival', 'diff_finished_arrived', 'foxtrot_adherence']

df = df.set_index('Dia_Entrega')


dfaero = df.copy()


#######
#
# CONFIGURAÇÃO DO SIDEBAR
#
#######

st.sidebar.title('Filtros:')

#min_date = df.index.min()  
max_date = df.index.max()
#min_date = max_date - pd.Timedelta(days=30)
min_date = max_date.replace(day=1)

start_date = st.sidebar.date_input('Data de Início',  min_date)
end_date = st.sidebar.date_input('Data de Fim', max_date)

# Converta start_date e end_date para pd.Timestamp
start_date = pd.Timestamp(start_date)
end_date = pd.Timestamp(end_date)

# Converta o índice do DataFrame para pd.Timestamp
df.index = pd.to_datetime(df.index)


# Filtro de Status na Sidebar
status = df['status'].unique().tolist()
selected_status = st.sidebar.selectbox('Escolha um Status', options=status, index=status.index("CONCLUDED"))

# Filtro de Placa na Sidebar
placas = df['vehicle_license_plate'].dropna().unique().tolist()
selected_placa = st.sidebar.multiselect('Escolha uma Placa', options=placas)

# Filtro de Código do PDV na Sidebar
select_pdv = st.sidebar.number_input("Digite o Código PDV:", value=0)




############
#
# APLICANDO FILTROS A TABELA DO SIDEBAR
#
#############
if end_date < start_date:
    st.sidebar.error('A Data de Fim deve ser maior ou igual à Data de Início.')
else:
    # Filtre o DataFrame com base nas datas selecionadas
    df_filtrado = df[(df.index >= start_date) & (df.index <= end_date)]
    
    # Verifique se selected_status e selected_placa não estão vazios
    if selected_status:
        st.write(f"Filtrando por status: {selected_status}")
        df_filtrado = df_filtrado[df_filtrado['status'] == selected_status]
    
    if selected_placa:
        st.write(f"Filtrando por placa: {selected_placa}")
        # Filtra o DataFrame para placas selecionadas
        df_filtrado = df_filtrado[df_filtrado['vehicle_license_plate'].isin(selected_placa)]

    if select_pdv:
        st.write(f"Filtrando por PDV: {select_pdv}")
        # Filtra o DataFrame para o código do PDV selecionado
        df_filtrado = df_filtrado[df_filtrado['Cod_Cliente'] == select_pdv]
    
    st.sidebar.image("logom.png", use_column_width=True)

 

    # Exibe o DataFrame filtrado
    st.write("Dados Filtrados:")
    
    df_filtrado = df_filtrado.rename(columns={
        'arrived_at': 'Chegada',
        'assistants_quantity': 'xx', 
        'Chave_Mapa': 'Chave Mapa', 
        'Cod_Cliente': 'PDV',    
        'driver_external_id': 'Tempo',
        'estimated_time_arrival': 'Estimativa de Chegada',
        'estimated_time_departure': 'Estimativa da Partida',
        'finished_at': 'Terminou em:', 
        'last_reason_rescheduled': 'Ultimo motivo remarcado', 
        'last_reason_waiting_modulation': 'Ultima razão aguardando modulação',
        'last_timestamp_on_the_way': 'Ultimo carimbo de data/hora a caminho',
        'last_timestamp_rescheduled': 'Ultimo carimbo de data/hora reprogramado',
        'optimized_order': 'pedido_otimizado',
        'original_order': 'Pedido Original', 
        'poc_external_id': 'Cod PDV',
        'poc_latitude': 'Latitude',
        'poc_longitude': 'Longitude',
        'poc_name': 'Nome Fantasia', 
        'status': 'Status',
        'total_delivered_value': 'Valor Total Pedido',
        'total_delivered_vol': 'Volume Total Pedido',
        'total_refused_value': 'Valor Devolvido', 
        'total_refused_vol': 'Volume Devolvido',
        'total_value': 'Valor Total',
        'total_weight_kg': 'Peso Total',
        'tour_date': 'Data',
        'tour_display_id': 'Mapa', 
        'tour_display_id_Original': 'Mapa2',
        'Contagem de Tour_Trip_ID': 'x',
        'Soma de trip_display_id': 'Soma data/hora de término da viagem',
        'trip_end_timestamp': 'data/hora de término da viagem',
        'trip_start_timestamp': 'data/hora de inicio da viagem',
        'vehicle_license_plate': 'Placa', 
        'visit_order': 'Ordem Visita',
        'volume_hectoliters_sum': 'Soma Volume',
        'volume_packages': 'Total SKU',
        'within_radius': 'Acessou o raio',
        'diff_departure_arrival': 'Tempo de Atendimento', 
        'diff_finished_arrived': 'Tempo de Espera', 
        'foxtrot_adherence': 'Foxtrot',
        'Mapa-Cliente': 'Mapa Cliente'
    })

    df_filtrado = df_filtrado[['mapa', 'Placa', 'Acessou o raio', 'Ordem Visita', 'Chegada', 'xx', 'Cod PDV', 'Nome Fantasia', 'Latitude', 'Longitude', 
                               'Estimativa de Chegada', 'Estimativa da Partida', 'Terminou em:', 'Ultimo motivo remarcado',
                               'Ultima razão aguardando modulação', 'Ultimo carimbo de data/hora a caminho',
                               'Ultimo carimbo de data/hora reprogramado', 'Status', 'Valor Total Pedido', 'Volume Total Pedido',
                               'Valor Devolvido', 'Volume Devolvido', 'Valor Total', 'Peso Total', 'Data', 'Mapa', 
                               'x', 'Soma data/hora de término da viagem', 
                               'Soma Volume', 'Total SKU', 
                               'Tempo de Atendimento', 'Tempo de Espera','data/hora de inicio da viagem','data/hora de término da viagem', 'Mapa Cliente']]



    
    

    df_filtrado['Ordem Visita'] = df_filtrado['Ordem Visita'].fillna(0).astype(int)
   # df_filtrado['Volume Devolvido'] = df_filtrado['Volume Devolvido'].fillna(0).astype(int)
    df_filtrado = df_filtrado.sort_values(by=['Dia_Entrega', 'Ordem Visita'], ascending=[False, True])
    df_filtrado['Acessou o raio'] = df_filtrado['Acessou o raio'].fillna(0).astype(int)
    



    st.session_state['df_filtrado'] = df_filtrado




##########
#
#CONTAS PELO PANDAS
#
#########

# Calcula métricas
    
    total_visita_concluded = df_filtrado[df_filtrado['Status'] == 'CONCLUDED']['Mapa Cliente'].value_counts().sum()
    
    total_status_no_raio = df_filtrado.query("`Acessou o raio` == 1 and `Status` == 'CONCLUDED'")['Mapa Cliente'].value_counts().sum()

    
    total_fora_raio =  total_visita_concluded - total_status_no_raio
    percentual_dentro_do_raio = round( total_status_no_raio / total_visita_concluded, 2) * 100

    

    st.write("")



      # Exibir as métricas na página
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("✅ Visitas Concluídas", total_visita_concluded)

    with col2:
        st.metric("📍 Visitas no Raio", total_status_no_raio)

    with col3:
        st.metric("🚫 Visitas Fora do Raio", total_fora_raio)
    
    with col4:  
        st.metric("📊 % Visitas no Raio", f"{percentual_dentro_do_raio}%")

# Aumentar o tamanho da fonte no dataframe
    st.markdown(
    """
    <style>
    .dataframe {
        font-size: 18px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

    

    colunass = ['mapa', 'Placa', 'Acessou o raio', 'Ordem Visita', 'Chegada', 'Cod PDV', 'Nome Fantasia', 'Latitude', 'Longitude', 
                               'Estimativa de Chegada', 'Estimativa da Partida', 'Terminou em:', 'Ultimo motivo remarcado',
                               'Ultima razão aguardando modulação', 'Ultimo carimbo de data/hora a caminho',
                               'Ultimo carimbo de data/hora reprogramado', 'Status', 'Valor Total Pedido', 'Volume Total Pedido',
                               'Valor Devolvido', 'Volume Devolvido', 'Valor Total', 'Peso Total', 'Data', 
                               'Soma data/hora de término da viagem', 
                               'Soma Volume', 'Total SKU', 
                               'Tempo de Atendimento', 'Tempo de Espera','data/hora de inicio da viagem','data/hora de término da viagem']
    

    colunasss = ['mapa', 'Placa', 'Acessou o raio', 'Ordem Visita', 'Chegada', 'Cod PDV', 'Nome Fantasia', 
                               'Estimativa de Chegada', 'Estimativa da Partida', 'Terminou em:', 'Ultimo motivo remarcado',
                               'Ultima razão aguardando modulação', 'Ultimo carimbo de data/hora a caminho',
                               'Ultimo carimbo de data/hora reprogramado', 'Status', 'Valor Total Pedido', 'Volume Total Pedido',
                               'Valor Devolvido', 'Volume Devolvido', 'Valor Total', 'Peso Total', 'Data', 
                               'Soma data/hora de término da viagem', 
                               'Soma Volume', 'Total SKU', 
                               'Tempo de Atendimento', 'Tempo de Espera','data/hora de inicio da viagem','data/hora de término da viagem']



    
    df_exibicao =  df_filtrado[colunasss]

# Exibir o DataFrame filtrado com a fonte aumentada
    st.write("Dados Filtrados:")
  #  st.dataframe(df_exibicao, height=500)

    if not df_exibicao.empty:
                # Aumenta a altura da tabela para exibir mais linhas
                num_linhas = len(df_exibicao)
                altura = 1 + min(num_linhas * 35, 600)  # Ajusta a altura com base no número de linhas, até um máximo de 600
                st.dataframe(df_exibicao, use_container_width=True, height=altura)




    st.write("Ranking Aderência PDV:")

    df_ranking = df_exibicao.groupby(['Cod PDV', 'Nome Fantasia']).agg(
    aderencia=('Acessou o raio', lambda x: (x.sum() / len(x)) * 100),  # Calcula a porcentagem de entregas dentro do raio
    num_entregas=('Acessou o raio', 'size'),  # Conta o número total de entregas
    num_entregas_no_raio=('Acessou o raio', 'sum'),  # Soma o número de entregas dentro do raio
    entregas_fora_raio=('Acessou o raio', lambda x: len(x) - x.sum())  # Co # Soma o número de entregas fora do raio
).reset_index()

# Corrigir o nome da coluna e arredondar a aderência
    df_ranking['aderencia'] = df_ranking['aderencia'].round(0)

# Exibir o DataFrame com aderência, número de entregas e entregas fora do raio
    #st.dataframe(df_ranking, height=500)
    if not df_ranking.empty:
                # Aumenta a altura da tabela para exibir mais linhas
                num_linhas = len(df_ranking)
                altura = 1 + min(num_linhas * 35, 600)  # Ajusta a altura com base no número de linhas, até um máximo de 600
                st.dataframe(df_ranking, use_container_width=False, height=altura)





    ultimas_10_entregas = df_filtrado.groupby('Cod PDV').tail(10)
    media_tempo_entrega = ultimas_10_entregas.groupby('Cod PDV')['Tempo de Espera'].mean().reset_index()

    st.write("Tempo médio das ultimas 10 entregas por cliente:")
    #st.write(media_tempo_entrega)
    if not media_tempo_entrega.empty:
                # Aumenta a altura da tabela para exibir mais linhas
                num_linhas = len(media_tempo_entrega)
                altura = 1 + min(num_linhas * 35, 600)  # Ajusta a altura com base no número de linhas, até um máximo de 600
                st.dataframe(media_tempo_entrega, use_container_width=False, height=altura)




   


   

    # RETORNA O TEMPO MÉDIO PDV
    def tempo(pdv):
        return ultimas_10_entregas[ultimas_10_entregas['Cod PDV'] == pdv]['Tempo de Espera'].mean()
    



    st.write("Mapas de Clientes que acessaram o Raio do Cliente:")
    ultimas_10_entregas =  ultimas_10_entregas.dropna(subset=['Latitude', 'Longitude'])
    # Criação do mapa centrado na primeira entrega
    if not ultimas_10_entregas.empty:
        mapa = folium.Map(location=[ultimas_10_entregas.iloc[0]['Latitude'], ultimas_10_entregas.iloc[0]['Longitude']], zoom_start=13)

        # Adicionar marcadores para cada entrega com cor dependendo do within_radius
        for _, entrega in ultimas_10_entregas.iterrows():
            # Determinar a cor do marcador
            cor_marcador = 'green' if entrega['Acessou o raio'] == 1 else 'red'

            # Criar o conteúdo do popup
            popup_content = f"Data: {entrega['Data']}<br>Placa: {entrega['Placa']}<br>Volume: {entrega['Soma Volume']}<br>Fantasia: {entrega['Nome Fantasia']} <br>TM: {tempo(entrega['Cod PDV'])}"

            # Adicionar o marcador ao mapa com um popup de tamanho aumentado
            folium.Marker(
                location=[entrega['Latitude'], entrega['Longitude']],
                popup=folium.Popup(popup_content, max_width=300),  # Aumenta o tamanho do popup
                icon=folium.Icon(color=cor_marcador, icon='info-sign')
            ).add_to(mapa)

        # Converter o mapa para HTML
        mapa_html = mapa._repr_html_()

        # Exibir o mapa diretamente em Streamlit
        st.components.v1.html(mapa_html, height=600)
    else:
        st.write("Nenhuma entrega encontrada para o cliente especificado.")

