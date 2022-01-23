import streamlit as st
import pandas as pd
import numpy as np
import json
import requests
from IPython.display import HTML
import datetime 
import pytz
tz = pytz.timezone("Brazil/East")


# def increment_counter(increment_value=0):
#     st.session_state.count += increment_value

st.sidebar.header("tft_region_analitycs")
st.sidebar.image("https://i2.wp.com/gamehall.com.br/wp-content/uploads/2020/03/teamfight-tactics.jpg?fit=1920%2C1080&ssl=1", use_column_width=True)
pesquisa = st.sidebar.text_input("Input your nick for search")
pd.set_option('display.max_colwidth', -1)

st.header ("Team fight tatics region analitycs")
info= st.checkbox("Information")

if info:
    st.write("This app is still under construction, but some people asked me and I decided to give it a head start to be able to use it.")
    st.write("He is currently counting games and daily scores with lolchesse mobalytics links from all players who were in Chall/GM the day before")
    st.write("Every day at 24hrs the tables will be reset and the same account will start and so on.")
    st.write("It also has server br snapshot scores updated in real time")
    st.write("So, I'm making it available as a test and over time I'll see what I can do about it, if there were any problems")
    st.write("Otherwise, I hope this is useful in some way, and any feedback just send a dm on twitter")
    st.write(" [Twitter](https://twitter.com/Arthurlinsz)")
    
    
# def make_clickable(val):
#     return f'<a href="{val}">{val}</a>'

def main ():

    lista_server=["BR1","EUW1","JP1","KR","NA1"]

    server = st.selectbox(
        'Choose a server?',
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
        df["Daily Games"]=0
        df["Games"] = games
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
        df1["Daily Games"]=0
        df1["Games"] = games
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
        parcial["Total Games"]=df["Games_x"]
        parcial["Daily League Points"]=df["League Points_x"]-df["League Points_y"]
        parcial["Daily Games"]=df["Games_x"]-df["Games_y"]
        parcial=parcial.sort_values("Daily League Points",ascending=False).reset_index(drop=True)
        parcial.sort_values(['Daily League Points', 'League Points'], ascending=[False, False], inplace=True)
        # parcial.index += 1

        
        
        parcial.to_csv(f"parcial{server}.csv")
            
        
    
        return parcial,dfo

    parcial,dfo = day(server)


    if st.button("Calculate daily lps"):
        
        with open('count.txt',"r") as f:
            contents = f.read()
        count=int(contents.split("=")[-1])
        count=count+1
        # print(f"The program was used {count} times today")
        with open('count.txt',"w") as f:
            f.write(f'count={count}')
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
        cols=["Nick", "Daily League Points", "Daily Games", "League Points", "Total Games","lolchess", "mobalytics"]
        
        parcial = parcial[cols] 
        parcial.rename(columns={"Total Games": "Total Matches"},inplace=True)  
#         parcial["League Points Diários"] = parcial["League Points Diários"].astype(int)
        parcial=parcial.dropna()
        parcial["Daily League Points"]=parcial["Daily League Points"].astype(int)
        parcial["Daily Games"]=parcial["Daily Games"].astype(int)
        parcial["League Points"]=parcial["League Points"].astype(int)
        parcial["Total Matches"]=parcial["Total Matches"].astype(int)
        parcial.index+=1
        st.write(parcial[parcial["Nick"]==pesquisa])
        
        st.write(parcial, unsafe_allow_html=True)
        # st.write(parcial.to_html(escape=False, index=False),unsafe_allow_html=True)
        
        st.sidebar.write(f"The program was used {count} times today")

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
            if server =="BR1":
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
                cols=["Nick", "Daily League Points", "Daily Games", "League Points", "Total Games","lolchess", "mobalytics"]
                
                parcial = parcial[cols] 
                parcial.rename(columns={"Total Games": "Total Matches"},inplace=True)  
        #         parcial["League Points Diários"] = parcial["League Points Diários"].astype(int)
                parcial=parcial.dropna()
                parcial["Daily League Points"]=parcial["Daily League Points"].astype(int)
                parcial["Daily Games"]=parcial["Daily Games"].astype(int)
                parcial["League Points"]=parcial["League Points"].astype(int)
                parcial["Total Matches"]=parcial["Total Matches"].astype(int)
                parcial.index+=1
                st.write(parcial[parcial["Nick"]==pesquisa])
                
                st.write(parcial, unsafe_allow_html=True)
                snap3=pd.read_csv("snap3.3.csv",index_col=0)
                        
                snap3=snap3.merge(parcial,how="left",on="Nick")
                # st.write(snap3)
                snap3["Total games in snap"]=abs(snap3["Daily Games_x"]-snap3["Total Matches"])
                snap3.sort_values(by="League Points",ascending=False,inplace=True)
                snap3=snap3.fillna(0)
                # st.write(snap3)
                column_names=["Nick","Cycle 1","Cycle 2","Cycle 3","Total games in snap","Sum of snapshot points"]
                snap3=snap3[column_names]
                # st.write(snap3)
                snap3=snap3.fillna(0)
                
                snap3.iloc[:,1:]=snap3.iloc[:,1:].astype(int)
                snap3.reset_index(inplace=True,drop=True)
                # st.write(snap3)
                snap3.index=snap3.index+1
                snap3.loc[1,"Cycle 4"]=133
                snap3.loc[2,"Cycle 4"]=120
                snap3.loc[3,"Cycle 4"]=106
                snap3.loc[4,"Cycle 4"]=93
                snap3.loc[5,"Cycle 4"]=80
                snap3.loc[6,"Cycle 4"]=73
                snap3.loc[7,"Cycle 4"]=66
                snap3.loc[8,"Cycle 4"]=60
                snap3.loc[9:25,"Cycle 4"]=47
                snap3.loc[26:50,"Cycle 4"]=34
                snap3.loc[51:100,"Cycle 4"]=20
                snap3.loc[101:150,"Cycle 4"]=8
                snap3["Sum of snapshot points"]= snap3.loc[:,["Cycle 1","Cycle 2","Cycle 3","Cycle 4"]].sum(axis=1)
                column_names=["Nick","Cycle 1","Cycle 2","Cycle 3","Cycle 4","Total games in snap","Sum of snapshot points"]
                snap3=snap3.reindex(columns=column_names)
                snap3.iloc[:,1:]=snap3.iloc[:,1:].astype(int)
                snap3=snap3.sort_values(by="Sum of snapshot points",ascending=False)
                snap3.reset_index(drop=True, inplace=True)
                snap3.index=snap3.index+1





                st.write(snap3[snap3["Nick"]==pesquisa])
                st.write(snap3)
    except:
        pass
            # snap.to_csv("snap3.csv")
    qualify = st.checkbox("Qualify Points:")
    if qualify:
        if server =="BR1":
            qualify_points=pd.read_csv("qualify_t.csv")
            st.write(qualify_points)
        else:
            pass
  
    senha= st.sidebar.text_input("Enter Admin password to update day")
    st.write(senha)
    
    # st.sidebar.number_input("coloque o numero")
    
    if senha == "12345":
        if st.button("Update the day"):
            with open('count.txt',"r") as f:
                contents = f.read()
            count=int(contents.split("=")[-1])
            count=0
            # print(f"The program was used {count} times today")
            with open('count.txt',"w") as f:
                f.write(f'count={count}')
            troca(dfo) 
            # st.session_state.count=0  
            tz = pytz.timezone("Brazil/East")
            time_now=datetime.datetime.now(tz).time()
            
            current_time = time_now.strftime("%H:%M:%S")
            with open('current_time.txt',"w") as f:
                f.write(f'current_time={current_time}')
    with open('count.txt',"r") as f:
        contents = f.read()
    count=int(contents.split("=")[-1])
    with open('current_time.txt',"r") as f:
        current_time = f.read()
    current_time=current_time.split("=")[-1]
    st.sidebar.write(f"The program was used {count} times today")
    st.sidebar.write("The time this program was reset was :",current_time,"Brazil/East")   
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
            

    # st.sidebar.write('Quantas vezes  o app foi utilizado no dia = ', st.write(count))



# import schedule
# import time
# hora = st.text_input("Insira um horario")
# parcial = schedule.every().day.at(hora).do(day(server))
# st.write(parcial)



# while 1:
#     schedule.run_pending()
#     time.sleep(1)

