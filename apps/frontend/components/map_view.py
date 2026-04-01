from __future__ import annotations

import streamlit as st


def render_map_view(path: list[str]) -> None:
    st.subheader("🗺️ Route Timeline")

    cols = st.columns(len(path)) if path else []
    for index, node in enumerate(path):
        cols[index].markdown(f"**{index + 1}. {node}**")
        if index < len(path) - 1:
            cols[index].caption("⬇")

    st.markdown("### Step-by-step")
    for index, node in enumerate(path, start=1):
        st.write(f"{index}. Arrive at node `{node}`")
