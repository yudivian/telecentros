import streamlit as st
import json
import unicodedata
from datetime import datetime , timedelta


st.title("Telecentros  - Explorador")

def normalize(text):
    t = unicodedata.normalize('NFD', text)
    t = ''.join(c for c in t if unicodedata.category(c) != 'Mn')
    return t.lower()

files = {
    "pr": "tele-pinar-v2-llama.json",
    "ar": "artv-v2-llama.json",
    "ij": "islavision-v2-llama.json",
    "lh": "canal-habana-v2-llama.json",
    "my": "tele-mayabeque-v2-llama.json",
    "mt": "tv-yumuri-v2-llama.json",
    "cf": "perlavision-v2-llama.json",
    "vc": "tele-cubanacan-v2-llama.json",
    "ss": "centrovision-v2-llama.json",
    "ca": "tv-avilena-v2-llama.json",
    "cm": "tv-camaguey-v2-llama.json",
    "lt": "tunasvision-v2-llama.json",
    "hg": "tele-cristal-v2-llama.json",
    "gr": "cnc-granma-v2-llama.json",
    "sc": "tv-santiago-v2-llama.json",
    "gt": "solvision-v2-llama.json",
    # "ts": "tv-serrana-v2-llama.json",
}

tc = {
    "Todos": "all",
    "Tele Pinar": "pr",
    "ArTV": "ar",
    "Islavision": "ij",
    "Canal Habana": "lh",
    "Tele Mayabeque": "my",
    "Tele Yumurí": "mt",
    "Telecubanacán": "vc",
    "Perlavisión": "cf",
    "Centrovisión": "ss",
    "TV Avileña": "ca",
    "TV Camagüey": "cm",
    "Tunasvisión": "lt",
    "Tele Cristal": "hg",
    "CNC Granma": "gr",
    "TV Santiago": "sc",
    "Solvisión": "gt",
    # "TV Serrana": "ts",
}

data = {}

for key, filename in files.items():
    with open("data/" + filename, "r") as file:
        d = json.load(file)
        for i in d:
            i["tc"] = key
            if i["check"]:
                data[i["link"]] = i

with st.container(border=True):
    st.markdown("**Explora los videos**")
    selected_keys = st.multiselect(
        "Seleciona los telecentros a analizar:",
        list(tc.keys()),
        key="total_multiselect",
    )
    ndata = {}
    if selected_keys:
        if not ("Todos" in selected_keys):
            for k,p in data.items():
                if p["tc"] in [tc[i] for i in selected_keys]:
                    ndata[k]=p
        else:
            ndata = data
        dates = []
        for d in ndata.values():
            dates.append(d["date"])
        dates.sort()
        start_date = datetime.fromisoformat(dates[0])
        end_date = datetime.fromisoformat(dates[-1])
        selected_date_range = st.slider(
            "Selecciona el rango de fechas:",
            min_value=start_date,
            max_value=end_date,
            value=(start_date, end_date),  
            step=timedelta(days=1),  
            format="YYYY-MM-DD"  
        )
        start = selected_date_range[0]
        end = selected_date_range[-1]
        ndata = {k:p for k,p in ndata.items() if start <= datetime.fromisoformat(p["date"]) <= end}
        vis = [i["views"] for i in ndata.values()]
        minvis = min(vis)
        maxvis = max(vis)
        vis_range = st.slider(
            "Selecciona el rango de visualizaciones:",
            min_value=minvis,
            max_value=maxvis,
            value=(minvis, maxvis),  
            step=1
        )
        ndata = {k:p for k,p in ndata.items() if vis_range[0] <= p["views"] <= vis_range[1]}
        dur = [i["duration"] for i in ndata.values()]
        mindur = min(dur)
        maxdur = max(dur)
        dur_range = st.slider(
            "Selecciona el rango de visualizaciones:",
            min_value=mindur,
            max_value=maxdur,
            value=(mindur, maxdur),  
            step=1
        )
        ndata = {k:p for k,p in ndata.items() if dur_range[0] <= p["duration"] <= dur_range[1]} 
        st.divider()
        hcol1, hcol2 = st.columns(2)
        with hcol1:
            st.markdown("Resultados: "+str(len(ndata)))
        with hcol2:
            filter = st.text_input("Filtrar:")
            if filter:
                filter_norm = normalize(filter)
                fdata = {}
                for k,p in ndata.items():
                    for d in ["title","snippet","transcript"]:
                        if (d in p) and p[d]!=None:
                            if filter_norm in normalize(p[d]):
                                fdata[k]=p
                                break
                ndata = fdata
        rtc = {p:k for k,p in tc.items() if k!="Todos"}
        for p in ndata.values():
            with st.expander(p["title"]):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(rtc[p["tc"]])
                with col2:
                    st.markdown("Vistas: "+str(p["views"]))
                with col3:
                    st.markdown("Duración: "+str(p["duration"]))
                st.video(p["link"])
                st.markdown("**Lead:**")
                st.markdown(p["snippet"])
                if p["transcript"]:
                    st.markdown("**Transcripción:**")
                    st.markdown(p["transcript"])