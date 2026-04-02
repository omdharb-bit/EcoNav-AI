// --- DOM Elements ---
const btnHome = document.getElementById('btn-home');
const btnRoute = document.getElementById('btn-route');
const btnTraffic = document.getElementById('btn-traffic');
const btnNetwork = document.getElementById('btn-network');
const btnAqi = document.getElementById('btn-aqi');
const btnTasks = document.getElementById('btn-tasks');
const viewHome = document.getElementById('view-home');
const viewRoute = document.getElementById('view-route');
const viewTraffic = document.getElementById('view-traffic');
const viewNetwork = document.getElementById('view-network');
const viewAqi = document.getElementById('view-aqi');
const viewTasks = document.getElementById('view-tasks');

// --- Map Initialization ---
let map = L.map('map').setView([26.0, 80.0], 5);
L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; OpenStreetMap contributors &copy; CARTO',
    subdomains: 'abcd',
    maxZoom: 19
}).addTo(map);

let currentRouteLayer = null;

// Traffic Engine Map
let mapTraffic = L.map('map-traffic').setView([26.0, 80.0], 5);
L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; OpenStreetMap contributors &copy; CARTO',
    subdomains: 'abcd',
    maxZoom: 19
}).addTo(mapTraffic);

let currentTrafficRouteLayer = null;

const CITY_COORDS = {
    "A": [28.6139, 77.2090], // Delhi
    "B": [26.9124, 75.7873], // Jaipur
    "C": [27.1767, 78.0081], // Agra
    "D": [25.3176, 82.9739], // Varanasi
    "E": [26.8467, 80.9462], // Lucknow
    "F": [22.5726, 88.3639], // Kolkata
};

const CITY_NAMES = {
    "A": "Delhi",
    "B": "Jaipur",
    "C": "Agra",
    "D": "Varanasi",
    "E": "Lucknow",
    "F": "Kolkata"
};

// --- Global State ---
let globalCredits = parseInt(localStorage.getItem('econav_credits')) || 1000;

function updateGlobalCreditsUI() {
    const badge = document.getElementById('global-credit-badge');
    const valObj = document.getElementById('global-credits-val');
    valObj.textContent = globalCredits;
    
    // Scale indicating depletion of today's health credits
    if (globalCredits >= 800) {
        // Green
        badge.style.background = 'rgba(16, 185, 129, 0.1)';
        badge.style.color = '#10b981';
    } else if (globalCredits >= 500) {
        // Light Red / Orange
        badge.style.background = 'rgba(249, 115, 22, 0.1)';
        badge.style.color = '#f97316';
    } else if (globalCredits >= 200) {
        // Red
        badge.style.background = 'rgba(239, 68, 68, 0.1)'; 
        badge.style.color = '#ef4444';
    } else {
        // Dark Red
        badge.style.background = 'rgba(153, 27, 27, 0.2)'; 
        badge.style.color = '#dc2626'; // slightly brighter text for contrast against dark background
    }
}
updateGlobalCreditsUI();

document.getElementById('btn-reset-day').addEventListener('click', () => {
    globalCredits = 1000;
    localStorage.setItem('econav_credits', globalCredits);
    updateGlobalCreditsUI();
});

// --- Tab Switching ---
function hideAll() {
    [viewHome, viewRoute, viewTraffic, viewNetwork, viewAqi, viewTasks].forEach(v => {
        v.classList.add('hidden');
        v.classList.remove('animate-in');
    });
    [btnHome, btnRoute, btnTraffic, btnNetwork, btnAqi, btnTasks].forEach(b => b.classList.remove('active'));
}

btnHome.addEventListener('click', () => {
    hideAll();
    viewHome.classList.remove('hidden');
    viewHome.classList.add('animate-in');
    btnHome.classList.add('active');
});

btnRoute.addEventListener('click', () => {
    hideAll();
    viewRoute.classList.remove('hidden');
    viewRoute.classList.add('animate-in');
    btnRoute.classList.add('active');
    setTimeout(() => map.invalidateSize(), 100);
});

btnTraffic.addEventListener('click', () => {
    hideAll();
    viewTraffic.classList.remove('hidden');
    viewTraffic.classList.add('animate-in');
    btnTraffic.classList.add('active');
    setTimeout(() => mapTraffic.invalidateSize(), 100);
});

btnNetwork.addEventListener('click', () => {
    hideAll();
    viewNetwork.classList.remove('hidden');
    viewNetwork.classList.add('animate-in');
    btnNetwork.classList.add('active');
    loadNetworkGraph();
});

btnAqi.addEventListener('click', () => {
    hideAll();
    viewAqi.classList.remove('hidden');
    viewAqi.classList.add('animate-in');
    btnAqi.classList.add('active');
    if (!window.aqiLoaded) loadAqiData();
});

btnTasks.addEventListener('click', () => {
    hideAll();
    viewTasks.classList.remove('hidden');
    viewTasks.classList.add('animate-in');
    btnTasks.classList.add('active');
    if (!window.tasksLoaded) loadTasksData();
});

// --- Normal Route Optimization Logic ---
const btnSubmit = document.getElementById('submit-route');
const routeLoading = document.getElementById('route-loading');
const routeResults = document.getElementById('route-results');
const routeError = document.getElementById('route-error');

async function geocodeCity(name) {
    const res = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(name)}&limit=1`);
    const data = await res.json();
    if (data.length === 0) throw new Error(`City not found: ${name}`);
    return [parseFloat(data[0].lat), parseFloat(data[0].lon)];
}

function calculateDistance(lat1, lon1, lat2, lon2) {
    const R = 6371; // km
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
              Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * 
              Math.sin(dLon/2) * Math.sin(dLon/2);
    return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a)); 
}

btnSubmit.addEventListener('click', async () => {
    const startStr = document.getElementById('start-node').value.trim();
    const endStr = document.getElementById('end-node').value.trim();
    const multiplier = 1.0; 
    
    // UI Reset
    routeResults.classList.add('hidden');
    routeError.classList.add('hidden');
    routeLoading.classList.remove('hidden');

    try {
        let startKey = Object.keys(CITY_NAMES).find(k => CITY_NAMES[k].toLowerCase() === startStr.toLowerCase());
        let endKey = Object.keys(CITY_NAMES).find(k => CITY_NAMES[k].toLowerCase() === endStr.toLowerCase());

        let data = null;

        if (startKey && endKey) {
            // Both inside our 6-node RL environment
            const response = await fetch('/api/v1/eco-route', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ start: startKey, end: endKey, traffic_multiplier: multiplier })
            });
            
            if (!response.ok) throw new Error(`API Error: ${response.statusText}`);
            data = await response.json();
            
        } else {
            // One or more arbitrary cities! Do custom geocode routing
            const [startLat, startLng] = await geocodeCity(startStr);
            const [endLat, endLng] = await geocodeCity(endStr);
            
            const straightDist = calculateDistance(startLat, startLng, endLat, endLng);
            const mockDist = Math.floor(straightDist * 1.3); // Apply ~1.3x routing modifier to straight line
            
            // Seed a consistent mock pollution value based on the city names so it doesn't change on refresh
            const seed = ((startStr.charCodeAt(0) || 0) + (endStr.charCodeAt(0) || 0)) % 100;
            const pseudoAqi = 50 + seed; // 50-150 AQI range
            const mockPollution = mockDist * pseudoAqi * 0.04;
            
            data = {
                route: [startStr, endStr],
                custom_coords: [[startLat, startLng], [endLat, endLng]], // injected custom payload
                total_distance: mockDist,
                total_pollution: mockPollution,
                improvement: "12% (Simulated)",
                exposure_credits: {
                    final_credit_change: (Math.random() > 0.5 ? 20 : -10),
                    overall_grade: "B",
                    overall_emoji: "🟡",
                    segments: [
                        {from: startStr, to: endStr, avg_aqi: Math.floor(Math.random()*200), credit_delta: 0, emoji: "🚦"}
                    ]
                }
            };
        }

        renderRouteResults(data);
        
        // Deduct/Add credits to global state
        const creditsEarned = data.exposure_credits.final_credit_change || 0;
        globalCredits += creditsEarned;
        localStorage.setItem('econav_credits', globalCredits);
        updateGlobalCreditsUI();
        
    } catch (err) {
        routeError.textContent = err.message;
        routeError.classList.remove('hidden');
    } finally {
        routeLoading.classList.add('hidden');
    }
});

// --- Traffic Engine Simulator Logic ---
const simSlider = document.getElementById('traffic-level-sim');
const simTrafficVal = document.getElementById('traffic-val-sim');

simSlider.addEventListener('input', (e) => {
    simTrafficVal.textContent = parseFloat(e.target.value).toFixed(1) + 'x';
});

document.getElementById('submit-traffic').addEventListener('click', async () => {
    const start = document.getElementById('traffic-start').value;
    const end = document.getElementById('traffic-end').value;
    const multiplier = parseFloat(simSlider.value);
    
    const resultsPanel = document.getElementById('traffic-results');
    const errText = document.getElementById('traffic-error');
    errText.classList.add('hidden');
    resultsPanel.classList.add('hidden');
    
    try {
        let startKey = Object.keys(CITY_NAMES).find(k => CITY_NAMES[k].toLowerCase() === start.toLowerCase());
        let endKey = Object.keys(CITY_NAMES).find(k => CITY_NAMES[k].toLowerCase() === end.toLowerCase());

        let data = null;

        if (startKey && endKey) {
            const response = await fetch('/api/v1/eco-route', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ start: startKey, end: endKey, traffic_multiplier: multiplier })
            });
            if (!response.ok) throw new Error(`API Error: ${response.statusText}`);
            data = await response.json();
            
        } else {
            // Geographic custom routing
            const [startLat, startLng] = await geocodeCity(start);
            const [endLat, endLng] = await geocodeCity(end);
            
            const straightDist = calculateDistance(startLat, startLng, endLat, endLng);
            const mockDist = Math.floor(straightDist * 1.3);
            
            const seed = ((start.charCodeAt(0) || 0) + (end.charCodeAt(0) || 0)) % 100;
            const pseudoAqi = 50 + seed;
            const mockPollution = mockDist * pseudoAqi * 0.04 * multiplier;
            data = {
                route: [start, end],
                custom_coords: [[startLat, startLng], [endLat, endLng]],
                total_distance: mockDist,
                total_pollution: mockPollution,
                exposure_credits: { segments: [{from: start, to: end, avg_aqi: Math.floor(Math.random()*200), emoji: "🚦"}] }
            };
        }
        
        const routeArr = data.route || [];

        // Populate the traffic stats
        document.getElementById('traffic-res-dist').textContent = `Distance: ${Math.round(data.total_distance || 0)} km`;
        document.getElementById('traffic-res-exp').textContent = `Exposure: ${Math.round(data.total_pollution || 0)}`;
        document.getElementById('traffic-res-path').textContent = `Path: ${routeArr.map(n => CITY_NAMES[n] || n).join(' → ')}`;
        
        const segStr = data.exposure_credits?.segments?.map(s => `${CITY_NAMES[s.from] || s.from} to ${CITY_NAMES[s.to] || s.to} (AQI: ${s.avg_aqi})`).join(' | ');
        document.getElementById('traffic-res-segments').textContent = `Segments: ${segStr || 'N/A'}`;
        
        resultsPanel.classList.remove('hidden');
        resultsPanel.classList.add('animate-in');
        
        setTimeout(() => {
            mapTraffic.invalidateSize();
        }, 100);
        
        // Traffic Map Updates
        if (currentTrafficRouteLayer) mapTraffic.removeLayer(currentTrafficRouteLayer);
        if (window.trafficRouteControl) mapTraffic.removeControl(window.trafficRouteControl);
        
        const coords = data.custom_coords ? data.custom_coords : routeArr.map(n => CITY_COORDS[n]).filter(Boolean);
        if (coords.length > 0) {
            currentTrafficRouteLayer = L.featureGroup().addTo(mapTraffic);
            
            window.trafficRouteControl = L.Routing.control({
                waypoints: coords.map(c => L.latLng(c[0], c[1])),
                routeWhileDragging: false,
                addWaypoints: false,
                fitSelectedRoutes: true,
                showAlternatives: false,
                createMarker: function() { return null; },
                lineOptions: {
                    styles: [{ className: 'glowing-route glow-red', weight: 6, color: '#f43f5e' }]
                }
            }).addTo(mapTraffic);
            
            coords.forEach((coord, i) => {
                const isEndpoint = i === 0 || i === coords.length - 1;
                L.circleMarker(coord, {
                    radius: isEndpoint ? 8 : 5,
                    fillColor: isEndpoint ? "#0ea5e9" : "#f43f5e",
                    color: "#fff",
                    weight: 2,
                    opacity: 1,
                    fillOpacity: 1
                }).bindTooltip(routeArr[i], {permanent: true, direction: "top"}).addTo(currentTrafficRouteLayer);
            });
            setTimeout(() => mapTraffic.invalidateSize(), 50);
        }
    } catch (err) {
        errText.textContent = err.message;
        errText.classList.remove('hidden');
    }
});

function renderRouteResults(data) {
    const credits = data.exposure_credits || {};
    
    // Credits
    const cChange = credits.final_credit_change || 0;
    const sign = cChange > 0 ? '+' : '';
    const cColor = cChange >= 0 ? '#10b981' : '#f43f5e';
    
    const elCred = document.getElementById('res-credits');
    if (elCred) {
        elCred.textContent = `${sign}${cChange}`;
        elCred.style.color = cColor;
    }
    
    const elGrade = document.getElementById('res-grade');
    if (elGrade) {
        elGrade.textContent = `${credits.overall_emoji || ''} Grade ${credits.overall_grade || '?'}`;
    }
    
    // Advantage
    document.getElementById('res-advantage').textContent = data.improvement || '0%';
    
    // Summary line
    const routeArr = data.route || [];
    document.getElementById('res-path').textContent = routeArr.map(n => CITY_NAMES[n] || n).join(' → ');
    document.getElementById('res-dist').textContent = `Distance: ${Math.round(data.total_distance)} km`;
    document.getElementById('res-exp').textContent = `Exposure: ${Math.round(data.total_pollution)}`;

    // Map Updates
    if (currentRouteLayer) map.removeLayer(currentRouteLayer);
    if (window.routeControlMain) map.removeControl(window.routeControlMain);
    
    const coords = data.custom_coords ? data.custom_coords : routeArr.map(n => CITY_COORDS[n]).filter(Boolean);
    if (coords.length > 0) {
        currentRouteLayer = L.featureGroup().addTo(map);
        
        window.routeControlMain = L.Routing.control({
            waypoints: coords.map(c => L.latLng(c[0], c[1])),
            routeWhileDragging: false,
            addWaypoints: false,
            fitSelectedRoutes: true,
            showAlternatives: false,
            createMarker: function() { return null; },
            lineOptions: {
                styles: [{ className: 'glowing-route', weight: 6, color: '#10b981' }]
            }
        }).addTo(map);
        
        // Draw markers
        coords.forEach((coord, i) => {
            const isEndpoint = i === 0 || i === coords.length - 1;
            L.circleMarker(coord, {
                radius: isEndpoint ? 8 : 5,
                fillColor: isEndpoint ? "#0ea5e9" : "#10b981",
                color: "#fff",
                weight: 2,
                opacity: 1,
                fillOpacity: 1
            }).bindTooltip(routeArr[i], {permanent: true, direction: "top"}).addTo(currentRouteLayer);
        });
    }

    // Segments
    const segContainer = document.getElementById('segment-container');
    if (segContainer) {
        segContainer.innerHTML = '';
    
    if (credits.segments) {
        credits.segments.forEach(s => {
            const segSign = s.credit_delta > 0 ? '+' : '';
            const row = document.createElement('div');
            row.style.display = 'flex';
            row.style.justifyContent = 'space-between';
            row.style.padding = '0.75rem';
            row.style.background = 'rgba(0,0,0,0.2)';
            row.style.borderRadius = '8px';
            row.style.fontSize = '0.9rem';
            
            row.innerHTML = `
                <div style="font-weight:600; color: #e2e8f0;">${CITY_NAMES[s.from] || s.from} → ${CITY_NAMES[s.to] || s.to}</div>
                <div style="color: #94a3b8;">AQI: ${s.avg_aqi}</div>
                <div style="color: ${s.credit_delta >= 0 ? '#10b981' : '#f43f5e'}; font-weight:600;">
                    ${s.emoji} ${segSign}${s.credit_delta}
                </div>
            `;
            segContainer.appendChild(row);
        });
    }
    } // closes if (segContainer)

    routeResults.classList.remove('hidden');
    routeResults.classList.add('animate-in');
    
    // Fix Leaflet grey map loading issue
    setTimeout(() => {
        map.invalidateSize();
    }, 100);
}



// --- AQI Matrix Logic ---
window.aqiLoaded = false;

async function loadAqiData() {
    const container = document.getElementById('aqi-container');
    const loader = document.getElementById('aqi-loading');
    
    try {
        const res = await fetch('/api/v1/aqi?region=metro');
        if (!res.ok) throw new Error('Network response was not ok');
        const data = await res.json();
        
        container.innerHTML = '';
        const cities = data.cities || [];
        
        cities.sort((a,b) => b.aqi - a.aqi);

        cities.forEach(c => {
            let color = '#4CAF50';
            if (c.aqi > 50) color = '#FFC107';
            if (c.aqi > 100) color = '#FF9800';
            if (c.aqi > 150) color = '#F44336';
            if (c.aqi > 200) color = '#9C27B0';
            if (c.aqi > 300) color = '#7E0023';

            const card = document.createElement('div');
            card.className = 'glass city-card';
            card.style.setProperty('--card-color', color);
            
            card.innerHTML = `
                <div class="city-header">
                    <div>
                        <div class="city-name">${c.city_name}</div>
                        <div style="font-size: 11px; color: var(--text-secondary);">${c.category}</div>
                    </div>
                    <div class="city-aqi">${c.aqi}</div>
                </div>
                <div class="pollutants-list">
                    <div>PM2.5: <span style="color:#fff">${c.pollutants.pm25 || '--'}</span></div>
                    <div>PM10: <span style="color:#fff">${c.pollutants.pm10 || '--'}</span></div>
                    <div>CO: <span style="color:#fff">${c.pollutants.co || '--'}</span></div>
                    <div>O₃: <span style="color:#fff">${c.pollutants.o3 || '--'}</span></div>
                </div>
                <div style="margin-top:0.75rem; font-size:11px; text-transform:uppercase; color: ${color}; font-weight:600;">
                    🎯 Dominant: ${c.dominant_pollutant}
                </div>
            `;
            container.appendChild(card);
        });
        
        window.aqiLoaded = true;
    } catch (err) {
        console.error(err);
        container.innerHTML = `<p style="color: #ef4444;">Failed to load live AQI data.</p>`;
    } finally {
        loader.classList.add('hidden');
    }
}

// --- Tasks Viewer Logic ---
window.tasksLoaded = false;

let simChartInstance = null;

async function loadTasksData() {
    const taskSelect = document.getElementById('sim-task-select');
    try {
        const res = await fetch('/tasks');
        const data = await res.json();
        const tasks = data.tasks || [];
        
        taskSelect.innerHTML = tasks.map(t => 
            `<option value="${t.id}">${t.name} (${t.difficulty})</option>`
        ).join('');
        
        window.tasksLoaded = true;
    } catch (err) {
        console.error(err);
        taskSelect.innerHTML = `<option>Failed to load tasks</option>`;
    }
}

document.getElementById('btn-run-sim').addEventListener('click', async () => {
    const task_id = document.getElementById('sim-task-select').value;
    const loader = document.getElementById('sim-loading');
    const logBox = document.getElementById('sim-event-log');
    
    loader.classList.remove('hidden');
    logBox.innerHTML = '<span style="color: #10b981;">Starting simulation...</span>';
    
    try {
        const res = await fetch('/api/v1/simulate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ task_id: task_id })
        });
        
        if (!res.ok) throw new Error('Simulation failed');
        const data = await res.json();
        
        // Populate logs
        let logHtml = '';
        const labels = [];
        const creditsData = [];
        const aqiData = [];
        
        data.timeline.forEach(step => {
            logHtml += `<div style="padding: 0.3rem 0; border-bottom: 1px dashed rgba(255,255,255,0.05);"><span style="color:#a855f7;">[Step ${step.step}]</span> Arrived: <strong>${step.city}</strong> <span style="color:#0ea5e9;">(AQI: ${step.aqi})</span> | Credits: <span style="color:#10b981;">${step.credits}</span></div>`;
            labels.push(`Step ${step.step}`);
            creditsData.push(step.credits);
            aqiData.push(step.aqi);
        });
        
        logHtml += `<div style="color: var(--accent-primary); margin-top: 1rem; font-size: 1rem;">🏁 Final Grade: ${data.grade_report.grade} (Score: ${data.grade_report.score.toFixed(3)})</div>`;
        logBox.innerHTML = logHtml;
        
        // Draw Chart
        const ctx = document.getElementById('simChart').getContext('2d');
        if (simChartInstance) simChartInstance.destroy();
        
        Chart.defaults.color = '#a1a1aa';
        simChartInstance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Exposure Credits',
                        data: creditsData,
                        borderColor: '#10b981',
                        backgroundColor: 'rgba(16, 185, 129, 0.2)',
                        borderWidth: 2,
                        tension: 0.3,
                        yAxisID: 'y'
                    },
                    {
                        label: 'Local AQI',
                        data: aqiData,
                        borderColor: '#f59e0b',
                        backgroundColor: 'rgba(245, 158, 11, 0.2)',
                        borderWidth: 1,
                        borderDash: [5, 5],
                        tension: 0.1,
                        yAxisID: 'y1'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: false,
                        grid: { color: 'rgba(255, 255, 255, 0.05)' },
                        title: { display: true, text: 'Credits Remaining' }
                    },
                    y1: {
                        position: 'right',
                        grid: { drawOnChartArea: false },
                        title: { display: true, text: 'AQI' }
                    },
                    x: {
                        grid: { color: 'rgba(255, 255, 255, 0.05)' }
                    }
                },
                plugins: {
                    legend: { labels: { color: '#fff' } }
                }
            }
        });
        
    } catch (err) {
        logBox.innerHTML = `<span style="color:#ef4444;">Error: ${err.message}</span>`;
    } finally {
        loader.classList.add('hidden');
    }
});

// ============================================================
// ROUTE NETWORK — canvas-based interactive graph
// ============================================================

let networkData = null;         // { nodes, edges }
let networkAnimationId = null;  // rAF handle
let networkDashOffset = 0;      // animated dash offset

const NODE_RADIUS  = 28;
const CANVAS_PAD_X = 60;        // extra padding so labels don't clip
const CANVAS_PAD_Y = 40;

// Scale raw node positions to the actual canvas pixel size
function scaleNodes(nodes, canvas) {
    const rawW = 760, rawH = 400;       // design-time canvas size
    const scaleX = (canvas.width  - CANVAS_PAD_X * 2) / rawW;
    const scaleY = (canvas.height - CANVAS_PAD_Y * 2) / rawH;
    return nodes.map(n => ({
        ...n,
        px: Math.round(n.x * scaleX + CANVAS_PAD_X),
        py: Math.round(n.y * scaleY + CANVAS_PAD_Y),
    }));
}

function nodeById(scaled, id) {
    return scaled.find(n => n.id === id);
}

// Draw a filled, glow-ringed city node
function drawNode(ctx, n) {
    // Glow halo
    const grad = ctx.createRadialGradient(n.px, n.py, NODE_RADIUS * 0.6, n.px, n.py, NODE_RADIUS * 1.8);
    grad.addColorStop(0, n.color + '55');
    grad.addColorStop(1, 'transparent');
    ctx.beginPath();
    ctx.arc(n.px, n.py, NODE_RADIUS * 1.8, 0, Math.PI * 2);
    ctx.fillStyle = grad;
    ctx.fill();

    // Node ring
    ctx.beginPath();
    ctx.arc(n.px, n.py, NODE_RADIUS, 0, Math.PI * 2);
    ctx.fillStyle = '#0f172a';
    ctx.fill();
    ctx.strokeStyle = n.color;
    ctx.lineWidth = 2.5;
    ctx.shadowColor = n.color;
    ctx.shadowBlur = 12;
    ctx.stroke();
    ctx.shadowBlur = 0;

    // City label (name above, code below)
    ctx.fillStyle = '#f1f5f9';
    ctx.font = 'bold 12px Inter, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(n.name, n.px, n.py + 4);

    // AQI badge
    ctx.fillStyle = n.color;
    ctx.font = '10px Inter, sans-serif';
    ctx.fillText(`AQI ${n.aqi}`, n.px, n.py + NODE_RADIUS + 14);
}

// Draw one directed edge (source → target) with animated dash
function drawEdge(ctx, src, tgt, edge, dashOffset) {
    const dx = tgt.px - src.px;
    const dy = tgt.py - src.py;
    const len = Math.sqrt(dx * dx + dy * dy);
    const ux = dx / len, uy = dy / len;

    // Offset start/end so lines don't overlap the node circles
    const startX = src.px + ux * (NODE_RADIUS + 4);
    const startY = src.py + uy * (NODE_RADIUS + 4);
    const endX   = tgt.px - ux * (NODE_RADIUS + 10);
    const endY   = tgt.py - uy * (NODE_RADIUS + 10);

    // Build curved path (slight arc for bidirectional edges)
    const mx = (startX + endX) / 2 + uy * 18;
    const my = (startY + endY) / 2 - ux * 18;

    ctx.beginPath();
    ctx.moveTo(startX, startY);
    ctx.quadraticCurveTo(mx, my, endX, endY);
    ctx.strokeStyle = edge.color;
    ctx.lineWidth = 2;
    ctx.setLineDash([8, 6]);
    ctx.lineDashOffset = -dashOffset;
    ctx.shadowColor = edge.color;
    ctx.shadowBlur = 6;
    ctx.stroke();
    ctx.setLineDash([]);
    ctx.shadowBlur = 0;

    // Arrowhead at end
    const angle = Math.atan2(endY - my, endX - mx);
    const aLen = 9;
    ctx.beginPath();
    ctx.moveTo(endX, endY);
    ctx.lineTo(endX - aLen * Math.cos(angle - 0.4), endY - aLen * Math.sin(angle - 0.4));
    ctx.lineTo(endX - aLen * Math.cos(angle + 0.4), endY - aLen * Math.sin(angle + 0.4));
    ctx.closePath();
    ctx.fillStyle = edge.color;
    ctx.fill();

    // Mid-label: distance + avg_aqi
    const lx = (startX + endX) / 2 + uy * 20;
    const ly = (startY + endY) / 2 - ux * 20;
    ctx.fillStyle = 'rgba(15,23,42,0.8)';
    ctx.beginPath();
    ctx.roundRect(lx - 28, ly - 11, 56, 17, 4);
    ctx.fill();
    ctx.fillStyle = edge.color;
    ctx.font = 'bold 9.5px Inter, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(`${edge.distance}km · AQI${edge.avg_aqi}`, lx, ly + 1);
}

function drawNetwork(canvas, nodes, edges, dashOffset) {
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const scaled = scaleNodes(nodes, canvas);

    // Edges first
    edges.forEach(e => {
        const src = nodeById(scaled, e.source);
        const tgt = nodeById(scaled, e.target);
        if (src && tgt) drawEdge(ctx, src, tgt, e, dashOffset);
    });

    // Nodes on top
    scaled.forEach(n => drawNode(ctx, n));
}

function startNetworkAnimation(canvas) {
    if (networkAnimationId) cancelAnimationFrame(networkAnimationId);
    function frame() {
        if (!networkData) return;
        networkDashOffset = (networkDashOffset + 0.4) % 28;
        drawNetwork(canvas, networkData.nodes, networkData.edges, networkDashOffset);
        networkAnimationId = requestAnimationFrame(frame);
    }
    networkAnimationId = requestAnimationFrame(frame);
}

function populateEdgeTable(edges, nodes) {
    const tbody = document.getElementById('network-edge-tbody');
    if (!tbody) return;
    tbody.innerHTML = '';
    const nodeMap = Object.fromEntries(nodes.map(n => [n.id, n.name]));
    edges.forEach(e => {
        const aqiLabel = e.avg_aqi <= 50 ? 'Good' :
                         e.avg_aqi <= 100 ? 'Moderate' :
                         e.avg_aqi <= 150 ? 'Unhealthy (Sensitive)' :
                         e.avg_aqi <= 200 ? 'Unhealthy' :
                         e.avg_aqi <= 300 ? 'Very Unhealthy' : 'Hazardous';
        const tr = document.createElement('tr');
        tr.style.cssText = 'border-bottom: 1px solid rgba(255,255,255,0.05);';
        tr.innerHTML = `
            <td style="padding:0.6rem 0.75rem; color:#e2e8f0;">${nodeMap[e.source] || e.source}</td>
            <td style="padding:0.6rem 0.75rem; color:#e2e8f0;">${nodeMap[e.target] || e.target}</td>
            <td style="padding:0.6rem 0.75rem; text-align:right; color:#94a3b8;">${e.distance} km</td>
            <td style="padding:0.6rem 0.75rem; text-align:right; font-weight:bold; color:${e.color};">${e.avg_aqi}</td>
            <td style="padding:0.6rem 0.75rem; text-align:right; color:#94a3b8;">${e.pollution.toFixed(4)}</td>
            <td style="padding:0.6rem 0.75rem; color:${e.color}; font-size:12px;">${aqiLabel}</td>
        `;
        tbody.appendChild(tr);
    });
}

// Hover tooltip
function setupNetworkHover(canvas, nodes) {
    const tooltip = document.getElementById('network-tooltip');
    if (!tooltip) return;
    const scaled = scaleNodes(nodes, canvas);
    canvas.addEventListener('mousemove', (evt) => {
        const rect = canvas.getBoundingClientRect();
        const scaleX = canvas.width  / rect.width;
        const scaleY = canvas.height / rect.height;
        const mx = (evt.clientX - rect.left) * scaleX;
        const my = (evt.clientY - rect.top)  * scaleY;

        const hit = scaled.find(n => {
            const dx = mx - n.px, dy = my - n.py;
            return Math.sqrt(dx*dx + dy*dy) <= NODE_RADIUS + 6;
        });

        if (hit) {
            tooltip.style.display = 'block';
            tooltip.style.left = (evt.clientX - rect.left + 14) + 'px';
            tooltip.style.top  = (evt.clientY - rect.top  + 14) + 'px';
            tooltip.innerHTML = `
                <div style="font-weight:700; color:${hit.color}; margin-bottom:4px;">📍 ${hit.name}</div>
                <div style="color:#94a3b8;">AQI: <b style="color:${hit.color}">${hit.aqi}</b> — ${hit.category}</div>
                <div style="color:#94a3b8; margin-top:2px;">Pollution weight: ${hit.pollution_weight}</div>
            `;
        } else {
            tooltip.style.display = 'none';
        }
    });
    canvas.addEventListener('mouseleave', () => { tooltip.style.display = 'none'; });
}

window.networkLoaded = false;

async function loadNetworkGraph(force = false) {
    if (window.networkLoaded && !force) return;
    const loader = document.getElementById('network-loading');
    const canvas = document.getElementById('network-canvas');
    if (!canvas) return;

    if (loader) loader.classList.remove('hidden');
    if (networkAnimationId) { cancelAnimationFrame(networkAnimationId); networkAnimationId = null; }

    try {
        const res  = await fetch('/api/v1/route-network');
        if (!res.ok) throw new Error('Network API error');
        networkData = await res.json();

        // Resize canvas to actual display width maintaining aspect ratio
        const displayW = canvas.clientWidth || 900;
        canvas.width  = displayW > 0 ? displayW : 900;
        canvas.height = Math.round(canvas.width * (480 / 900));

        populateEdgeTable(networkData.edges, networkData.nodes);
        setupNetworkHover(canvas, networkData.nodes);
        startNetworkAnimation(canvas);
        window.networkLoaded = true;
    } catch (err) {
        console.error('Route network:', err);
        const ctx = canvas.getContext('2d');
        ctx.fillStyle = '#ef4444';
        ctx.font = '14px Inter, sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText('Failed to load route network data.', canvas.width / 2, canvas.height / 2);
    } finally {
        if (loader) loader.classList.add('hidden');
    }
}

// Refresh button
document.getElementById('btn-refresh-network')?.addEventListener('click', () => {
    window.networkLoaded = false;
    loadNetworkGraph(true);
});

// Pause animation when tab is hidden, resume when visible
document.addEventListener('visibilitychange', () => {
    if (document.hidden && networkAnimationId) {
        cancelAnimationFrame(networkAnimationId);
        networkAnimationId = null;
    } else if (!document.hidden && networkData && !viewNetwork.classList.contains('hidden')) {
        const c = document.getElementById('network-canvas');
        if (c) startNetworkAnimation(c);
    }
});
