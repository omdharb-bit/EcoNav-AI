from __future__ import annotations

import streamlit as st
from requests import RequestException

from apps.frontend.components.map_view import render_map_view
from apps.frontend.components.route_card import render_route_card
from apps.frontend.services.api_client import DEFAULT_BASE_URL, fetch_eco_route
from apps.frontend.utils.formatters import route_to_string

st.set_page_config(page_title="EcoNav AI", page_icon="🌱", layout="wide")

st.markdown(
    """
    <style>
      .block-container {padding-top: 1.5rem;}
      .hero-card {
        padding: 1rem 1.2rem;
        border-radius: 1rem;
        background: linear-gradient(90deg, #d9f99d 0%, #bbf7d0 45%, #a7f3d0 100%);
      }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero-card">
      <h2>🌱 EcoNav AI</h2>
      <p>Plan cleaner city routes with exposure-aware optimization.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Settings")
    api_url = st.text_input("Backend API URL", value=DEFAULT_BASE_URL)
    preset = st.selectbox("Quick route preset", ["A → F", "A → E", "C → F"], index=0)

start_default, end_default = [x.strip() for x in preset.split("→")]

with st.form("eco_route_form"):
    col1, col2 = st.columns(2)
    start = col1.text_input("Start node", value=start_default)
    end = col2.text_input("Destination node", value=end_default)
    submitted = st.form_submit_button("Find Eco Route", use_container_width=True)

if "history" not in st.session_state:
    st.session_state.history = []

if submitted:
    if not start or not end:
        st.warning("Please provide both start and destination nodes.")
    else:
        try:
            data = fetch_eco_route(start, end, api_url)
            st.session_state.history.insert(
                0,
                {
                    "from": start.upper(),
                    "to": end.upper(),
                    "route": route_to_string(data["route"]),
                    "improvement": data["improvement"],
                },
            )
            st.session_state.history = st.session_state.history[:5]

            left, right = st.columns([1.2, 1])
            with left:
                render_route_card(data)
            with right:
                render_map_view(data["route"])
        except RequestException as exc:
            st.error(f"Failed to reach backend API: {exc}")
        except Exception as exc:  # noqa: BLE001
            st.error(f"Unexpected error: {exc}")

if st.session_state.history:
    st.markdown("### Recent Searches")
    st.dataframe(st.session_state.history, use_container_width=True, hide_index=True)
