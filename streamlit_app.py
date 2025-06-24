import streamlit as st

explorer_page = st.Page(
    "explorer.py", title="Explorador", icon=":material/search:", default=True
)
dashboard_page = st.Page("dashboard.py", title="Análisis", icon=":material/dashboard:")


pg = st.navigation([explorer_page, dashboard_page])
pg.run()
