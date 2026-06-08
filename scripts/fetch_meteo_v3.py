"""
fetch_meteo_v3.py
Scarica previsioni Open-Meteo per le 83 stazioni Magic Pass.
Produce un GeoJSON per ogni timestep (ogni 6h per 5 giorni = 20 file).

Uso: python3 scripts/fetch_meteo_v3.py
Output: data/weather_YYYYMMDDHH00.geojson + data/index.json
"""

import urllib.request
import json
import os
from datetime import datetime, timezone

OUTPUT_DIR = "data"

MAGIC_PASS_STATIONS = {
    "Aeschiallmend":           {"lat": 46.647366, "lon": 7.732993},
    "Anzère":                  {"lat": 46.295128, "lon": 7.394955},
    "Axalp":                   {"lat": 46.738341, "lon": 8.059329},
    "Balmberg":                {"lat": 47.265914, "lon": 7.543444},
    "Belalp":                  {"lat": 46.371792, "lon": 7.975012},
    "Bugnenets-Savagnières":   {"lat": 47.126057, "lon": 7.018470},
    "Bumbach":                 {"lat": 46.807377, "lon": 7.888115},
    "Charmey":                 {"lat": 46.622372, "lon": 7.188038},
    "Crêt-du-Puy":             {"lat": 47.090527, "lon": 6.993179},
    "Eischoll":                {"lat": 46.289505, "lon": 7.776881},
    "Eriz":                    {"lat": 46.803519, "lon": 7.910718},
    "Arolla":                  {"lat": 46.020262, "lon": 7.473954},
    "Evolène":                 {"lat": 46.121571, "lon": 7.477226},
    "La Forclaz":              {"lat": 46.086246, "lon": 7.523221},
    "Faltschen":               {"lat": 46.628002, "lon": 7.724980},
    "Gantrisch Gurnigel":      {"lat": 46.724655, "lon": 7.454506},
    "Glacier 3000":            {"lat": 46.353821, "lon": 7.205612},
    "Gpson":                   {"lat": 46.225312, "lon": 7.902122},
    "Grenchenberg":            {"lat": 47.221455, "lon": 7.380616},
    "Grimentz-Zinal":          {"lat": 46.163437, "lon": 7.584548},
    "Gstaad":                  {"lat": 46.465485, "lon": 7.273952},
    "Rougemont":               {"lat": 46.472771, "lon": 7.206613},
    "Saanenmöser":             {"lat": 46.506207, "lon": 7.323383},
    "Schönried":               {"lat": 46.507072, "lon": 7.274805},
    "St-Stephan":              {"lat": 46.511063, "lon": 7.382613},
    "Zweisimmen":              {"lat": 46.550652, "lon": 7.373709},
    "Grimmialp":               {"lat": 46.568069, "lon": 7.484264},
    "Gurnigelbad":             {"lat": 46.757008, "lon": 7.449590},
    "Habkern":                 {"lat": 46.731907, "lon": 7.854006},
    "Heimenschwand":           {"lat": 46.827389, "lon": 7.677143},
    "Hohwald":                 {"lat": 46.709320, "lon": 7.821546},
    "Homberg":                 {"lat": 46.767752, "lon": 7.677712},
    "Jaun":                    {"lat": 46.608944, "lon": 7.290691},
    "Jaunpass":                {"lat": 46.595580, "lon": 7.338010},
    "Jeizinen":                {"lat": 46.331917, "lon": 7.722714},
    "Kiental":                 {"lat": 46.582592, "lon": 7.715937},
    "La Berra":                {"lat": 46.682167, "lon": 7.166771},
    "La Lécherette":           {"lat": 46.416975, "lon": 7.119769},
    "Lauchernalp":             {"lat": 46.406406, "lon": 7.776004},
    "Le Brassus":              {"lat": 46.576439, "lon": 6.213542},
    "Les Diablerets":          {"lat": 46.341095, "lon": 7.147033},
    "Les Marécottes":          {"lat": 46.111336, "lon": 7.006306},
    "Les Mayens de Conthey":   {"lat": 46.256624, "lon": 7.284725},
    "Les Mosses":              {"lat": 46.391678, "lon": 7.071578},
    "Les Paccots":             {"lat": 46.514724, "lon": 6.936362},
    "Les Pléiades":            {"lat": 46.488899, "lon": 6.916388},
    "Les Rasses":              {"lat": 46.834576, "lon": 6.534253},
    "Les Rochers de Naye":     {"lat": 46.432796, "lon": 6.979251},
    "Leukerbad":               {"lat": 46.371437, "lon": 7.638759},
    "Leysin":                  {"lat": 46.353519, "lon": 7.010152},
    "Linden":                  {"lat": 46.843925, "lon": 7.678084},
    "Marbachegg":              {"lat": 46.834702, "lon": 7.911718},
    "Meiringen-Hasliberg":     {"lat": 46.730618, "lon": 8.200658},
    "Melchsee-Frutt":          {"lat": 46.776344, "lon": 8.270116},
    "Moléson":                 {"lat": 46.561966, "lon": 7.034523},
    "Moosalp":                 {"lat": 46.248253, "lon": 7.829611},
    "Mörlialp":                {"lat": 46.822742, "lon": 8.108218},
    "Nax":                     {"lat": 46.225464, "lon": 7.462543},
    "Niederhorn":              {"lat": 46.710602, "lon": 7.775802},
    "Ottenleue":               {"lat": 46.735054, "lon": 7.364665},
    "Ovronnaz":                {"lat": 46.204193, "lon": 7.151211},
    "Rathvel":                 {"lat": 46.544109, "lon": 6.975307},
    "Robella - Val de Travers":{"lat": 46.881100, "lon": 6.550070},
    "Rossberg":                {"lat": 46.627453, "lon": 7.433806},
    "Rosswald":                {"lat": 46.304493, "lon": 8.041525},
    "Rüschegg":                {"lat": 46.750965, "lon": 7.425229},
    "Saas-Almagell":           {"lat": 46.089706, "lon": 7.963252},
    "Saas Fee":                {"lat": 46.099144, "lon": 7.925277},
    "Saignelégier":            {"lat": 47.255810, "lon": 6.995653},
    "Schwanden":               {"lat": 46.736632, "lon": 7.729452},
    "Schwarzsee":              {"lat": 46.664074, "lon": 7.290966},
    "Selital":                 {"lat": 46.744904, "lon": 7.392882},
    "Sörenberg":               {"lat": 46.814800, "lon": 8.030524},
    "Springenboden":           {"lat": 46.616902, "lon": 7.576687},
    "St Cergue":               {"lat": 46.442966, "lon": 6.087220},
    "St-Luc / Chandolin":      {"lat": 46.248325, "lon": 7.604917},
    "Tramelan":                {"lat": 47.214433, "lon": 7.083587},
    "Unterbäch":               {"lat": 46.279270, "lon": 7.799555},
    "Vercorin":                {"lat": 46.246895, "lon": 7.532484},
    "Villars-Gryon":           {"lat": 46.299984, "lon": 7.090662},
    "Visperterminen":          {"lat": 46.256939, "lon": 7.913731},
    "Wilerallmi":              {"lat": 46.726089, "lon": 7.745841},
    "Wiriehorn":               {"lat": 46.612373, "lon": 7.532542},
}

OPEN_METEO_PARAMS = [
    "temperature_2m",
    "windspeed_10m",
    "windgusts_10m",
    "precipitation",
    "precipitation_probability",
    "snowfall",
    "weathercode",
    "freezinglevel_height",
    "cloudcover",
    "sunshine_duration",
]

HOUR_STEP     = 6
FORECAST_DAYS = 5


def fetch_station(name, lat, lon):
    params = ",".join(OPEN_METEO_PARAMS)
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&hourly={params}"
        f"&forecast_days={FORECAST_DAYS}"
        f"&models=icon_seamless"
        f"&timezone=Europe%2FZurich"
    )
    try:
        r = urllib.request.urlopen(url, timeout=15)
        return json.loads(r.read().decode('utf-8'))
    except Exception as e:
        print(f"  ⚠️  {name}: {e}")
        return None


def main():
    print("=" * 60)
    print("Magic Pass Weather Fetcher — Open-Meteo")
    print(f"Configurazione: ogni {HOUR_STEP}h per {FORECAST_DAYS} giorni")
    print("=" * 60)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 1. Scarica i dati per tutte le stazioni
    print(f"\n📥 Scarico previsioni per {len(MAGIC_PASS_STATIONS)} stazioni...")
    all_station_data = {}

    for i, (name, info) in enumerate(MAGIC_PASS_STATIONS.items()):
        data = fetch_station(name, info['lat'], info['lon'])
        if data:
            all_station_data[name] = data
            print(f"  [{i+1:02d}/{len(MAGIC_PASS_STATIONS)}] ✅ {name}")
        else:
            print(f"  [{i+1:02d}/{len(MAGIC_PASS_STATIONS)}] ⚠️  {name} — saltata")

    # 2. Costruisci i timestep ogni HOUR_STEP ore
    first = next(iter(all_station_data.values()))
    all_times = first['hourly']['time']
    timestep_indices = list(range(0, len(all_times), HOUR_STEP))

    print(f"\n🗺️  Costruisco {len(timestep_indices)} GeoJSON...")

    index = []
    for idx in timestep_indices:
        time_iso = all_times[idx]
        hour_str = time_iso.replace("-", "").replace("T", "").replace(":", "")

        features = []
        for name, info in MAGIC_PASS_STATIONS.items():
            if name not in all_station_data:
                continue
            h = all_station_data[name]['hourly']
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [info['lon'], info['lat']]
                },
                "properties": {
                    "name":              name,
                    "lat":               info['lat'],
                    "lon":               info['lon'],
                    "forecast_time_iso": time_iso,
                    "forecast_time_str": hour_str,
                    "temp_c":            h['temperature_2m'][idx],
                    "wind_kmh":          h['windspeed_10m'][idx],
                    "gust_kmh":          h['windgusts_10m'][idx],
                    "precip_mm":         h['precipitation'][idx],
                    "precip_prob_pct":   h['precipitation_probability'][idx],
                    "snowfall_cm":       h['snowfall'][idx],
                    "weathercode":       h['weathercode'][idx],
                    "zero_level_m":      h['freezinglevel_height'][idx],
                    "cloudcover_pct":    h['cloudcover'][idx],
                    "sunshine_min":      h['sunshine_duration'][idx],
                }
            })

        geojson = {
            "type": "FeatureCollection",
            "metadata": {
                "source":            "Open-Meteo — ICON Seamless",
                "forecast_time_iso": time_iso,
                "forecast_time_str": hour_str,
                "updated_utc":       datetime.now(timezone.utc).isoformat(),
                "total_stations":    len(features),
            },
            "features": features
        }

        filename = f"weather_{hour_str}.geojson"
        filepath = os.path.join(OUTPUT_DIR, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(geojson, f, ensure_ascii=False, separators=(',', ':'))

        index.append({
            "file":              filename,
            "forecast_time_iso": time_iso,
            "forecast_time_str": hour_str,
        })
        print(f"  ✅ {filename} ({len(features)} stazioni)")

    # 3. Salva index.json
    index_path = os.path.join(OUTPUT_DIR, "index.json")
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump({
            "updated_utc": datetime.now(timezone.utc).isoformat(),
            "hour_step":   HOUR_STEP,
            "timesteps":   index,
        }, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Completato: {len(index)} GeoJSON in '{OUTPUT_DIR}/'")
    print(f"✅ Index: {index_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
