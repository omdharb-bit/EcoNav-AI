"""Exposure Credit display components for Streamlit."""

from __future__ import annotations

import streamlit as st


def _grade_color(grade: str) -> str:
    colors = {
        "A": "#4CAF50", "B": "#FFC107", "C": "#FF9800",
        "D": "#F44336", "E": "#9C27B0", "F": "#7E0023",
    }
    return colors.get(grade, "#888")


def render_credit_summary(data: dict, label: str = "Eco Route") -> None:
    """Render the exposure credit summary for a route."""
    credits = data.get("exposure_credits")
    if not credits:
        return

    grade = credits.get("overall_grade", "?")
    emoji = credits.get("overall_emoji", "")
    final_change = credits.get("final_credit_change", 0)
    eco_bonus = credits.get("eco_bonus", 0)
    summary = credits.get("grade_summary", "")
    color = _grade_color(grade)

    st.markdown(f"### 💳 Exposure Credits — {label}")

    # Main credit card
    delta_sign = "+" if final_change >= 0 else ""
    delta_color = "#4CAF50" if final_change >= 0 else "#F44336"

    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #1a1a2e, #16213e);
            border-radius: 16px;
            padding: 20px;
            color: white;
            border: 2px solid {color};
            margin-bottom: 16px;
        ">
            <div style="display:flex; justify-content:space-between; align-items:center">
                <div>
                    <div style="font-size:14px; color:#aaa">Route Grade</div>
                    <div style="font-size:48px; font-weight:800; color:{color}">{emoji} {grade}</div>
                </div>
                <div style="text-align:right">
                    <div style="font-size:14px; color:#aaa">Credits</div>
                    <div style="font-size:42px; font-weight:800; color:{delta_color}">{delta_sign}{final_change}</div>
                </div>
            </div>
            <div style="margin-top:10px; font-size:13px; color:#ccc">{summary}</div>
            {"<div style='margin-top:6px; font-size:12px; color:#4dd0e1'>🌱 Eco Bonus: +" + str(eco_bonus) + " credits for choosing green!</div>" if eco_bonus > 0 else ""}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_credit_comparison(data: dict) -> None:
    """Compare credits between eco and shortest route."""
    eco = data.get("exposure_credits")
    shortest = data.get("shortest_credits")
    if not eco or not shortest:
        return

    eco_change = eco.get("final_credit_change", 0)
    short_change = shortest.get("final_credit_change", 0)
    advantage = eco_change - short_change

    col1, col2, col3 = st.columns(3)

    with col1:
        color = "#4CAF50" if eco_change >= 0 else "#F44336"
        sign = "+" if eco_change >= 0 else ""
        st.markdown(
            f"""
            <div style="background:{color}15; border:1px solid {color}; border-radius:12px; padding:14px; text-align:center">
                <div style="font-size:12px; color:#aaa">🌿 Eco Route</div>
                <div style="font-size:28px; font-weight:700; color:{color}">{sign}{eco_change}</div>
                <div style="font-size:11px">Grade {eco.get('overall_grade', '?')}</div>
            </div>
            """, unsafe_allow_html=True,
        )

    with col2:
        color = "#4CAF50" if short_change >= 0 else "#F44336"
        sign = "+" if short_change >= 0 else ""
        st.markdown(
            f"""
            <div style="background:{color}15; border:1px solid {color}; border-radius:12px; padding:14px; text-align:center">
                <div style="font-size:12px; color:#aaa">🛣️ Shortest Route</div>
                <div style="font-size:28px; font-weight:700; color:{color}">{sign}{short_change}</div>
                <div style="font-size:11px">Grade {shortest.get('overall_grade', '?')}</div>
            </div>
            """, unsafe_allow_html=True,
        )

    with col3:
        adv_color = "#4CAF50" if advantage >= 0 else "#F44336"
        adv_sign = "+" if advantage >= 0 else ""
        st.markdown(
            f"""
            <div style="background:{adv_color}15; border:1px solid {adv_color}; border-radius:12px; padding:14px; text-align:center">
                <div style="font-size:12px; color:#aaa">💎 Eco Advantage</div>
                <div style="font-size:28px; font-weight:700; color:{adv_color}">{adv_sign}{advantage}</div>
                <div style="font-size:11px">credits saved</div>
            </div>
            """, unsafe_allow_html=True,
        )


def render_segment_breakdown(data: dict) -> None:
    """Show per-segment credit details."""
    credits = data.get("exposure_credits")
    if not credits:
        return

    segments = credits.get("segments", [])
    city_grades = credits.get("city_grades", [])

    if city_grades:
        with st.expander("🏙️ City Grades Along Route", expanded=False):
            cols = st.columns(min(len(city_grades), 6))
            for i, cg in enumerate(city_grades):
                color = _grade_color(cg["grade"])
                with cols[i % len(cols)]:
                    sign = "+" if cg["credit_delta"] >= 0 else ""
                    st.markdown(
                        f"**{cg['emoji']} {cg['city_name']}**  \n"
                        f"AQI: {cg['aqi']}  \n"
                        f"Grade: **{cg['grade']}** ({cg['grade_label']})  \n"
                        f"Credits: {sign}{cg['credit_delta']}"
                    )

    if segments:
        with st.expander("📊 Segment-by-Segment Credits", expanded=False):
            table = []
            for s in segments:
                sign = "+" if s["credit_delta"] >= 0 else ""
                table.append({
                    "Segment": f"{s['from']} → {s['to']}",
                    "From AQI": s["from_aqi"],
                    "To AQI": s["to_aqi"],
                    "Avg AQI": s["avg_aqi"],
                    "Grade": f"{s['emoji']} {s['grade']}",
                    "Credits": f"{sign}{s['credit_delta']}",
                })
            st.dataframe(table, use_container_width=True, hide_index=True)


def render_grade_legend() -> None:
    """Show the AQI → Grade → Credit reference table."""
    with st.expander("📖 Exposure Credit Grade Table", expanded=False):
        st.markdown(
            """
            | Grade | AQI Range | Label | Credits/Segment |
            |:-----:|:---------:|:------|:---------------:|
            | 🟢 A | 0 – 50 | Pristine Air | **+10** |
            | 🟡 B | 51 – 100 | Acceptable | **+5** |
            | 🟠 C | 101 – 150 | Moderate Risk | **±0** |
            | 🔴 D | 151 – 200 | High Risk | **−5** |
            | 🟣 E | 201 – 300 | Dangerous | **−15** |
            | ⚫ F | 300+ | Hazardous | **−25** |

            **Eco Bonus:** +5 extra credits when you choose the eco route over shortest path!
            """
        )
