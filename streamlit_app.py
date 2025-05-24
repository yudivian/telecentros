import streamlit as st
import json
import statistics
import plotly.graph_objects as go
from datetime import datetime , timedelta

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
    "ts": "tv-serrana-v2-llama.json",
}

tc = {
    "Todos": "all",
    "ArTV": "ar",
    "Canal Habana": "lh",
    "Centrovisión": "ss",
    "CNC Granma": "gr",
    "Islavision": "ij",
    "Perlavisión": "cf",
    "Solvisión": "gt",
    "Tele Cristal": "hg",
    "Telecubanacán": "vc",
    "Tele Mayabeque": "my",
    "Tele Pinar": "pr",
    "Tele Yumurí": "mt",
    "Tunasvisión": "lt",
    "TV Avileña": "ca",
    "TV Camagüey": "cm",
    "TV Santiago": "sc",
    "TV Serrana": "ts",
}

st_names = {"Media": "mean", "Mediana": "median", "Moda": "mode"}


data = {}


for key, filename in files.items():
    with open("data/" + filename, "r") as file:
        data[key] = json.load(file)


data["all"] = [entry for entries in data.values() for entry in entries]

st.title("Telecentros  - Dashboard")


def stats(serie, key):
    values = [d[key] for d in serie]

    return {
        "mean": statistics.mean(values),
        "median": statistics.median(values),
        "mode": statistics.mode(values),
        "stdev": statistics.stdev(values),
    }


with st.container(border=True):
    st.markdown("**Número de programas**")
    selected_keys = st.multiselect(
        "Seleciona los telecentros a analizar:",
        list(tc.keys()),
        key="total_multiselect",
    )
    if selected_keys:
        dates = []
        for k in selected_keys:
            for d in data[tc[k]]:
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
        selected_type = st.selectbox(
            "Selecciona el tipo:",
            list(["Porciento","Cantidad"]),
            key="pn_select",
        )
        fig = go.Figure()
        
        subcat = ["MA", "No MA"]
        subcat_vals = {x: [] for x in subcat}
        for c in selected_keys:
            ma_items = len([ i for i in data[tc[c]] if i["check"] and (start < datetime.fromisoformat(i["date"]) < end)])
            nma_items = len([ i for i in data[tc[c]] if (not i["check"]) and (start < datetime.fromisoformat(i["date"]) < end)])
            if selected_type=="Porciento":
                ma_items = round(ma_items*100/(ma_items+nma_items),2)
                nma_items = 100 - ma_items 
            subcat_vals["MA"].append(ma_items)
            subcat_vals["No MA"].append(nma_items)
            
        for sc in subcat:
            fig.add_trace(
                go.Bar(
                    name=sc,
                    x=selected_keys,
                    y=subcat_vals[sc],
                    text=[f"{sc}: {v}" for v in subcat_vals[sc]],
                    textposition="auto",
                )
            )
            
        fig.update_layout(
                barmode="stack",
                xaxis_title="Telecentros",
                yaxis_title="Programas en "+selected_type.lower(),
            )

        st.plotly_chart(fig, use_container_width=True)

        
    
with st.container(border=True):
    st.markdown("**Duración de los programas**")
    selected_keys = st.multiselect(
        "Seleciona los telecentros a analizar:",
        list(tc.keys()),
        key="duration_multiselect",
    )
    if selected_keys:
        selected_stat = st.selectbox(
            "Selecciona la estadística a mostrar:",
            list(st_names.keys()),
            key="duration_select",
        )
        if selected_stat:
            s_stat = st_names[selected_stat]
            categories = selected_keys
            subcat = ["Todos", "No MA", "MA"]
            subcat_vals = {x: [] for x in subcat}
            for c in categories:
                d = data[tc[c]]
                st_all = stats([i for i in d], "duration")
                st_ma = stats([i for i in d if i["check"]], "duration")
                st_nma = stats([i for i in d if not i["check"]], "duration")
                subcat_vals["Todos"].append(round(st_all[s_stat]))
                subcat_vals["MA"].append(round(st_ma[s_stat]))
                subcat_vals["No MA"].append(round(st_nma[s_stat]))

            fig = go.Figure()

            for sc in subcat:
                fig.add_trace(
                    go.Bar(
                        name=sc,
                        x=categories,
                        y=subcat_vals[sc],
                        text=[f"{sc}: {v}" for v in subcat_vals[sc]],
                        textposition="auto",
                    )
                )

            fig.update_layout(
                barmode="group",
                xaxis_title="Telecentros",
                yaxis_title="Duración en segundos",
            )

            st.plotly_chart(fig, use_container_width=True)


with st.container(border=True):
    st.markdown("**Visualizaciones de los programas**")
    selected_keys = st.multiselect(
        "Seleciona los telecentros a analizar:", list(tc.keys()),key="likes_multselect",
    )
    if selected_keys:
        selected_stat = st.selectbox(
            "Selecciona la estadística a mostrar:", list(st_names.keys()),key="likes_select",
        )
        if selected_stat:
            s_stat = st_names[selected_stat]
            categories = selected_keys
            subcat = ["Todos", "No MA", "MA"]
            subcat_vals = {x: [] for x in subcat}
            for c in categories:
                d = data[tc[c]]
                st_all = stats([i for i in d], "views")
                st_ma = stats([i for i in d if i["check"]], "views")
                st_nma = stats([i for i in d if not i["check"]], "views")
                subcat_vals["Todos"].append(round(st_all[s_stat]))
                subcat_vals["MA"].append(round(st_ma[s_stat]))
                subcat_vals["No MA"].append(round(st_nma[s_stat]))

            fig2 = go.Figure()

            for sc in subcat:
                fig2.add_trace(
                    go.Bar(
                        name=sc,
                        x=categories,
                        y=subcat_vals[sc],
                        text=[f"{sc}: {v}" for v in subcat_vals[sc]],
                        textposition="auto",
                    )
                )

            fig2.update_layout(
                barmode="group",
                xaxis_title="Telecentros",
                yaxis_title="Visualizaciones",
            )

            st.plotly_chart(fig2, use_container_width=True)
