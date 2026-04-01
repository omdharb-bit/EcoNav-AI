import streamlit as st


def render_route_card(result: dict):
    st.subheader("🌿 Recommended Eco Route")
    st.success(" → ".join(result["route"]))

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Distance", f"{result['total_distance']:.1f} km")
    col2.metric("Total Pollution", f"{result['total_pollution']:.1f}")
    col3.metric("Improvement", result["improvement"])

    with st.expander("Compare with shortest route"):
        st.write("**Shortest path:**", " → ".join(result["shortest_route"]))
        st.write("**Shortest exposure:**", f"{result['shortest_exposure']:.1f}")
