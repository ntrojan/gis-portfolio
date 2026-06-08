//##########################################################################################################################################################
//1. Initialisation de la carte

// Définition du territoire Suisse
const switzerlandBounds = [[45.817993, 5.955911], [47.808455, 10.49205]];

// Initialisation de la carte
const map = L.map("map", {
    maxBounds: switzerlandBounds,
    maxBoundsViscosity: 1.0,
    zoomSnap: 0.5,
    minZoom: 7
});
const pathsLayer = L.layerGroup().addTo(map);
const cheminsPath = './data/chemins.geojson';
const geojsonPath = './data/spot_all.geojson';

// Ajouter le layer Tile
L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    minZoom: 7,
    attribution: "© OpenStreetMap contributors"
}).addTo(map);

// Frame Switzerland, padding for the side panels so no canton stays hidden
function frameSwitzerland() {
    const narrow = window.innerWidth <= 820;
    map.fitBounds(switzerlandBounds, narrow
        ? { padding: [20, 20] }
        : { paddingTopLeft: [262, 28], paddingBottomRight: [Math.round(window.innerWidth * 0.24) + 28, 52] });
}
frameSwitzerland();

//##########################################################################################################################################################
//2. Clusters

// Icone SVG (Loup gris)
const wolfIconHtmlCluster = `
    <svg height="80px" width="65px" version="1.1" id="_x34_" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" 
        viewBox="0 0 512 512"  xml:space="preserve">
        <g>
            <path style="fill:#C0B495;" d="M343.736,404.417c0,31.472-25.509,56.984-56.981,56.984h-61.511
            c-31.465,0-56.981-25.512-56.981-56.984l0,0c0-31.472,25.516-56.984,56.981-56.984h61.511
            C318.227,347.433,343.736,372.945,343.736,404.417L343.736,404.417z"/>
            <path style="fill:#92959D;" d="M300.341,72.46c0,0,43.416-54.272,54.276-65.126C365.47-3.52,384.46-3.52,389.89,15.472
            c5.423,18.996,37.992,116.687,37.992,116.687L512,320.295h-45.516v45.227l-38.898-8.142l-13.566,38.895l-36.179-16.281
            l-18.09,34.374l-58.898-33.924l-47.834,23.07h5.963l-47.835-23.07l-58.898,33.924l-18.09-34.374l-36.18,16.281L84.414,357.38
            l-38.898,8.142v-45.227H0l84.118-188.136c0,0,32.568-97.691,37.992-116.687c5.43-18.992,24.426-18.992,35.28-8.138
            c10.853,10.853,54.269,65.126,54.269,65.126H300.341z"/>
        <g>
        <g>
            <polygon style="fill:#FEFFFF;" points="182.728,100.5 147.455,54.37 133.89,100.5 "/>
        </g>
        <g>
            <polygon style="fill:#FEFFFF;" points="329.272,100.5 364.544,54.37 378.11,100.5 "/>
        </g>
        </g>
            <path style="fill:#FEFFFF;" d="M256,403.514h32.562c0,0,27.328,1.084,48.307-19.898c25.326-25.326,35.135-78.019,35.135-78.019
            c22.384-3.391,64.322-66.567,18.313-108.314c-48.839-44.321-127.534,3.165-118.486,79.145v74.584l14.38,39.84L256,394.469v1.806
            l-30.217-3.615l14.386-39.84v-74.585c9.041-75.983-69.647-123.469-118.492-79.145c-46.002,41.747-4.071,104.924,18.313,108.315
            c0,0,9.816,52.69,35.135,78.015c20.985,20.985,48.307,19.899,48.307,19.899H256V403.514z"/>
        <g>
        <g>
            <path style="fill:#564236;" d="M180.614,252.88h-18.609l6.021,8.162c-0.781,1.733-1.228,3.628-1.228,5.636
            c0,7.63,6.178,13.819,13.815,13.819c7.617,0,13.802-6.189,13.802-13.819C194.416,259.062,188.231,252.88,180.614,252.88z"/>
        </g>
        <g>
            <path style="fill:#564236;" d="M331.386,252.88h18.609l-6.014,8.162c0.775,1.733,1.221,3.628,1.221,5.636
            c0,7.63-6.179,13.819-13.815,13.819c-7.617,0-13.802-6.189-13.802-13.819C317.584,259.062,323.769,252.88,331.386,252.88z"/>
        </g>
        </g>
            <path style="fill:#71605B;" d="M283.046,383.839c-5.759,0-27.046,0-27.046,0s-21.294,0-27.046,0
            c-16.113,0-26.461,19.56-13.802,35.673c15.779,20.092,30.487,20.713,40.848,20.713c10.354,0,25.063-0.621,40.848-20.713
            C309.514,403.399,299.159,383.839,283.046,383.839z"/>
        </g>
            <path style="opacity:0.23;fill:#71605B;" d="M427.882,132.159c0,0-32.568-97.691-37.992-116.687
            C384.46-3.52,365.47-3.52,354.617,7.334c-10.86,10.853-54.276,65.126-54.276,65.126h-49.659v388.941h36.074
            c31.228,0,56.561-25.135,56.948-56.275l16.048,9.242l18.09-34.374l36.179,16.281l13.566-38.895l38.898,8.142v-45.227H512
            L427.882,132.159z"/>
        </g>
    </svg>`
    ;

// Configuration clusters 
const markers = L.markerClusterGroup({
    iconCreateFunction: (cluster) => {
        // Nb. marqueurs par cluster
        const count = cluster.getChildCount();

        // HTML icône cluster
        return L.divIcon({
            html: `
                <div style="position: relative; text-align: center; width: 60px; height: 60px;">
                    <div style="position: absolute; top: 10px; left: 10px; width: 40px; height: 40px;">
                        ${wolfIconHtmlCluster} 
                    </div>
                    <div style="position: absolute; top: 0; left: 0; width: 60px; height: 60px; display: flex; align-items: center; justify-content: center;">
                        <div style="background: white; border: 2px solid black; border-radius: 50%; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; font-size: 14px; font-weight: bold;">
                            ${count} <!-- Affiche le nombre de marqueurs dans le cluster -->
                        </div>
                    </div>
                </div>`,
            className: '', 
            iconSize: [60, 60], 
        });
    }
});

// Ajoute à la carte
map.addLayer(markers);

//##########################################################################################################################################################
//3. Données et variables

// Variables 
let pathsByWolf = {}; // Wolf paths
let data = []; // Observation data
let filteredData = []; // Filtered data
let animatedLayer = null; // Path animation
let scatterData = []; // Scatter-plot (time travel) data

// Graphiques de defaut
fetch(geojsonPath)
    .then(response => response.json())
    .then(geojsonData => {

    // Conversion geojson
    data = geojsonData.features.map(feature => ({
            lat: feature.geometry.coordinates[1],
            lon: feature.geometry.coordinates[0],
            wolfID: feature.properties.joint_wolf_id,
            year: feature.properties.joint_date.split("-")[0],
            canton: feature.properties.joint_nom_canton,
            gender: feature.properties.joint_sexe,
            commune: feature.properties.name,
            date: feature.properties.joint_date
        }));

        // Afficher les graphiques par défaut
        createYearChart(data); 
        createCantonChartStatic(data); 

        // Afficher les marqueurs par defaut
        addAllMarkers(data);
        
        // Scatter-plot data
        scatterData = geojsonData.features.map(feature => ({
            id: feature.properties.joint_wolf_id,
            longitude: feature.geometry.coordinates[0],
            latitude: feature.geometry.coordinates[1],
            year: new Date(feature.properties.joint_date).getFullYear(),
            gender: feature.properties.joint_sexe
        }));

        // Build scatter-plot
        createTimeTravelScatterPlot(scatterData);
    })


// Données des déplacements
fetch(cheminsPath)
    .then(response => response.json())
    .then(cheminsData => {
        console.log("Movement data loaded:", cheminsData);

        // Liaison avec ID
        cheminsData.features.forEach(feature => {
            const wolfID = feature.properties.joint_wolf_id; 
            if (!pathsByWolf[wolfID]) {
                pathsByWolf[wolfID] = [];
            }
            pathsByWolf[wolfID].push(feature); 
        });


    })

//####################################################################################################################################################
//4. Fonctions d'animations, interactivité

//4.1 Animations pour les chemins ###############################################################################################################

// Palette used to tell apart the paths of several selected wolves
const PATH_PALETTE = ['#81c784', '#4fc3f7', '#f48fb1', '#ffb74d', '#ba68c8', '#4db6ac', '#e57373', '#fff176'];

// Draw the path(s) of one or more wolves
function showWolfPaths(wolfIDs) {
    // Accept a single ID (string) or an array of IDs
    const ids = Array.isArray(wolfIDs) ? wolfIDs : [wolfIDs];

    // Clear existing paths and any running animation
    pathsLayer.clearLayers();
    if (animatedLayer) {
        map.removeLayer(animatedLayer);
        clearInterval(animatedLayer.animationInterval);
        animatedLayer = null;
    }

    const allCoordinates = [];

    ids.forEach((wolfID, i) => {
        const paths = pathsByWolf[wolfID];
        if (!paths || paths.length === 0) {
            console.warn(`No path found for ${wolfID}`);
            return;
        }

        // Chronological order
        const sortedPaths = [...paths].sort((a, b) =>
            new Date(a.properties.joint_date) - new Date(b.properties.joint_date));

        const coordinates = [];
        const color = PATH_PALETTE[i % PATH_PALETTE.length];

        sortedPaths.forEach(path => {
            const coords = path.geometry.coordinates;
            if (!coords || coords.length === 0) {
                console.warn("Segment without coordinates, skipped.");
                return;
            }
            coords.forEach(coord => {
                const latLng = [coord[1], coord[0]];
                coordinates.push(latLng);
                allCoordinates.push(latLng);

                // Observation point
                L.circleMarker(latLng, {
                    radius: 4,
                    color: color,
                    weight: 1.5,
                    fillColor: '#0a0e1a',
                    fillOpacity: 0.85
                })
                .bindPopup(`Observation: ${JSON.stringify(path.properties)}`)
                .addTo(pathsLayer);
            });
        });

        if (coordinates.length === 0) return;

        // Trace the path
        L.polyline(coordinates, { color: color, weight: 2, opacity: 0.9 }).addTo(pathsLayer);

        // Animate only when a single wolf is selected
        if (ids.length === 1) animatePath(coordinates);
    });

    // Zoom to fit every drawn path
    if (allCoordinates.length > 0) {
        map.fitBounds(L.latLngBounds(allCoordinates), { padding: [25, 25] });
    }
}

    function animatePath(coordinates) {
        let index = 0;

    // Supprimer animations précédentes
    if (animatedLayer) {
        map.removeLayer(animatedLayer);
    }

    // Nouveau layer animation
    animatedLayer = L.layerGroup().addTo(map);

    // Icône SVG (loup gris)
    const wolfIconHtml = `
    <svg height="40px" width="40px" version="1.1" id="_x34_" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" 
	viewBox="0 0 512 512"  xml:space="preserve">
        <g>
	    <g>
		    <path style="fill:#C0B495;" d="M343.736,404.417c0,31.472-25.509,56.984-56.981,56.984h-61.511
			c-31.465,0-56.981-25.512-56.981-56.984l0,0c0-31.472,25.516-56.984,56.981-56.984h61.511
			C318.227,347.433,343.736,372.945,343.736,404.417L343.736,404.417z"/>
		    <path style="fill:#92959D;" d="M300.341,72.46c0,0,43.416-54.272,54.276-65.126C365.47-3.52,384.46-3.52,389.89,15.472
			c5.423,18.996,37.992,116.687,37.992,116.687L512,320.295h-45.516v45.227l-38.898-8.142l-13.566,38.895l-36.179-16.281
			l-18.09,34.374l-58.898-33.924l-47.834,23.07h5.963l-47.835-23.07l-58.898,33.924l-18.09-34.374l-36.18,16.281L84.414,357.38
			l-38.898,8.142v-45.227H0l84.118-188.136c0,0,32.568-97.691,37.992-116.687c5.43-18.992,24.426-18.992,35.28-8.138
			c10.853,10.853,54.269,65.126,54.269,65.126H300.341z"/>
		<g>
		<g>
			<polygon style="fill:#FEFFFF;" points="182.728,100.5 147.455,54.37 133.89,100.5 				"/>
		</g>
		<g>
			<polygon style="fill:#FEFFFF;" points="329.272,100.5 364.544,54.37 378.11,100.5 				"/>
		</g>
		</g>
		    <path style="fill:#FEFFFF;" d="M256,403.514h32.562c0,0,27.328,1.084,48.307-19.898c25.326-25.326,35.135-78.019,35.135-78.019
			c22.384-3.391,64.322-66.567,18.313-108.314c-48.839-44.321-127.534,3.165-118.486,79.145v74.584l14.38,39.84L256,394.469v1.806
			l-30.217-3.615l14.386-39.84v-74.585c9.041-75.983-69.647-123.469-118.492-79.145c-46.002,41.747-4.071,104.924,18.313,108.315
			c0,0,9.816,52.69,35.135,78.015c20.985,20.985,48.307,19.899,48.307,19.899H256V403.514z"/>
		<g>
		<g>
			<path style="fill:#564236;" d="M180.614,252.88h-18.609l6.021,8.162c-0.781,1.733-1.228,3.628-1.228,5.636
			c0,7.63,6.178,13.819,13.815,13.819c7.617,0,13.802-6.189,13.802-13.819C194.416,259.062,188.231,252.88,180.614,252.88z"/>
		</g>
		<g>
			<path style="fill:#564236;" d="M331.386,252.88h18.609l-6.014,8.162c0.775,1.733,1.221,3.628,1.221,5.636
			c0,7.63-6.179,13.819-13.815,13.819c-7.617,0-13.802-6.189-13.802-13.819C317.584,259.062,323.769,252.88,331.386,252.88z"/>
		</g>
		</g>
		    <path style="fill:#71605B;" d="M283.046,383.839c-5.759,0-27.046,0-27.046,0s-21.294,0-27.046,0
			c-16.113,0-26.461,19.56-13.802,35.673c15.779,20.092,30.487,20.713,40.848,20.713c10.354,0,25.063-0.621,40.848-20.713
			C309.514,403.399,299.159,383.839,283.046,383.839z"/>
	    </g>
	        <path style="opacity:0.23;fill:#71605B;" d="M427.882,132.159c0,0-32.568-97.691-37.992-116.687
		    C384.46-3.52,365.47-3.52,354.617,7.334c-10.86,10.853-54.276,65.126-54.276,65.126h-49.659v388.941h36.074
		    c31.228,0,56.561-25.135,56.948-56.275l16.048,9.242l18.09-34.374l36.179,16.281l13.566-38.895l38.898,8.142v-45.227H512
		    L427.882,132.159z"/>
        </g>
    </svg>`;

    // Marqueur avec icone SVG
    const animatedMarker = L.divIcon({
        html: wolfIconHtml,
        className: '' 
    });

    // Ajoute marqueur
    const marker = L.marker(coordinates[0], { icon: animatedMarker }).addTo(animatedLayer);

    // Mise à jour marqueur 
    function updateMarker() {
        if (index < coordinates.length - 1) {
            index++;
            marker.setLatLng(coordinates[index]); 
        } else {
            index = 0; // Restart from the beginning
            marker.setLatLng(coordinates[index]); 
        }
    }

    // Vitesse animation
    const animationInterval = setInterval(updateMarker, 800);
    animatedLayer.animationInterval = animationInterval;
}

//4.2 Marquers #####################################################################################################################################

// Chargements données chemin
fetch(geojsonPath)
    .then(response => response.json())
    .then(geojsonData => {
        console.log("GeoJSON data loaded:", geojsonData);

        // Conversion GeoJSON
        data = geojsonData.features.map(feature => ({
            lat: feature.geometry.coordinates[1],
            lon: feature.geometry.coordinates[0],
            wolfID: feature.properties.joint_wolf_id,
            year: feature.properties.joint_date.split("-")[0],
            canton: feature.properties.joint_nom_canton,
            gender: feature.properties.joint_sexe,
            commune: feature.properties.name,
            date: feature.properties.joint_date
        }));

        console.log("Data transformed for markers:", data);

        // Show all markers by default
        addAllMarkers(data);
    })
    .catch(error => console.error("Error loading markers:", error));

// Icone SVG (loup gris)
const wolfIconHtml = `
    <svg height="40px" width="40px" version="1.1" id="_x34_" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" 
    viewBox="0 0 512 512"  xml:space="preserve">
        <g>
        <g>
            <path style="fill:#C0B495;" d="M343.736,404.417c0,31.472-25.509,56.984-56.981,56.984h-61.511
            c-31.465,0-56.981-25.512-56.981-56.984l0,0c0-31.472,25.516-56.984,56.981-56.984h61.511
            C318.227,347.433,343.736,372.945,343.736,404.417L343.736,404.417z"/>
            <path style="fill:#92959D;" d="M300.341,72.46c0,0,43.416-54.272,54.276-65.126C365.47-3.52,384.46-3.52,389.89,15.472
            c5.423,18.996,37.992,116.687,37.992,116.687L512,320.295h-45.516v45.227l-38.898-8.142l-13.566,38.895l-36.179-16.281
            l-18.09,34.374l-58.898-33.924l-47.834,23.07h5.963l-47.835-23.07l-58.898,33.924l-18.09-34.374l-36.18,16.281L84.414,357.38
            l-38.898,8.142v-45.227H0l84.118-188.136c0,0,32.568-97.691,37.992-116.687c5.43-18.992,24.426-18.992,35.28-8.138
            c10.853,10.853,54.269,65.126,54.269,65.126H300.341z"/>
        <g>
        <g>
            <polygon style="fill:#FEFFFF;" points="182.728,100.5 147.455,54.37 133.89,100.5 "/>
        </g>
        <g>
            <polygon style="fill:#FEFFFF;" points="329.272,100.5 364.544,54.37 378.11,100.5 "/>
        </g>
        </g>
            <path style="fill:#FEFFFF;" d="M256,403.514h32.562c0,0,27.328,1.084,48.307-19.898c25.326-25.326,35.135-78.019,35.135-78.019
            c22.384-3.391,64.322-66.567,18.313-108.314c-48.839-44.321-127.534,3.165-118.486,79.145v74.584l14.38,39.84L256,394.469v1.806
            l-30.217-3.615l14.386-39.84v-74.585c9.041-75.983-69.647-123.469-118.492-79.145c-46.002,41.747-4.071,104.924,18.313,108.315
            c0,0,9.816,52.69,35.135,78.015c20.985,20.985,48.307,19.899,48.307,19.899H256V403.514z"/>
        <g>
        <g>
            <path style="fill:#564236;" d="M180.614,252.88h-18.609l6.021,8.162c-0.781,1.733-1.228,3.628-1.228,5.636
            c0,7.63,6.178,13.819,13.815,13.819c7.617,0,13.802-6.189,13.802-13.819C194.416,259.062,188.231,252.88,180.614,252.88z"/>
        </g>
        <g>
            <path style="fill:#564236;" d="M331.386,252.88h18.609l-6.014,8.162c0.775,1.733,1.221,3.628,1.221,5.636
            c0,7.63-6.179,13.819-13.815,13.819c-7.617,0-13.802-6.189-13.802-13.819C317.584,259.062,323.769,252.88,331.386,252.88z"/>
        </g>
        </g>
            <path style="fill:#71605B;" d="M283.046,383.839c-5.759,0-27.046,0-27.046,0s-21.294,0-27.046,0
            c-16.113,0-26.461,19.56-13.802,35.673c15.779,20.092,30.487,20.713,40.848,20.713c10.354,0,25.063-0.621,40.848-20.713
            C309.514,403.399,299.159,383.839,283.046,383.839z"/>
        </g>
            <path style="opacity:0.23;fill:#71605B;" d="M427.882,132.159c0,0-32.568-97.691-37.992-116.687
            C384.46-3.52,365.47-3.52,354.617,7.334c-10.86,10.853-54.276,65.126-54.276,65.126h-49.659v388.941h36.074
            c31.228,0,56.561-25.135,56.948-56.275l16.048,9.242l18.09-34.374l36.179,16.281l13.566-38.895l38.898,8.142v-45.227H512
            L427.882,132.159z"/>
        </g>
    </svg>`;

// Création icône 
function createWolfIcon() {
    return L.divIcon({
        className: '', 
        html: wolfIconHtml,
        iconSize: [30, 30], 
        iconAnchor: [15, 15] 
    });
}

// Ajoute marqueurs 
function addAllMarkers(markerData) {
    markers.clearLayers();
    markerData.forEach(item => {
        const wolfData = markerData.filter(data => data.wolfID === item.wolfID);
        const uniqueCommunes = new Set(wolfData.map(data => data.commune));
        const totalDistance = calculateTotalDistance(wolfData);

        const marker = L.marker([item.lat, item.lon], {
            icon: createWolfIcon() 
        }).bindPopup(`
            <b>Municipality:</b> ${item.commune}<br>
            <b>Wolf ID:</b> ${item.wolfID}<br>
            <b>Date:</b> ${item.date}<br>
            <b>Straight-line distance travelled:</b> ${totalDistance} km<br>
            <b>Municipalities with observations:</b> ${uniqueCommunes.size}
        `);
        markers.addLayer(marker);
    });
    map.addLayer(markers);
}

//4.3 Infobox #####################################################################################################################################

// Calcul distance total
function calculateTotalDistance(wolfData) {
    let totalDistance = 0;
    for (let i = 1; i < wolfData.length; i++) {
        const prev = wolfData[i - 1];
        const curr = wolfData[i];
        const distance = turf.distance([prev.lon, prev.lat], [curr.lon, curr.lat], { units: 'kilometers' });
        totalDistance += distance;
    }
    return totalDistance.toFixed(2); // 2 ddcimales
}

// Mise à jour infobox
function updateWolfAnalysisPanel(wolfID, totalDistance, uniqueCommunes) {
    const panel = document.getElementById("wolf-analysis-panel");
    panel.innerHTML = `
        <h3>Wolf analysis: ${wolfID}</h3>
        <p><b>Total distance travelled:</b> ${totalDistance} km</p>
        <p><b>Number of municipalities visited:</b> ${uniqueCommunes}</p>
    `;
}

//4.4 Filters #####################################################################################################################################

// Read all selected values of a (multi-)select as an array, ignoring the empty option
function getSelectedValues(id) {
    return Array.from(document.getElementById(id).selectedOptions)
        .map(o => o.value)
        .filter(v => v !== "");
}

// Apply the filters
function applyFilters() {
    const gender = document.getElementById("filter-gender").value;      // single
    const years = getSelectedValues("filter-year");                     // multiple / range
    const cantons = getSelectedValues("filter-canton");                 // multiple
    const wolfIDs = getSelectedValues("filter-wolf-id");                // multiple

    // Filter the data (empty selection = no constraint = all)
    filteredData = data.filter(item =>
        (!gender || item.gender === gender) &&
        (years.length === 0 || years.includes(item.year)) &&
        (cantons.length === 0 || cantons.includes(item.canton)) &&
        (wolfIDs.length === 0 || wolfIDs.includes(item.wolfID))
    );

    // Stop any running animation
    if (animatedLayer) {
        map.removeLayer(animatedLayer);
        clearInterval(animatedLayer.animationInterval);
        animatedLayer = null;
    }

    // If one or more wolves are selected, draw their paths; otherwise show the filtered markers
    if (wolfIDs.length > 0) {
        markers.clearLayers();
        showWolfPaths(wolfIDs);
    } else {
        addAllMarkers(filteredData);
        pathsLayer.clearLayers();
    }

    // Refresh the charts with the filtered data
    updateCharts(filteredData);
}

function resetFilters() {
    // Clear filter values (single + multi-select)
    document.getElementById("filter-gender").value = "";
    ["filter-year", "filter-canton", "filter-wolf-id"].forEach(id => {
        Array.from(document.getElementById(id).options).forEach(o => o.selected = false);
    });

    // Restore the original data
    filteredData = data;

    // Refresh the map
    markers.clearLayers();
    addAllMarkers(filteredData);

    // Remove existing paths
    pathsLayer.clearLayers();

    // Stop the active animation
    if (animatedLayer) {
        map.removeLayer(animatedLayer);
        clearInterval(animatedLayer.animationInterval);
        animatedLayer = null;
    }

    // Reset the default framing
    frameSwitzerland();

    // Refresh the charts
    updateCharts(filteredData);
}


// 4.5 Charts #########################################################################################################################################
function updateCharts(filteredData) {
    // Refresh the charts
    createYearChart(filteredData);
    createCantonChartStatic(filteredData);
    createTimeTravelScatterPlot(scatterData);
}

// 4.5.a Observations per year
function createYearChart(data) {
    const container = document.getElementById("year-chart");

    // Dimensions et marges dynamique
    const margin = { top: 40, right: 10, bottom: 40, left: 10 };
    const width = container.clientWidth - margin.left - margin.right;
    const height = container.clientHeight - margin.top - margin.bottom;

    // Reactivité SVG
    const svg = d3.select("#year-chart").html("").append("svg")
        .attr("viewBox", `0 0 ${width + margin.left + margin.right} ${height + margin.top + margin.bottom}`)
        .attr("preserveAspectRatio", "xMidYMid meet")
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    // Préparation données
    const groupedData = d3.rollups(data, v => v.length, d => +d.year).sort((a, b) => a[0] - b[0]);

    // X 
    const x = d3.scaleBand()
        .domain(groupedData.map(d => d[0]))
        .range([0, width])
        .padding(0.1);

    // Y
    const y = d3.scaleLinear()
        .domain([0, d3.max(groupedData, d => d[1])])
        .range([height, 0]);

    // X axis
    svg.append("g")
        .attr("transform", `translate(0, ${height})`)
        .call(d3.axisBottom(x).ticks(Math.floor(width / 50)))
        .selectAll("text")
        .style("font-family", "DM Mono, monospace")
        .style("font-size", `${Math.max(width / 50, 8)}px`)
        .attr("transform", "rotate(-45)")
        .style("text-anchor", "end");

    // Bars
    svg.selectAll(".bar")
        .data(groupedData)
        .enter().append("rect")
        .attr("class", "bar")
        .attr("x", d => x(d[0]))
        .attr("y", d => y(d[1]))
        .attr("width", x.bandwidth())
        .attr("height", d => height - y(d[1]))
        .attr("rx", 2)
        .attr("fill", "#81c784");
    svg.selectAll(".bar-label")
        .data(groupedData)
        .enter().append("text")
        .attr("class", "bar-label")
        .attr("x", d => x(d[0]) + x.bandwidth() / 2)
        .attr("y", d => y(d[1]) - 5)
        .attr("text-anchor", "middle")
        .style("font-family", "DM Mono, monospace")
        .style("font-size", `${Math.max(width / 50, 8)}px`)
        .style("font-weight", "bold")
        .text(d => d[1]);

    // Title
    svg.append("text")
        .attr("class", "chart-title")
        .attr("x", width / 2)
        .attr("y", -margin.top / 2)
        .attr("text-anchor", "middle")
        .style("font-family", "Syne, sans-serif")
        .style("font-size", `${Math.max(width / 25, 13)}px`)
        .style("font-weight", "700")
        .text("Observations per year");
}

// Mise à jour avec redimensionnement 
window.addEventListener("resize", () => {
    createYearChart(data); 
    createCantonChartStatic(data); 
});

// 4.5.b Observations per canton
function createCantonChartStatic(data) {
    const container = document.getElementById("canton-chart");

    // Dimension et marges dynamiques
    const margin = { top: 40, right: 10, bottom: 40, left: 10 };
    const width = container.clientWidth - margin.left - margin.right;
    const height = container.clientHeight - margin.top - margin.bottom;

    // Reactivité SVG
    const svg = d3.select("#canton-chart").html("").append("svg")
        .attr("viewBox", `0 0 ${width + margin.left + margin.right} ${height + margin.top + margin.bottom}`)
        .attr("preserveAspectRatio", "xMidYMid meet")
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    const cantonCounts = d3.rollups(data, v => v.length, d => d.canton).sort((a, b) => b[1] - a[1]);

    // X
    const x = d3.scaleBand()
        .domain(cantonCounts.map(d => d[0]))
        .range([0, width])
        .padding(0.1);

    // Y
    const y = d3.scaleLinear()
        .domain([0, d3.max(cantonCounts, d => d[1])])
        .range([height, 0]);

    // X axis
    svg.append("g")
        .attr("transform", `translate(0, ${height})`)
        .call(d3.axisBottom(x).ticks(Math.floor(width / 50)))
        .selectAll("text")
        .style("font-family", "DM Mono, monospace")
        .style("font-size", `${Math.max(width / 50, 8)}px`)
        .attr("transform", "rotate(-45)")
        .style("text-anchor", "end");

    // Bars
    svg.selectAll(".bar")
        .data(cantonCounts)
        .enter().append("rect")
        .attr("class", "bar")
        .attr("x", d => x(d[0]))
        .attr("y", d => y(d[1]))
        .attr("width", x.bandwidth())
        .attr("height", d => height - y(d[1]))
        .attr("rx", 2)
        .attr("fill", "#81c784");
    svg.selectAll(".bar-label")
        .data(cantonCounts)
        .enter().append("text")
        .attr("class", "bar-label")
        .attr("x", d => x(d[0]) + x.bandwidth() / 2)
        .attr("y", d => y(d[1]) - 5)
        .attr("text-anchor", "middle")
        .style("font-family", "DM Mono, monospace")
        .style("font-size", `${Math.max(width / 50, 8)}px`)
        .style("font-weight", "bold")
        .text(d => d[1]);

    // Title
    svg.append("text")
        .attr("class", "chart-title")
        .attr("x", width / 2)
        .attr("y", -margin.top / 2)
        .attr("text-anchor", "middle")
        .style("font-family", "Syne, sans-serif")
        .style("font-size", `${Math.max(width / 25, 13)}px`)
        .style("font-weight", "700")
        .text("Observations per canton");
}

    // Redimensionnement
    window.addEventListener("resize", () => createCantonChartStatic(data));


// 4.5.c Lat-long time-travel chart
function createTimeTravelScatterPlot(originalData) {
    const container = document.getElementById("scatter-svg");

    // Reactive dimensions and margins
    const margin = { top: 40, right: 20, bottom: 40, left: 50 };
    const width = container.clientWidth - margin.left - margin.right;
    const height = container.clientHeight - margin.top - margin.bottom;

    // Reactive SVG
    const svg = d3.select("#scatter-svg").html("").append("svg")
        .attr("viewBox", `0 0 ${width + margin.left + margin.right} ${height + margin.top + margin.bottom}`)
        .attr("preserveAspectRatio", "xMidYMid meet")
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    // X
    const xScale = d3.scaleLinear()
        .domain(d3.extent(originalData, d => d.longitude))
        .nice()
        .range([0, width]);

    // Y    
    const yScale = d3.scaleLinear()
        .domain(d3.extent(originalData, d => d.latitude))
        .nice()
        .range([height, 0]);

    // X axis
    svg.append("g")
        .attr("transform", `translate(0, ${height})`)
        .call(d3.axisBottom(xScale).ticks(Math.floor(width / 50)))
        .selectAll("text")
        .style("font-family", "DM Mono, monospace")
        .style("font-size", `${Math.max(width / 50, 8)}px`);

    // Y axis
    svg.append("g")
        .call(d3.axisLeft(yScale).ticks(Math.floor(height / 50)))
        .selectAll("text")
        .style("font-family", "DM Mono, monospace")
        .style("font-size", `${Math.max(height / 50, 8)}px`);

    // Select points for the chosen year
    function update(year) {
        const filteredData = originalData.filter(d => d.year === year);
        const points = svg.selectAll("circle")
            .data(filteredData, d => d.id);

        points.enter()
            .append("circle")
            .attr("cx", d => xScale(d.longitude))
            .attr("cy", d => yScale(d.latitude))
            .attr("r", Math.max(width / 100, 3))
            .attr("fill", d => d.gender === "M" ? "#4fc3f7" : "#f48fb1")
            .attr("fill-opacity", 0.85)
            .merge(points)
            .transition()
            .duration(500)
            .attr("cx", d => xScale(d.longitude))
            .attr("cy", d => yScale(d.latitude));

        points.exit().remove();
    }

    // Title
    svg.append("text")
        .attr("class", "chart-title")
        .attr("x", width / 2)
        .attr("y", -margin.top / 2)
        .attr("text-anchor", "middle")
        .style("font-family", "Syne, sans-serif")
        .style("font-size", `${Math.max(width / 25, 13)}px`)
        .style("font-weight", "700")
        .text("Time travel");

    // X label
    svg.append("text")
        .attr("class", "axis-label")
        .attr("x", width / 2)
        .attr("y", height + margin.bottom - 9)
        .attr("text-anchor", "middle")
        .text("Longitude")
        .style("font-size", `${Math.max(width / 50, 9)}px`)
        .style("font-family", "DM Mono, monospace");

    // Y label
    svg.append("text")
        .attr("class", "axis-label")
        .attr("x", -height / 2)
        .attr("y", -margin.left + 16)
        .attr("text-anchor", "middle")
        .attr("transform", "rotate(-90)")
        .text("Latitude")
        .style("font-size", `${Math.max(height / 50, 9)}px`)
        .style("font-family", "DM Mono, monospace");

    // Time-slider
    d3.select("#time-slider")
        .on("input", function () {
            const year = +this.value;
            d3.select("#year-label").text(year);
            update(year); 
        });
    
        update(1999);

    // Redimensionnement
    window.addEventListener("resize", () => {
        createTimeTravelScatterPlot(originalData); 
        const year = +d3.select("#time-slider").node().value; 
        update(year); 
    });
}

