# 🛰️ Satellite Crop Classification - Wallonia, Belgium 2023

A complete satellite image classification pipeline that maps crop and land cover types across a ~40 × 31 km study area in Wallonia, Belgium. Built on Microsoft Azure over 4 days as part of the BeCode data training program.

## Project Overview

This project uses multi-temporal Sentinel-2 satellite imagery and a Random Forest classifier to predict crop types at 10-meter resolution. The model was trained on official Belgian government survey data (LPIS + WALOUS) and achieves 99.1% pixel-level accuracy on 110 crop and land cover classes.

## Study Area

| Parameter | Value |
|---|---|
| Region | Wallonia, Belgium |
| Bounding Box (WGS84) | [4.55, 50.25, 5.15, 50.55] |
| Projection | EPSG:32631 (WGS 84 / UTM zone 31N) |
| Area | ~40 × 31 km (~1,240 km²) |
| Pixel Size | 10 × 10 meters |
| Grid Size | 3,246 × 4,181 pixels |

## Data Sources

**Sentinel-2 L2A Imagery**
- 22 cloud-free scenes from February to October 2023
- 11 spectral bands (B02-B12 + SCL cloud mask)
- Accessed via the Copernicus STAC catalogue

**Training Data**
- LPIS (Land Parcel Identification System): 99 crop classes from official farmer declarations
- WALOUS (Wallonia Land Cover): 11 land cover classes from the 2018 land cover map
- Combined: 1,467 training polygons, 594,405 labeled pixels, 110 classes

## Pipeline

### Day 1: Setup & Data Access
- Azure infrastructure: ML workspace, Blob Storage, E4ds_v4 compute instance
- Copernicus authentication and STAC catalogue search
- Sentinel-2 data download to shared Blob Storage

### Day 2: Cloud Masking, Compositing & Feature Stack
- Cloud masking using the Scene Classification Layer (SCL)
- Monthly median composites for 9 months (Feb-Oct)
- Spectral indices: NDVI, NDWI, NDBI per month
- Feature stack assembly: 117 features (10 bands × 9 months + 3 indices × 9 months)

### Day 3: Classification
- Training data rasterization from LPIS + WALOUS shapefiles
- Feature importance ranking using Gini importance
- Top 60 features selected for training
- Random Forest classifier: 100 trees, OOB accuracy = 99.1%
- Full image prediction (13.5 million pixels)

### Day 4: Evaluation & Post-Processing
- Accuracy assessment: 99.1% overall accuracy on held-out test set
- Reclassification: 110 classes grouped into 15 broader categories
- Majority filter (3×3) to remove salt-and-pepper noise
- Visualization in QGIS and matplotlib

## Results

### Model Performance

| Metric | Value |
|---|---|
| Overall Accuracy (pixel-level) | 99.1% |
| OOB Score | 99.1% |
| Parcel-level Accuracy (spatial split) | 48.6% |
| Training Samples | 475,524 pixels |
| Test Samples | 118,881 pixels |
| Number of Classes | 110 (detailed) / 15 (reclassified) |

### Top Features
The most discriminating features were B05 (Red Edge) and B11/B12 (SWIR) bands, particularly from May 2023. May is the most important month because different crops are at distinct growth stages during spring in Wallonia.

### Reclassified Groups

| Code | Group | Source |
|---|---|---|
| 100 | Cereals | LPIS |
| 200 | Maize | LPIS |
| 300 | Grassland (LPIS) | LPIS |
| 400 | Potato | LPIS |
| 500 | Sugar Beet | LPIS |
| 600 | Rapeseed | LPIS |
| 700 | Legumes | LPIS |
| 800 | Other Crops | LPIS |
| 900 | Artificial Surfaces | WALOUS |
| 1000 | Bare Soil | WALOUS |
| 1100 | Water | WALOUS |
| 1200 | Rotating Grassland | WALOUS |
| 1300 | Permanent Grassland | WALOUS |
| 1400 | Coniferous Forest | WALOUS |
| 1500 | Broadleaved Forest | WALOUS |

### Known Limitations
- Pixel-level accuracy (99.1%) is inflated by spatial autocorrelation between neighboring pixels within the same field
- Parcel-level spatial validation (48.6%) provides a more honest estimate of generalization performance
- Narrow rivers (< 10m wide) are poorly detected due to sub-pixel width at 10m resolution
- WALOUS training data labels had no descriptive names and were identified using the WALOUS 2018 research paper
- Rare classes with very few training samples (< 10 pixels) have lower F1-scores

## Technology Stack

| Component | Technology |
|---|---|
| Cloud Platform | Microsoft Azure (ML Studio, Blob Storage) |
| Compute | Standard E4ds_v4 (4 cores, 32 GB RAM) |
| Language | Python 3.10 |
| Satellite Data | Sentinel-2 L2A via Copernicus STAC |
| Raster Processing | rasterio, numpy |
| Vector Processing | geopandas, shapely |
| Machine Learning | scikit-learn (Random Forest) |
| Visualization | matplotlib, QGIS |
| Version Control | Git / GitHub |
| Cost | < $8 per person over 4 days |

## Project Structure

```
crop-classification/
├── config.py                  # Azure and Copernicus credentials (not in repo)
├── student_workbook.ipynb     # Main notebook with all pipeline steps
├── download_s2.py             # Sentinel-2 download script
├── test_auth.py               # Copernicus authentication test
├── test_search.py             # STAC search verification
├── feature_names.json         # Ordered list of 117 feature names
├── feature_importance.png     # Feature importance chart
├── final_crop_map_v2.png      # Final map visualization
├── requirements.txt           # Python dependencies
├── .gitignore                 # Excludes config.py, .tif files, .venv
└── README.md                  # This file
```

## Azure Blob Storage Structure

```
sentinel2-data/
├── raw/                       # Raw Sentinel-2 scenes (shared, Cloud Lead downloaded)
│   └── T31UFS/
│       ├── 20230601_B04_10m.tif
│       └── ...
├── composites/                # Monthly median composites per band
│   ├── 202302_B02_10m.tif
│   ├── 202302_NDVI.tif
│   └── ...
└── results/                   # Classification outputs
    ├── classification_RF.tif              # 110-class prediction
    ├── reclassification_RF_v2.tif         # 15-class grouped prediction
    └── reclassification_RF_filtered.tif   # 15-class smoothed prediction
```

## Team Collaboration

The project used a shared Blob Storage architecture where one Cloud Lead downloaded the raw data and shared access credentials with teammates via a config file. Each team member used a personal prefix for their output files to avoid overwriting each other's work.

## Data Sources & References

- [Copernicus Data Space](https://dataspace.copernicus.eu) - Sentinel-2 satellite imagery
- [LPIS Wallonia (SIGEC)](https://geoportail.wallonie.be/catalogue/3f0f4112-2dac-4c04-a4d7-3e60fcbf158d.html) - Agricultural parcel declarations 2023
- [WALOUS Land Cover](https://geoportail.wallonie.be/catalogue/a0ad23a1-1845-4bd5-8c2f-0f62d3f1ec75.html) - Land cover map 2018
- Bassine et al. (2020). "First 1-M Resolution Land Cover Map Labeling the Overlap in the 3rd Dimension: The 2018 Map for Wallonia." *Data*, 5(4), 117.

## Setup

1. Create an Azure ML workspace with an E4ds_v4 compute instance
2. Create a Blob Storage container named `sentinel2-data`
3. Clone this repository
4. Create `config.py` with your Azure and Copernicus credentials
5. Install dependencies: `pip install -r requirements.txt`
6. Run `download_s2.py` to download Sentinel-2 data
7. Work through `student_workbook.ipynb` steps 1-20

## Author

**Kliti Hamataj** - BeCode Data Training Program, 2026

## License

This project uses open data from the European Space Agency (Copernicus) and the Wallonia Government (LPIS, WALOUS), both available under open access licenses.