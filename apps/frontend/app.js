// --- DOM Elements ---
const btnRoute = document.getElementById('btn-route');
const btnAqi = document.getElementById('btn-aqi');
const btnTasks = document.getElementById('btn-tasks');
const viewRoute = document.getElementById('view-route');
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

const CITY_COORDS = {
    "A": [28.6139, 77.2090], // Delhi
    "B": [26.9124, 75.7873], // Jaipur
    "C": [27.1767, 78.0081], // Agra
    "D": [25.3176, 82.9739], // Varanasi
    "E": [26.8467, 80.9462], // Lucknow
    "F": [22.5726, 88.3639], // Kolkata
};

// --- Tab Switching ---
function hideAll() {
    [viewRoute, viewAqi, viewTasks].forEach(v => {
        v.classList.add('hidden');
        v.classList.remove('animate-in');
    });
    [btnRoute, btnAqi, btnTasks].forEach(b => b.classList.remove('active'));
}

btnRoute.addEventListener('click', () => {
    hideAll();
    viewRoute.classList.remove('hidden');
    viewRoute.classList.add('animate-in');
    btnRoute.classList.add('active');
    setTimeout(() => map.invalidateSize(), 100);
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

// --- Route Optimization Logic ---
const btnSubmit = document.getElementById('submit-route');
const routeLoading = document.getElementById('route-loading');
const routeResults = document.getElementById('route-results');
const routeError = document.getElementById('route-error');

btnSubmit.addEventListener('click', async () => {
    const start = document.getElementById('start-node').value;
    const end = document.getElementById('end-node').value;
    
    // UI Reset
    routeResults.classList.add('hidden');
    routeError.classList.add('hidden');
    routeLoading.classList.remove('hidden');

    try {
        const response = await fetch('/api/v1/eco-route', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ start, end })
        });
        
        if (!response.ok) throw new Error(`API Error: ${response.statusText}`);
        
        const data = await response.json();
        renderRouteResults(data);
    } catch (err) {
        routeError.textContent = err.message;
        routeError.classList.remove('hidden');
    } finally {
        routeLoading.classList.add('hidden');
    }
});

function renderRouteResults(data) {
    const credits = data.exposure_credits || {};
    
    // Credits
    const cChange = credits.final_credit_change || 0;
    const sign = cChange > 0 ? '+' : '';
    const cColor = cChange >= 0 ? '#10b981' : '#f43f5e';
    
    const elCred = document.getElementById('res-credits');
    elCred.textContent = `${sign}${cChange}`;
    elCred.style.color = cColor;
    
    document.getElementById('res-grade').textContent = `${credits.overall_emoji || ''} Grade ${credits.overall_grade || '?'}`;
    
    // Advantage
    document.getElementById('res-advantage').textContent = data.improvement || '0%';
    
    // Summary line
    const routeArr = data.route || [];
    document.getElementById('res-path').textContent = routeArr.join(' → ');
    document.getElementById('res-dist').textContent = `Distance: ${Math.round(data.total_distance)} km`;
    document.getElementById('res-exp').textContent = `Exposure: ${Math.round(data.total_pollution)}`;

    // Map Updates
    if (currentRouteLayer) map.removeLayer(currentRouteLayer);
    const coords = routeArr.map(n => CITY_COORDS[n]).filter(Boolean);
    
    if (coords.length > 0) {
        currentRouteLayer = L.featureGroup().addTo(map);
        // Draw polyline
        L.polyline(coords, {
            color: '#10b981',
            weight: 5,
            opacity: 0.8,
            dashArray: "10 5"
        }).addTo(currentRouteLayer);
        
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
        map.fitBounds(currentRouteLayer.getBounds(), {padding: [50, 50]});
    }

    // Segments
    const segContainer = document.getElementById('segment-container');
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
                <div style="font-weight:600; color: #e2e8f0;">${s.from} → ${s.to}</div>
                <div style="color: #94a3b8;">AQI: ${s.avg_aqi}</div>
                <div style="color: ${s.credit_delta >= 0 ? '#10b981' : '#f43f5e'}; font-weight:600;">
                    ${s.emoji} ${segSign}${s.credit_delta}
                </div>
            `;
            segContainer.appendChild(row);
        });
    }

    routeResults.classList.remove('hidden');
    routeResults.classList.add('animate-in');
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

async function loadTasksData() {
    const container = document.getElementById('tasks-container');
    const loader = document.getElementById('tasks-loading');
    
    try {
        const res = await fetch('/tasks');
        if (!res.ok) throw new Error('Tasks API failed');
        const data = await res.json();
        
        container.innerHTML = '';
        const tasks = data.tasks || [];

        tasks.forEach(t => {
            const passStyle = "color: var(--accent-primary); font-weight: bold;";
            const card = document.createElement('div');
            card.className = 'glass route-form-card';
            
            card.innerHTML = `
                <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                    <h3 style="color:var(--text-primary); margin-bottom:0.5rem; font-size:1.2rem;">${t.name}</h3>
                    <span style="background: rgba(148, 163, 184, 0.2); padding: 4px 8px; border-radius: 4px; font-size: 0.75rem; text-transform: uppercase;">
                        ${t.difficulty}
                    </span>
                </div>
                <p style="color: var(--text-secondary); font-size: 0.95rem; margin-bottom: 1rem;">${t.description}</p>
                <div style="background: rgba(0,0,0,0.3); padding: 1rem; border-radius: 8px;">
                    <div style="display:flex; justify-content:space-between; margin-bottom:0.5rem;">
                        <span style="color: var(--text-secondary);">Start → Target</span>
                        <span style="color: #fff; font-weight: 600;">${t.start} → ${t.destination}</span>
                    </div>
                    <div style="display:flex; justify-content:space-between; margin-bottom:0.5rem;">
                        <span style="color: var(--text-secondary);">Max Steps Budget</span>
                        <span style="color: #fff; font-weight: 600;">${t.max_steps} moves</span>
                    </div>
                    <div style="display:flex; justify-content:space-between;">
                        <span style="color: var(--text-secondary);">Passing Score Required</span>
                        <span style="${passStyle}">${t.passing_score.toFixed(2)}</span>
                    </div>
                </div>
            `;
            container.appendChild(card);
        });
        
        window.tasksLoaded = true;
    } catch (err) {
        console.error(err);
        container.innerHTML = `<p style="color: #ef4444;">Failed to load Hackathon Tasks definitions.</p>`;
    } finally {
        loader.classList.add('hidden');
    }
}
