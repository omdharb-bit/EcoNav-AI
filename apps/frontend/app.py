import streamlit as st
from requests import RequestException

from apps.frontend.components.map_view import render_map_view
from apps.frontend.components.route_card import render_route_card
from apps.frontend.services.api_client import fetch_eco_route


st.set_page_config(page_title="EcoNav AI", page_icon="🌱", layout="centered")
st.title("🌱 EcoNav AI")
st.caption("Smarter routes with lower pollution exposure")

with st.form("eco_route_form"):
    start = st.text_input("Start node", value="A")
    end = st.text_input("Destination node", value="F")
    submitted = st.form_submit_button("Find eco route")

if submitted:
    if not start or not end:
        st.warning("Please provide both start and destination nodes.")
    else:
        try:
            data = fetch_eco_route(start, end)
            render_route_card(data)
            render_map_view(data["route"])
        except RequestException as exc:
            st.error(f"Failed to reach backend API: {exc}")
        except Exception as exc:
            st.error(f"Unexpected error: {exc}")
