
import streamlit as st
import pandas as pd
import numpy as np
import json
import requests
from IPython.display import HTML
import datetime as datetime
from datetime import datetime
import pytz
tz = pytz.timezone("Brazil/East")

if 'count' not in st.session_state:
        st.session_state.count = 0
def increment_counter(increment_value=0):
    st.session_state.count += increment_value

st.sidebar.header("Tft Água")
st.sidebar.image("https://i2.wp.com/gamehall.com.br/wp-content/uploads/2020/03/teamfight-tactics.jpg?fit=1920%2C1080&ssl=1", use_column_width=True)
pesquisa = st.sidebar.text_input("Coloque um nick para pesquisa")
pd.set_option('display.max_colwidth', -1)

st.header ("Team fight tatics Água")
info= st.checkbox("Informações")

if info:
    st.write("Esse aplicativo ainda esta em construção, mas algumas pessoas me pediram e resolvi dar uma adiantada para poder usado.")
    st.write("Atualmente ele esta contando os jogos e pontuação diária com links do lolchesse mobalytics de todos os players que estiverem no Chall/GM no dia anterior")
    st.write("Cada dia as 24hrs as tabelas serão resetadas e começara a mesma conta assim por diante.")
    st.write("Para o futuro eu quero organizar melhor e deixar com um design melhor e adicionar uma parte onde irá ter uma tabela dos snapshots em tempo real")
    st.write("Eu nunca tinha feito um programa para outras pessoas usarem, então não sei o quanto esse servidor gratuito que hospedei aguenta de acessos simulâneos")
    st.write("Então, estou disponibilizando como um teste e com o tempo vou vendo o que da para fazer em relação a isso, se houve algum problema")
    st.write("De resto, espero que isso seja útil de alguma forma, e qualquer feedback só mandar um dm no twitter")
    
    
# def make_clickable(val):
#     return f'<a href="{val}">{val}</a>'

def main ():
    lista_server=["BR1","EUW1","JP1","KR","NA1"]

    server = st.selectbox(
        'Escolha um server?',
        lista_server)
    result=''.join([i for i in server if not i.isdigit()])

    def criar(server):
            
        server = server
        lista_chaa=requests.get(f"https://{server}.api.riotgames.com/tft/league/v1/challenger?api_key=RGAPI-68951cc5-0345-4a6e-af85-d9e541ec159c").json()
        lista_gm=requests.get(f"https://{server}.api.riotgames.com/tft/league/v1/grandmaster?api_key=RGAPI-68951cc5-0345-4a6e-af85-d9e541ec159c").json()

        nick=[]
        for i in range(len(lista_chaa["entries"])):
            nick.append(lista_chaa['entries'][i]["summonerName"])

        lp=[]
        for i in range(len(lista_chaa["entries"])):
            lp.append(lista_chaa['entries'][i]["leaguePoints"])
            
        games=[]
        for i in range(len(lista_chaa["entries"])):
            games.append(lista_chaa["entries"][i]["wins"]+lista_chaa["entries"][i]["losses"])

        df=pd.DataFrame(lp,nick).reset_index().rename(columns={"index":"Nick",0:"League Points"})
        df["Jogos Diários"]=0
        df["Jogos"] = games
        df=df.sort_values("League Points",ascending=False).reset_index(drop=True)  
        nick=[]

        for i in range(len(lista_gm["entries"])):
            
            nick.append(lista_gm['entries'][i]["summonerName"])
        lp=[]
        for i in range(len(lista_gm["entries"])):
            lp.append(lista_gm['entries'][i]["leaguePoints"])
            
        games=[]
        for i in range(len(lista_gm["entries"])):
            games.append(lista_gm["entries"][i]["wins"]+lista_gm["entries"][i]["losses"])

        df1=pd.DataFrame(lp,nick).reset_index().rename(columns={"index":"Nick",0:"League Points"})
        df1["Jogos Diários"]=0
        df1["Jogos"] = games
        df1=df1.sort_values("League Points",ascending=False).reset_index(drop=True)
        dff=df.append(df1).reset_index(drop=True)
        dff.dropna(inplace=True)
        # dff.to_csv(f"dia_ant{server}.csv",index=False)
     
            
        return dff

    def day(server):
        # for server in lista_server:
        dfo=criar(server)
        dia_ant = pd.read_csv(f"dia_ant{server}.csv")
        # dia_ant.index += 1
        df=dfo.merge(dia_ant,how="left",on="Nick")
        parcial=pd.DataFrame()
        parcial["Nick"]=df["Nick"]
        parcial["League Points"]=df["League Points_x"]
        parcial["Jogos Totais"]=df["Jogos_x"]
        parcial["League Points Diários"]=df["League Points_x"]-df["League Points_y"]
        parcial["Partidas Diárias"]=df["Jogos_x"]-df["Jogos_y"]
        parcial=parcial.sort_values("League Points Diários",ascending=False).reset_index(drop=True)
        parcial.sort_values(['League Points Diários', 'League Points'], ascending=[False, False], inplace=True)
        # parcial.index += 1

        
        
        parcial.to_csv(f"parcial{server}.csv")
            
        
    
        return parcial,dfo

    parcial,dfo = day(server)


    if st.button("Calcular lps diários",on_click=increment_counter,kwargs=dict(increment_value=1)):
        

        parcial["Posição"]=np.arange(parcial.shape[0])
        parcial.set_index(parcial["Posição"],inplace=True)
        parcial.drop("Posição",axis=1,inplace=True)
        lolchess=[]
        moba=[]
        for nick in parcial.Nick:
            lolchess.append(f"https://lolchess.gg/profile/{result}/{nick}")
            moba.append(f"https://app.mobalytics.gg/pt_br/tft/profile/{result}/{nick}/overview")
        parcial["lolchess"]=lolchess
        parcial["mobalytics"]=moba
        cols=["Nick", "League Points Diários", "Partidas Diárias", "League Points", "Jogos Totais","lolchess", "mobalytics"]
        parcial = parcial[cols] 
        parcial.rename(columns={"Jogos Totais": "Partidas Totais"},inplace=True)  
#         parcial["League Points Diários"] = parcial["League Points Diários"].astype(int)
        parcial=parcial.dropna()
        parcial["League Points Diários"]=parcial["League Points Diários"].astype(int)
        parcial["Partidas Diárias"]=parcial["Partidas Diárias"].astype(int)
        parcial["League Points"]=parcial["League Points"].astype(int)
        parcial["Partidas Totais"]=parcial["Partidas Totais"].astype(int)
        parcial.index+=1
        st.write(parcial[parcial["Nick"]==pesquisa])
        
        st.write(parcial,unsafe_allow_html=True)
        

    def troca(dfo):
        dia_ant=dfo
        dia_ant = dia_ant.to_csv(f"dia_ant{server}.csv")


        return

    

    # t =  datetime.time(15,56,05)
    # st.write('O dia irá se atualizar na hora:', t)
    # now = datetime.datetime.now()

    # current_time = now.strftime("%H:%M:%S")
    # st.write("Current Time =", current_time)
    
    # txt = st.text_area("")
 
    
    snapi= st.checkbox("Snapshots")
    try:
        if snapi:
            snap3=pd.read_csv("snap3.3.csv",index_col=0)
                    
            snap3=snap3.merge(parcial,how="left",on="Nick")
            # st.write(snap3)
            snap3["Partidas Totais no snap"]=abs(snap3["Jogos Totais"]-snap3["Partidas Totais"])
            snap3.sort_values(by="League Points",ascending=False,inplace=True)
            snap3=snap3.fillna(0)
            # st.write(snap3)
            column_names=["Nick","Ciclo 1","Ciclo 2","Ciclo 3","Partidas Totais no snap","Soma dos pontos do snap"]
            snap3=snap3[column_names]
            # st.write(snap3)
            snap3=snap3.fillna(0)
            
            snap3.iloc[:,1:]=snap3.iloc[:,1:].astype(int)
            snap3.reset_index(inplace=True,drop=True)
            # st.write(snap3)
            snap3.index=snap3.index+1
            snap3.loc[1,"Ciclo 4"]=133
            snap3.loc[2,"Ciclo 4"]=120
            snap3.loc[3,"Ciclo 4"]=106
            snap3.loc[4,"Ciclo 4"]=93
            snap3.loc[5,"Ciclo 4"]=80
            snap3.loc[6,"Ciclo 4"]=73
            snap3.loc[7,"Ciclo 4"]=66
            snap3.loc[8,"Ciclo 4"]=60
            snap3.loc[9:25,"Ciclo 4"]=47
            snap3.loc[26:50,"Ciclo 4"]=34
            snap3.loc[51:100,"Ciclo 4"]=20
            snap3.loc[101:150,"Ciclo 4"]=8
            snap3["Soma dos pontos do snap"]= snap3.loc[:,["Ciclo 1","Ciclo 2","Ciclo 3","Ciclo 4"]].sum(axis=1)
            column_names=["Nick","Ciclo 1","Ciclo 2","Ciclo 3","Ciclo 4","Partidas Totais no snap","Soma dos pontos do snap"]
            snap3=snap3.reindex(columns=column_names)
            snap3.iloc[:,1:]=snap3.iloc[:,1:].astype(int)
            snap3=snap3.sort_values(by="Soma dos pontos do snap",ascending=False)
            snap3.reset_index(drop=True, inplace=True)
            snap3.index=snap3.index+1





            st.write(snap3[snap3["Nick"]==pesquisa])
            st.write(snap3)
    except:
        pass
            # snap.to_csv("snap3.csv")

  
    senha= st.sidebar.text_input("Insira a senha de Admin para atualizar o dia")
    st.write(senha)   
    if senha == "12345":
        if st.button("Atualizar o dia"):
            troca(dfo) 
            st.session_state.count=0  
            now = datetime.now(tz=tz)
            dt_string = now.strftime("%H:%M:%S")
            st.sidebar.write("Horário do reset diário:",dt_string)   
    # if st.button("Atualizar o dia"):
    #     senha= st.number_input("Insira a senha")
    #     st.write(senha)
       
    #     # if senha == "atua":
    #     #     troca(dfo)
    #     #     st.write("Dia Atualizado")
        
    #     # else:
    #     #     st.write("Senha inválida")
    #     # pass

    



# main()



if __name__ == "__main__":

    main()
    st.sidebar.write('Quantas vezes  o app foi utilizado no dia = ', st.session_state.count)



# import schedule
# import time
# hora = st.text_input("Insira um horario")
# parcial = schedule.every().day.at(hora).do(day(server))
# st.write(parcial)



# while 1:
#     schedule.run_pending()
#     time.sleep(1)
