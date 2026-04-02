// --- DOM Elements ---
const btnRoute = document.getElementById('btn-route');
const btnAqi = document.getElementById('btn-aqi');
const viewRoute = document.getElementById('view-route');
const viewAqi = document.getElementById('view-aqi');

// --- Tab Switching ---
function switchTab(showRef, hideRef, btnActive, btnInactive) {
    hideRef.classList.add('hidden');
    hideRef.classList.remove('animate-in');
    
    showRef.classList.remove('hidden');
    showRef.classList.add('animate-in');
    
    btnActive.classList.add('active');
    btnInactive.classList.remove('active');
}

btnRoute.addEventListener('click', () => switchTab(viewRoute, viewAqi, btnRoute, btnAqi));
btnAqi.addEventListener('click', () => {
    switchTab(viewAqi, viewRoute, btnAqi, btnRoute);
    if (!window.aqiLoaded) loadAqiData();
});

// --- Route Optimization Logic ---
const btnSubmit = document.getElementById('submit-route');
const routeLoading = document.getElementById('route-loading');
const routeResults = document.getElementById('route-results');
const routeError = document.getElementById('route-error');

btnSubmit.addEventListener('click', async () => {
    const start = document.getElementById('start-node').value.trim().toUpperCase();
    const end = document.getElementById('end-node').value.trim().toUpperCase();
    
    if (!start || !end) return;

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
    document.getElementById('res-path').textContent = (data.route || []).join(' → ');
    document.getElementById('res-dist').textContent = `Distance: ${Math.round(data.total_distance)} km`;
    document.getElementById('res-exp').textContent = `Exposure: ${Math.round(data.total_pollution)}`;

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
        
        // Sort highest AQI first
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
