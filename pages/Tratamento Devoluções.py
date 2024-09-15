import streamlit as st
import pandas as pd
import time


def gerar_dados_devolucoes(df_filtrado):
    # Seleciona apenas as colunas relevantes para a exibição
    df = df_filtrado[['Cod PDV', 'Status', 'data/hora de término da viagem']].copy()
    df.rename(columns={'Cod PDV': 'Cliente', 'data/hora de término da viagem': 'Horário'}, inplace=True)


    status_icons = {
        'Aguardando': '⏳',  # Emoji de ampulheta
        'Em Tratamento': '⚙️',  # Emoji de engrenagem
        'Finalizado': '✅',  # Emoji de check
        'CONCLUDED': '✅',   # Caso existam outros status específicos no df_filtrado
    }
    df['Status'] = df['Status'].map(lambda x: f"{status_icons.get(x, '')} {x}")
    return df


st.set_page_config(page_title="Painel de Devoluções", layout="wide")
st.title("Painel de Devoluções - Aguardando Tratamento")

# CSS personalizado para ajustar a largura da tabela
st.markdown(
    """
    <style>
    .dataframe {
        width: 100%;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Recuperando o df_filtrado do cache (carregado na página Home)
if 'df_filtrado' in st.session_state:
    df_filtrado = st.session_state['df_filtrado']
    
    # Atualização automática a cada 30 segundos
    placeholder = st.empty()

    while True:
        # Chama a função para gerar a tabela com o DataFrame filtrado
        df = gerar_dados_devolucoes(df_filtrado)

        with placeholder.container():
            st.subheader("Devoluções Aguardando Tratamento")

            # Verifica se o DataFrame não está vazio antes de tentar exibir
            if not df.empty:
                # Aumenta a altura da tabela para exibir mais linhas
                num_linhas = len(df)
                altura = 200 + min(num_linhas * 35, 500)  # Ajusta a altura com base no número de linhas, até um máximo de 600
                st.dataframe(df[['Cliente', 'Status', 'Horário']], use_container_width=True, height=altura)
            else:
                st.write("Nenhuma devolução encontrada para os critérios selecionados.")

            # Adicionando um cronômetro para atualizar os dados
            st.write("Atualizando em 30 segundos...")
            time.sleep(30)
else:
    st.error("Os dados do df_filtrado não foram carregados na página Home.")