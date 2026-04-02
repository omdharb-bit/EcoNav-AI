"""AQI Dashboard component — supports 50+ cities with filtering."""

from __future__ import annotations

import streamlit as st


def _aqi_color(aqi: int) -> str:
    if aqi <= 50:
        return "#4CAF50"
    if aqi <= 100:
        return "#FFC107"
    if aqi <= 150:
        return "#FF9800"
    if aqi <= 200:
        return "#F44336"
    if aqi <= 300:
        return "#9C27B0"
    return "#7E0023"


def _aqi_emoji(aqi: int) -> str:
    if aqi <= 50:
        return "🟢"
    if aqi <= 100:
        return "🟡"
    if aqi <= 150:
        return "🟠"
    if aqi <= 200:
        return "🔴"
    if aqi <= 300:
        return "🟣"
    return "⚫"


def render_aqi_dashboard(aqi_data: dict) -> None:
    """Render full AQI dashboard with all cities."""
    cities = aqi_data.get("cities", [])
    total = aqi_data.get("total_configured", len(cities))

    if not cities:
        st.warning("No AQI data available.")
        return

    st.markdown(f"### 🌍 Real-Time Air Quality — {len(cities)} of {total} Cities")
    st.caption("Live data from Open-Meteo API • Updated every 10 minutes")

    # Summary row
    avg_aqi = sum(c["aqi"] for c in cities) / len(cities)
    sorted_cities = sorted(cities, key=lambda c: c["aqi"])
    best = sorted_cities[0]
    worst = sorted_cities[-1]

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("🏙️ Cities", f"{len(cities)}")
    m2.metric("📊 Avg AQI", f"{avg_aqi:.0f}")
    m3.metric(f"✅ Best: {best['city_name']}", f"{best['aqi']}")
    m4.metric(f"⚠️ Worst: {worst['city_name']}", f"{worst['aqi']}")

    st.divider()

    # AQI distribution
    good = sum(1 for c in cities if c["aqi"] <= 50)
    moderate = sum(1 for c in cities if 50 < c["aqi"] <= 100)
    usg = sum(1 for c in cities if 100 < c["aqi"] <= 150)
    unhealthy = sum(1 for c in cities if 150 < c["aqi"] <= 200)
    very_unhealthy = sum(1 for c in cities if 200 < c["aqi"] <= 300)
    hazardous = sum(1 for c in cities if c["aqi"] > 300)

    st.markdown("#### AQI Distribution")
    d1, d2, d3, d4, d5, d6 = st.columns(6)
    d1.markdown(f"🟢 Good\n\n**{good}**")
    d2.markdown(f"🟡 Moderate\n\n**{moderate}**")
    d3.markdown(f"🟠 USG\n\n**{usg}**")
    d4.markdown(f"🔴 Unhealthy\n\n**{unhealthy}**")
    d5.markdown(f"🟣 Very Bad\n\n**{very_unhealthy}**")
    d6.markdown(f"⚫ Hazardous\n\n**{hazardous}**")

    st.divider()

    # Sort options
    sort_by = st.selectbox("Sort by", ["AQI (High → Low)", "AQI (Low → High)", "City Name"], index=0)
    if sort_by == "AQI (High → Low)":
        cities = sorted(cities, key=lambda c: c["aqi"], reverse=True)
    elif sort_by == "AQI (Low → High)":
        cities = sorted(cities, key=lambda c: c["aqi"])
    else:
        cities = sorted(cities, key=lambda c: c["city_name"])

    # City cards — 4 per row
    for row_start in range(0, len(cities), 4):
        row_cities = cities[row_start:row_start + 4]
        cols = st.columns(4)
        for i, city in enumerate(row_cities):
            aqi = city["aqi"]
            color = _aqi_color(aqi)
            emoji = _aqi_emoji(aqi)
            with cols[i]:
                st.markdown(
                    f"""
                    <div style="
                        background: linear-gradient(135deg, {color}22, {color}08);
                        border-left: 4px solid {color};
                        border-radius: 10px;
                        padding: 12px;
                        margin-bottom: 8px;
                        min-height: 130px;
                    ">
                        <div style="font-size:14px; font-weight:600">{emoji} {city['city_name']}</div>
                        <div style="font-size:28px; font-weight:700; color:{color}; margin:4px 0">{aqi}</div>
                        <div style="font-size:11px; color:#999">{city['category']}</div>
                        <div style="font-size:11px">🎯 {city['dominant_pollutant']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    st.divider()

    # Pollutant table
    st.markdown("### 📊 Detailed Pollutant Data")
    table_data = []
    for city in cities:
        p = city.get("pollutants", {})
        table_data.append({
            "City": city["city_name"],
            "Code": city["city_code"],
            "AQI": city["aqi"],
            "Category": city["category"],
            "PM2.5 (µg/m³)": p.get("pm25") or "—",
            "PM10 (µg/m³)": p.get("pm10") or "—",
            "NO₂": p.get("no2") or "—",
            "SO₂": p.get("so2") or "—",
            "CO": p.get("co") or "—",
            "O₃": p.get("o3") or "—",
        })
    st.dataframe(table_data, use_container_width=True, hide_index=True)


def render_route_aqi_info(aqi_data: dict) -> None:
    """Render inline AQI cards for route result cities."""
    if not aqi_data:
        return

    st.markdown("#### 🏭 Real-Time AQI Along Route")
    cols = st.columns(min(len(aqi_data), 6))
    for i, (code, info) in enumerate(aqi_data.items()):
        col = cols[i % len(cols)]
        aqi = info.get("aqi", 0)
        emoji = _aqi_emoji(aqi)
        with col:
            st.markdown(
                f"**{emoji} {info['city']}**  \nAQI: **{aqi}**  \n{info['category']}  \n"
                f"Weight: {info['pollution_weight']}",
            )
