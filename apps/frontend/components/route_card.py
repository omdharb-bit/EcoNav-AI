from __future__ import annotations

import streamlit as st

from apps.frontend.utils.formatters import parse_improvement_percent, route_to_string


def render_route_card(result: dict) -> None:
    improvement_pct = parse_improvement_percent(result.get("improvement", "N/A"))

    st.subheader("🌿 Recommended Eco Route")
    st.success(route_to_string(result["route"]))

    baseline_exposure = float(result.get("shortest_exposure", 0.0))
    eco_exposure = float(result.get("total_pollution", 0.0))
    exposure_delta = baseline_exposure - eco_exposure

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Distance", f"{float(result['total_distance']):.1f} km")
    col2.metric("Eco Exposure", f"{eco_exposure:.1f}")
    col3.metric("Baseline Exposure", f"{baseline_exposure:.1f}")
    col4.metric("Saved", f"{exposure_delta:.1f}")

    if improvement_pct is not None:
        progress_value = max(min(improvement_pct / 100, 1.0), 0.0)
        st.progress(progress_value, text=f"{improvement_pct:.2f}% cleaner")
    else:
        st.info("Improvement data not available for this route.")

    with st.expander("🔍 Compare with shortest route"):
        st.write("**Eco route:**", route_to_string(result["route"]))
        st.write("**Shortest path:**", route_to_string(result["shortest_route"]))
        st.write("**Improvement:**", result["improvement"])
