# MagicMeteo: source data

Reference/source data used to build the MagicMeteo station list. These files are
not needed to run or deploy the app (the app reads the pre-generated GeoJSON under
`static/magicmeteo/data/`, produced by `scripts/fetch_meteo_v3.py`); they are kept
here for archival.

- `Stazioni_MP/`: Magic Pass resort station list (curated CSV / spreadsheet / PDF).
- `Stazioni_MS/`: MeteoSwiss station references (CSV + GeoJSON).

The swissTLMRegio boundary layers (`swissTLMRegio_*_LV95.gpkg`, ~420 MB) are public
swisstopo data, too large for git. They are not stored here; re-download from
swisstopo if needed: https://www.swisstopo.admin.ch/en/landscape-model-swisstlmregio
