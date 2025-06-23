import streamlit as st

dashboard_page = st.Page("dashboard.py", title="Dashboard", icon=":material/dashboard:", default=True)
explorer_page = st.Page("explorer.py", title="Explorador", icon=":material/search:")

pg = st.navigation([dashboard_page, explorer_page])
pg.run()