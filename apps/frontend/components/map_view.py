import streamlit as st
from components.route_card import get_city_data
from services.api_client import fetch_graph


def render_map_view(result: dict) -> None:
    """
    Renders a Graphviz route visualization showing both the eco route
    and shortest route on the same graph. Additionally renders a Leaflet
    map embed for real-world visualization.
    """
    # Load live city data
    CITY_NODES, NODE_COORDS = get_city_data()

    eco_path = result.get("route", [])
    shortest_path = result.get("shortest_route", [])

    if not eco_path:
        st.info("No route to display.")
        return

    # ---- Graphviz Network Graph ----
    st.markdown('<div class="section-header">🗺️ Route Network</div>', unsafe_allow_html=True)

    eco_edges = set()
    for i in range(len(eco_path) - 1):
        eco_edges.add((eco_path[i], eco_path[i + 1]))

    short_edges = set()
    for i in range(len(shortest_path) - 1):
        short_edges.add((shortest_path[i], shortest_path[i + 1]))

    # Load all graph edges dynamically from backend
    graph_data = fetch_graph()
    all_graph_edges = []
    if graph_data and "roads" in graph_data:
        for r in graph_data["roads"]:
            all_graph_edges.append((r["from"], r["to"], r["distance"], r["pollution"]))
    else:
        # Fallback
        all_graph_edges = [
            ("A", "B", 5, 10), ("A", "C", 8, 3),
            ("B", "D", 2, 2), ("C", "D", 4, 6),
            ("C", "E", 7, 1), ("D", "E", 1, 2),
            ("D", "F", 6, 8), ("E", "F", 3, 1),
        ]

    lines = []
    lines.append("digraph EcoNav {")
    lines.append("  rankdir=LR;")
    lines.append('  bgcolor="transparent";')
    lines.append("  pad=0.5; nodesep=0.8; ranksep=1.2;")
    lines.append('  node [shape=box, style="rounded,filled", fontname="Inter", fontsize=11, '
                 'fillcolor="#1e293b", fontcolor="#e2e8f0", color="#334155", penwidth=1.5];')
    lines.append('  edge [fontname="Inter", fontsize=9];')

    # Node labels with city names
    for node, city in CITY_NODES.items():
        if node == eco_path[0]:
            lines.append(f'  "{node}" [label="{city}", fillcolor="#064e3b", color="#10b981", fontcolor="#34d399"];')
        elif node == eco_path[-1]:
            lines.append(f'  "{node}" [label="{city}", fillcolor="#1e1b4b", color="#6366f1", fontcolor="#a5b4fc"];')
        else:
            lines.append(f'  "{node}" [label="{city}"];')

    # Draw edges
    for u, v, dist, pol in all_graph_edges:
        edge_label = f"{dist}km, AQI:{pol}"
        if (u, v) in eco_edges:
            lines.append(f'  "{u}" -> "{v}" [color="#10b981", penwidth=3.0, '
                         f'arrowsize=1.2, label=" {edge_label}", fontcolor="#34d399"];')
        elif (u, v) in short_edges:
            lines.append(f'  "{u}" -> "{v}" [color="#ef4444", penwidth=2.0, '
                         f'style=dashed, label=" {edge_label}", fontcolor="#f87171"];')
        else:
            lines.append(f'  "{u}" -> "{v}" [color="#334155", penwidth=1.0, '
                         f'arrowsize=0.7, label=" {edge_label}", fontcolor="#475569"];')

    # Legend
    lines.append('  subgraph cluster_legend {')
    lines.append('    label="Legend"; fontname="Inter"; fontsize=10; fontcolor="#94a3b8";')
    lines.append('    style="rounded"; color="#1e293b";')
    lines.append('    L1 [label="🟢 Eco Route", shape=plaintext, fontcolor="#34d399"];')
    lines.append('    L2 [label="🔴 Shortest Route", shape=plaintext, fontcolor="#f87171"];')
    lines.append('  }')

    lines.append("}")
    dot_source = "\n".join(lines)

    st.graphviz_chart(dot_source, use_container_width=True)

    # ---- Leaflet Map Embed ----
    st.markdown('<div class="section-header">🌍 Real-World Map</div>', unsafe_allow_html=True)

    # Build waypoint arrays for JS
    eco_waypoints_js = ", ".join(
        f"[{NODE_COORDS[n][0]}, {NODE_COORDS[n][1]}]" for n in eco_path if n in NODE_COORDS
    )
    short_waypoints_js = ", ".join(
        f"[{NODE_COORDS[n][0]}, {NODE_COORDS[n][1]}]" for n in shortest_path if n in NODE_COORDS
    )

    # Build markers JS
    markers_js = ""
    for n in set(eco_path + shortest_path):
        if n in NODE_COORDS:
            city = CITY_NODES.get(n, n)
            is_start = (n == eco_path[0])
            is_end = (n == eco_path[-1])
            if is_start:
                icon_html = "🟢"
                label = f"{city} (Start)"
            elif is_end:
                icon_html = "🏁"
                label = f"{city} (End)"
            else:
                icon_html = "📍"
                label = f"{city} ({n})"
            markers_js += (
                f'L.marker([{NODE_COORDS[n][0]}, {NODE_COORDS[n][1]}], {{'
                f'icon: L.divIcon({{html: "<div style=\\"font-size:20px;\\">{icon_html}</div>", '
                f'className: "", iconSize: [28,28], iconAnchor: [14,14]}})'
                f'}}).addTo(map).bindPopup("{label}");\n'
            )

    map_html = f"""
    <div style="border-radius: 12px; overflow: hidden; border: 1px solid rgba(255,255,255,0.08); position: relative;">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <div id="map" style="height: 450px; width: 100%; background: #0a0f1a;"></div>
    <div id="map-badge" style="position:absolute;top:10px;right:10px;background:rgba(10,15,26,0.9);
         color:#94a3b8;padding:6px 14px;border-radius:8px;font-size:11px;font-family:Inter,sans-serif;
         border:1px solid rgba(255,255,255,0.08);z-index:1000;"></div>
    <script>
        var map = L.map('map').setView([26, 80], 5);
        L.tileLayer('https://{{{{s}}}}.tile.openstreetmap.org/{{{{z}}}}/{{{{x}}}}/{{{{y}}}}.png', {{{{
            attribution: '&copy; OpenStreetMap'
        }}}}).addTo(map);

        var ecoWP = [{eco_waypoints_js}];
        var shortWP = [{short_waypoints_js}];
        var badge = document.getElementById('map-badge');

        // ── STEP 1: Draw straight lines INSTANTLY ──
        var shortLine = null, ecoLine = null;
        if (shortWP.length >= 2) {{{{
            shortLine = L.polyline(shortWP, {{{{color:'#ef4444',weight:3,opacity:0.5,dashArray:'10,6'}}}}).addTo(map);
        }}}}
        if (ecoWP.length >= 2) {{{{
            ecoLine = L.polyline(ecoWP, {{{{color:'#10b981',weight:5,opacity:0.7}}}}).addTo(map);
            map.fitBounds(L.latLngBounds(ecoWP), {{{{padding:[40,40]}}}});
        }}}}

        // Markers
        {markers_js}

        // Legend
        var legend = L.control({{{{position:'bottomleft'}}}});
        legend.onAdd = function() {{{{
            var d = L.DomUtil.create('div');
            d.style.cssText = 'background:rgba(10,15,26,0.9);padding:10px 14px;border-radius:10px;color:#e2e8f0;font-family:Inter,sans-serif;font-size:12px;border:1px solid rgba(255,255,255,0.08);';
            d.innerHTML = '<div style="margin-bottom:4px;"><span style="color:#10b981;">━━━</span> Eco Route</div><div><span style="color:#ef4444;">┅┅┅</span> Shortest Route</div>';
            return d;
        }}}};
        legend.addTo(map);

        // ── STEP 2: Upgrade to road routes in background ──
        badge.textContent = '🛣️ Loading road routes...';

        function decodeP6(enc) {{{{
            var c=[],i=0,lt=0,ln=0;
            while(i<enc.length){{{{var b,s=0,r=0;do{{{{b=enc.charCodeAt(i++)-63;r|=(b&0x1f)<<s;s+=5;}}}}while(b>=0x20);lt+=(r&1)?~(r>>1):(r>>1);s=0;r=0;do{{{{b=enc.charCodeAt(i++)-63;r|=(b&0x1f)<<s;s+=5;}}}}while(b>=0x20);ln+=(r&1)?~(r>>1):(r>>1);c.push([lt/1e6,ln/1e6]);}}}}
            return c;
        }}}}

        function fetchRoad(wp, timeout) {{{{
            if(wp.length<2) return Promise.resolve(null);
            var cs = wp.map(function(c){{{{return c[1]+','+c[0];}}}}).join(';');
            var ctrl = new AbortController();
            var tid = setTimeout(function(){{{{ctrl.abort();}}}}, timeout);
            return fetch('https://router.project-osrm.org/route/v1/driving/'+cs+'?overview=full&geometries=polyline6',
                {{{{signal:ctrl.signal}}}})
                .then(function(r){{{{return r.json();}}}})
                .then(function(d){{{{clearTimeout(tid);if(d.code==='Ok'&&d.routes&&d.routes.length>0)return decodeP6(d.routes[0].geometry);return null;}}}})
                .catch(function(){{{{clearTimeout(tid);return null;}}}});
        }}}}

        // Fire both requests at once, 4s timeout each
        Promise.all([fetchRoad(shortWP,4000), fetchRoad(ecoWP,4000)]).then(function(res){{{{
            if(res[0] && shortLine) {{{{ map.removeLayer(shortLine); L.polyline(res[0],{{{{color:'#ef4444',weight:4,opacity:0.6,dashArray:'10,6'}}}}).addTo(map).bindPopup('🔴 Shortest Route'); }}}}
            if(res[1] && ecoLine) {{{{ map.removeLayer(ecoLine); L.polyline(res[1],{{{{color:'#10b981',weight:6,opacity:0.9}}}}).addTo(map).bindPopup('🟢 Eco Route'); }}}}
            badge.textContent = '✅ Road routes loaded';
            setTimeout(function(){{{{badge.style.display='none';}}}},2000);
        }}}}).catch(function(){{{{
            badge.textContent = '📍 Showing straight-line routes';
            setTimeout(function(){{{{badge.style.display='none';}}}},3000);
        }}}});
    </script>
    </div>
    """
    st.components.v1.html(map_html, height=480)


