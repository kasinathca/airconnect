# AirConnect India
### A small, offline MLDS laboratory project

**Status:** Working academic prototype • **Version:** 1.0.0 • **Date:** 19 October 2026

## Open the website (Windows)

1. Unzip the whole folder. **Do not extract only the HTML file.**
2. Double-click `START_AIRCONNECT.bat`, or open `site/index.html` in Chrome, Edge or Firefox.
3. Use **Overview**, **Airport explorer**, **Machine learning**, and **Methodology** in the navigation.

There is **no server, login, API key, npm, cloud account or Jupyter installation** needed to view the site. The charts and fitted model results are pre-generated and work offline.

## Re-run the machine learning (optional)

Install Python 3.10+ and the dependencies shown in `requirements.txt`:

```powershell
cd AirConnect-India
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python src/build.py
python -m pytest -q
```

If you prefer Command Prompt, use `.venv\Scripts\activate.bat` instead. `src/build.py` consumes bundled verified DGCA-derived data and overwrites `site/assets/data.js` with newly trained results. **You do not need network connectivity** to train it.

If you want to run on an HTTP URL rather than opening the HTML file, execute:

```powershell
python -m http.server 8080 --directory site
```

Then open <http://localhost:8080>.

## What is included

| Folder | Purpose |
|---|---|
| `site/` | Static interactive website, no build tools |
| `data/raw/` | DGCA-derived airport-year data (2022–2025), official national totals (2016–2025), geographic coordinates |
| `data/processed/` | Airport-level feature table and JSON model output |
| `src/` | Data transcription, preprocessing, reproducible ML training |
| `tests/` | Structural and data/ML validation tests |
| `docs/` | Requirements, design, methodology, syllabus mapping, report and slide materials |

## Research question

How have Indian airport passenger movements evolved, how do annual airport traffic patterns differ, and can a small ML model predict annual domestic traffic more accurately than a simple baseline?

### Models

- **K-Means (k=3):** 2025 airport grouping based on scaled log domestic and international passenger movements. Silhouette Score **0.6235** on 129 airports.
- **Random Forest regression:** annual year-ahead domestic traffic prediction with lag-one and lag-two features. Trained on 106 airport observations for 2024, tested on 116 held-out 2025 observations.
- **Prior-year baseline:** predicts that 2025 traffic equals 2024 traffic; the baseline **outperformed Random Forest on test MAE and RMSE**. The project explicitly reports this negative ML result.

### Definitions

- Passenger movements = passengers arriving **plus** departing, not unique travellers.
- Reporting airports in the DGCA data are not identical to government counts of operational airports, heliports and water aerodromes.
- Low recorded traffic does not itself prove capacity underutilisation.
- A zero recorded international passenger count does not establish an international route restriction.

## Sources and attribution

1. Kubicek, M. (2026). *India Aviation Stats*, cleaned DGCA passenger traffic. MIT licence. https://github.com/mkubicek/india-aviation-stats
2. Ministry of Civil Aviation, Government of India. Operational airport listing (165 as of 7 July 2026). https://www.civilaviation.gov.in/index.php/node/4628
3. Ministry of Civil Aviation. Airport expansion from 74 in 2014. https://www.civilaviation.gov.in/node/7425
4. Brandon Himpfen, *Airports Dataset*: code and coordinates, MIT. https://github.com/brandonhimpfen/airports
5. Natural Earth (public domain), low-resolution India geographic outline. https://www.naturalearthdata.com/

The distributed data include a **four-year full airport-level subset** (2022–2025), while the national series spans 2016–2025. The website does not claim to reproduce the attached visualized.in hexagonal proximity study; that would require a separate historical network-distance dataset.

## Scope choices

The software intentionally uses only four website sections, two ML techniques, and no authentication, web backend, dynamic map tiles, flight route policy inference or aircraft/seat capacity model. This is designed for a short course laboratory project, not production aviation planning.

## Local validation

`pytest` exercises source data consistency, reproducibility, regression split integrity, metric consistency and web asset presence. The website was additionally exercised using a headless Chromium browser at desktop and mobile widths, including filter changes and CSV-related code checks.

## Team and academic report

Use the editable placeholders in `docs/PROJECT_REPORT.md` and the accompanying presentation before submission. Do not submit with placeholder team/member fields.
