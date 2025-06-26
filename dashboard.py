import streamlit as st
import json
import statistics
import calendar
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import string
import plotly.graph_objects as go
from datetime import datetime, timedelta

with open("stopwords-es.json", "r") as jfile:
    swes = json.load(jfile)
    stopwords_es = set(swes)

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

st_names = {"Media": "mean", "Mediana": "median", "Moda": "mode"}


data = {}


for key, filename in files.items():
    with open("data/" + filename, "r") as file:
        data[key] = json.load(file)


data["all"] = [entry for entries in data.values() for entry in entries]

st.title("Telecentros  - Dashboard")


def preprocess_text(text):
    text = text.lower().translate(
        str.maketrans("", "", string.punctuation + "0123456789")
    )
    tokens = [word for word in text.split() if word not in stopwords_es]
    return tokens


def generate_wordcloud(tokens, words=100, ngram=1):
    if ngram == 1:
        text_data = " ".join(tokens)
    else:
        bigrams = ["_".join(tokens[i : i + 2]) for i in range(len(tokens) - 1)]
        text_data = " ".join(bigrams)
    wordcloud = WordCloud(
        width=800,
        height=400,
        background_color="white",
        collocation_threshold=30,
        max_words=words,
    ).generate(text_data)
    return wordcloud


def stats(serie, key):
    values = [d[key] for d in serie]

    return {
        "mean": statistics.mean(values),
        "median": statistics.median(values),
        "mode": statistics.mode(values),
        "stdev": statistics.stdev(values),
        "sum": sum(values),
    }


def get_date_number(strdate):
    date = datetime.fromisoformat(strdate)
    if date.tzinfo is not None:
        date = date.replace(tzinfo=None)
    jan1 = datetime(date.year, 1, 1)
    feb28 = datetime(date.year, 2, 28)
    days = (date - jan1).days + 1
    if (not calendar.isleap(date.year)) and (date > feb28):
        days += 1
    return days


def get_number_date(numday):
    if numday == 60:
        return "29/2"
    jan1 = datetime(2025, 1, 1)
    if numday < 60:
        date = jan1 + timedelta(days=numday - 1)
        return str(date.day) + "/" + str(date.month)
    date = jan1 + timedelta(days=numday - 2)
    return str(date.day) + "/" + str(date.month)

def get_period_date(strdate):
    date = datetime.fromisoformat(strdate)
    return str(date.day) + "/" + str(date.month)+"/"+str(date.year)

with st.container(border=True):
    st.markdown("**Número de videos**")
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
            format="YYYY-MM-DD",
        )
        start = selected_date_range[0]
        end = selected_date_range[-1]
        selected_type = st.selectbox(
            "Selecciona el tipo:",
            list(["Porciento", "Cantidad"]),
            key="pn_select",
        )
        fig = go.Figure()

        subcat = ["MA", "No MA"]
        subcat_vals = {x: [] for x in subcat}
        for c in selected_keys:
            ma_items = len(
                [
                    i
                    for i in data[tc[c]]
                    if i["check"]
                    and (start <= datetime.fromisoformat(i["date"]) <= end)
                ]
            )
            nma_items = len(
                [
                    i
                    for i in data[tc[c]]
                    if (not i["check"])
                    and (start <= datetime.fromisoformat(i["date"]) <= end)
                ]
            )
            if selected_type == "Porciento":
                ma_items = round(ma_items * 100 / (ma_items + nma_items), 2)
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
            yaxis_title="Videos en " + selected_type.lower(),
        )

        st.plotly_chart(fig, use_container_width=True)

with st.container(border=True):
    st.markdown("**Duración total de los videos**")
    selected_keys = st.multiselect(
        "Seleciona los telecentros a analizar:",
        list(tc.keys()),
        key="duration_total_multiselect",
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
            format="YYYY-MM-DD",
            key="duration_total_date_slider",
        )
        start = selected_date_range[0]
        end = selected_date_range[-1]
        selected_type = st.selectbox(
            "Selecciona el tipo:",
            list(["Porciento", "Cantidad"]),
            key="dt_select",
        )
        if selected_type:
            categories = selected_keys
            subcat = ["MA", "No MA"]
            subcat_vals = {x: [] for x in subcat}
            for c in categories:
                d = data[tc[c]]
                item_all = [
                    i for i in d if (start < datetime.fromisoformat(i["date"]) < end)
                ]
                st_all = stats(item_all, "duration")["sum"]
                item_ma = [
                    i
                    for i in d
                    if i["check"]
                    and (start <= datetime.fromisoformat(i["date"]) <= end)
                ]
                st_ma = stats(item_ma, "duration")["sum"]
                item_nma = [
                    i
                    for i in d
                    if not i["check"]
                    and (start <= datetime.fromisoformat(i["date"]) <= end)
                ]
                st_nma = stats(item_nma, "duration")["sum"]
                if selected_type == "Porciento":
                    st_ma = round(st_ma * 100 / st_all, 2)
                    st_nma = 100 - st_ma
                subcat_vals["MA"].append(st_ma)
                subcat_vals["No MA"].append(st_nma)

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
                barmode="stack",
                xaxis_title="Telecentros",
                yaxis_title="Duración en segundos (" + selected_type + ")",
            )

            st.plotly_chart(fig, use_container_width=True)

with st.container(border=True):
    st.markdown("**Duración promedio de los videos**")
    selected_keys = st.multiselect(
        "Seleciona los telecentros a analizar:",
        list(tc.keys()),
        key="duration_multiselect",
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
            format="YYYY-MM-DD",
            key="duration_date_slider",
        )
        start = selected_date_range[0]
        end = selected_date_range[-1]
        selected_stat = st.selectbox(
            "Selecciona la estadística a mostrar:",
            list(st_names.keys()),
            key="duration_select",
        )
        if selected_stat:
            s_stat = st_names[selected_stat]
            categories = selected_keys
            subcat = ["MA", "No MA", "Todos"]
            subcat_vals = {x: [] for x in subcat}
            for c in categories:
                d = data[tc[c]]
                st_all = stats(
                    [
                        i
                        for i in d
                        if (start <= datetime.fromisoformat(i["date"]) <= end)
                    ],
                    "duration",
                )
                st_ma = stats(
                    [
                        i
                        for i in d
                        if i["check"]
                        and (start <= datetime.fromisoformat(i["date"]) <= end)
                    ],
                    "duration",
                )
                st_nma = stats(
                    [
                        i
                        for i in d
                        if not i["check"]
                        and (start <= datetime.fromisoformat(i["date"]) <= end)
                    ],
                    "duration",
                )
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
    st.markdown("**Visualizaciones de los videos**")
    selected_keys = st.multiselect(
        "Seleciona los telecentros a analizar:",
        list(tc.keys()),
        key="likes_multselect",
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
            format="YYYY-MM-DD",
            key="likes_date_slider",
        )
        start = selected_date_range[0]
        end = selected_date_range[-1]
        selected_stat = st.selectbox(
            "Selecciona la estadística a mostrar:",
            list(st_names.keys()),
            key="likes_select",
        )
        if selected_stat:
            s_stat = st_names[selected_stat]
            categories = selected_keys
            subcat = ["MA", "No MA", "Todos"]
            subcat_vals = {x: [] for x in subcat}
            for c in categories:
                d = data[tc[c]]
                st_all = stats(
                    [
                        i
                        for i in d
                        if (start <= datetime.fromisoformat(i["date"]) <= end)
                    ],
                    "views",
                )
                st_ma = stats(
                    [
                        i
                        for i in d
                        if i["check"]
                        and (start <= datetime.fromisoformat(i["date"]) <= end)
                    ],
                    "views",
                )
                st_nma = stats(
                    [
                        i
                        for i in d
                        if not i["check"]
                        and (start <= datetime.fromisoformat(i["date"]) <= end)
                    ],
                    "views",
                )
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

with st.container(border=True):
    st.markdown("**Distribución de los videos por día de la semana**")
    selected_keys = st.multiselect(
        "Seleciona los telecentros a analizar:",
        list(tc.keys()),
        key="weekday_multiselect",
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
            format="YYYY-MM-DD",
            key="week_date_slider",
        )
        start = selected_date_range[0]
        end = selected_date_range[-1]
        categories = selected_keys
        week_days = [
            "Lunes",
            "Martes",
            "Miercoles",
            "Jueves",
            "Viernes",
            "Sábado",
            "Domingo",
        ]
        selected_type = st.selectbox(
            "Selecciona cual tipo de video mostrar:",
            list(["Medio Ambiente", "No Medio Ambiente", "Todos"]),
            key="wd_type_select",
        )
        days = {}
        for c in categories:
            days[c] = {
                "Lunes": 0,
                "Martes": 0,
                "Miercoles": 0,
                "Jueves": 0,
                "Viernes": 0,
                "Sábado": 0,
                "Domingo": 0,
            }
            d = data[tc[c]]
            lp = []
            for i in d:
                check = True
                if selected_type=="Medio Ambiente":
                    check = i["check"]
                elif selected_type=="No Medio Ambiente":
                    check = not i["check"]
                if check and (start <= datetime.fromisoformat(i["date"]) <= end):
                    lp.append(i)
            for p in lp:
                index_day = datetime.fromisoformat(p["date"]).weekday()
                days[c][week_days[index_day]] += 1

        selected_type = st.selectbox(
            "Selecciona el modo de graficar:",
            list(["Apilados", "Uno a uno"]),
            key="wd_select",
        )
        fig = go.Figure()
        # Single bar (not stacked) - offsetgroup "group1"
        for key, week in days.items():
            wdays = []
            ndays = []
            for wd, nd in week.items():
                wdays.append(wd)
                ndays.append(nd)
            group = "resto"
            if selected_type == "Uno a uno":
                group = key
            if key == "Todos":
                group = "todos"
            fig.add_trace(go.Bar(x=wdays, y=ndays, name=key, offsetgroup=group))

        fig.update_layout(
            barmode="stack",
            xaxis_title="Día de la Semana",
            yaxis_title="Número de videos",
        )

        st.plotly_chart(fig, use_container_width=True)

with st.container(border=True):
    st.markdown("**Distribución de los videos por día del año**")
    s_key = st.selectbox(
        "Seleciona el telecentro a analizar:",
        list(tc.keys()),
        key="yearday_select",
    )
    if s_key:
        dates = []
        for d in data[tc[s_key]]:
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
            format="YYYY-MM-DD",
            key="dy_slider",
        )
        start = selected_date_range[0]
        end = selected_date_range[-1]
        ma_ydays = {i: 0 for i in range(1, 367)}
        d = data[tc[s_key]]
        selected_type = st.selectbox(
            "Selecciona cual tipo de video mostrar:",
            list(["Medio Ambiente", "No Medio Ambiente", "Todos"]),
            key="yd_select",
        )
        lp = []
        for i in d:
            check = True
            if selected_type=="Medio Ambiente":
                check = i["check"]
            elif selected_type=="No Medio Ambiente":
                check = not i["check"]
            if check and (start <= datetime.fromisoformat(i["date"]) <= end):
                lp.append(i)
        for p in lp:
            index_day = get_date_number(p["date"])
            ma_ydays[index_day] += 1
        fig = go.Figure()
        # Single bar (not stacked) - offsetgroup "group1"
        ydays = []
        ndays = []
        for key, num in ma_ydays.items():
            ydays.append(key)
            ndays.append(num)

        fig.add_trace(go.Bar(x=[get_number_date(i) for i in range(1, 367)], y=ndays))

        fig.update_layout(
            barmode="group",
            xaxis_title="Día del año",
            yaxis_title="Número de videos",
        )

        st.plotly_chart(fig, use_container_width=True)
        
with st.container(border=True):
    st.markdown("**Distribución de los videos por días del período**")
    s_key = st.selectbox(
        "Seleciona el telecentro a analizar:",
        list(tc.keys()),
        key="period_select",
    )
    if s_key:
        dates = []
        for d in data[tc[s_key]]:
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
            format="YYYY-MM-DD",
            key="period_slider",
        )
        start = selected_date_range[0]
        end = selected_date_range[-1]
        # ma_ydays = {i: 0 for i in range(1, 367)}
        ma_ydays = {get_period_date((start + timedelta(days=x)).isoformat()):0 for x in range((end - start).days + 1)}
        
        d = data[tc[s_key]]
        selected_type = st.selectbox(
            "Selecciona cual tipo de video mostrar:",
            list(["Medio Ambiente", "No Medio Ambiente", "Todos"]),
            key="period_type_select",
        )
        lp = []
        for i in d:
            check = True
            if selected_type=="Medio Ambiente":
                check = i["check"]
            elif selected_type=="No Medio Ambiente":
                check = not i["check"]
            if check and (start <= datetime.fromisoformat(i["date"]) <= end):
                lp.append(i)
        for p in lp:
            index_day = get_period_date(p["date"])
            ma_ydays[index_day] += 1
        fig = go.Figure()
        ydays = []
        ndays = []
        for key, num in ma_ydays.items():
            ydays.append(key)
            ndays.append(num)

        fig.add_trace(go.Bar(x=ydays, y=ndays))

        fig.update_layout(
            barmode="group",
            xaxis_title="Día",
            yaxis_title="Número de videos",
        )

        st.plotly_chart(fig, use_container_width=True)

with st.container(border=True):
    st.markdown("**Videos de MA relativos a la celebración de un Día especial**")
    selected_keys = st.multiselect(
        "Seleciona los telecentros a analizar:",
        list(tc.keys()),
        key="celeeb_day__multiselect",
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
            format="YYYY-MM-DD",
            key="celeb_day_date_slider",
        )
        start = selected_date_range[0]
        end = selected_date_range[-1]
        selected_type = st.selectbox(
            "Selecciona el tipo:",
            list(["Porciento", "Cantidad"]),
            key="cd_select",
        )
        if selected_type:
            categories = selected_keys
            subcat = ["Día", "No Día"]
            subcat_vals = {x: [] for x in subcat}
            for c in categories:
                d = data[tc[c]]
                item_all = len(
                    [
                        i
                        for i in d
                        if i["check"]
                        and (start <= datetime.fromisoformat(i["date"]) <= end)
                    ]
                )
                item_day = len(
                    [
                        i
                        for i in d
                        if i["check"]
                        and i["day_celebration"]
                        and (start <= datetime.fromisoformat(i["date"]) <= end)
                    ]
                )
                item_nday = item_all - item_day
                if selected_type == "Porciento":
                    item_day = round(item_day * 100 / item_all, 2)
                    item_nday = 100 - item_day
                subcat_vals["Día"].append(item_day)
                subcat_vals["No Día"].append(item_nday)

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
                barmode="stack",
                xaxis_title="Telecentros",
                yaxis_title="Videos (" + selected_type + ")",
            )

            st.plotly_chart(fig, use_container_width=True)


with st.container(border=True):
    st.markdown("**Nubes de etiquetas del contenido de los videos por telecentro**")
    s_key = st.selectbox(
        "Seleciona el telecentro a analizar:",
        list(tc.keys()),
        key="wc_select",
    )
    if s_key:
        dates = []
        for d in data[tc[s_key]]:
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
            format="YYYY-MM-DD",
            key="wc_slider",
        )
        start = selected_date_range[0]
        end = selected_date_range[-1]
        words = st.slider(
            "Selecciona la cantidad de palabras:",
            min_value=40,
            max_value=300,
            value=150,
            step=1,
        )
        s_type = st.selectbox(
            "Seleciona el texto a usar:",
            ["Título + Texto", "Título", "Texto"],
            key="wc_type select",
        )
        d = data[tc[s_key]]
        lp = [
            i
            for i in d
            if i["check"] and (start <= datetime.fromisoformat(i["date"]) <= end)
        ]
        text = " "
        for p in lp:
            title = p["title"]
            trans = ""
            if "transcript" in p:
                trans = p["transcript"] if p["transcript"] != None else ""
            if s_type == "Título + Texto":
                text += title + " " + trans + " "
            elif s_type == "Título":
                text += title + " "
            else:
                text += trans + " "

        tokens = preprocess_text(text)
        wc = generate_wordcloud(tokens, words=words)
        fig, ax = plt.subplots(figsize=(30, 15))
        ax.imshow(wc, interpolation="bilinear")
        ax.axis("off")
        placeholder = st.empty()
        placeholder.pyplot(fig)
