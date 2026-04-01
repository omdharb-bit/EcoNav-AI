import streamlit as st


def render_map_view(path: list[str]):
    st.subheader("🗺️ Route Steps")
    for index, node in enumerate(path, start=1):
        st.write(f"{index}. {node}")
