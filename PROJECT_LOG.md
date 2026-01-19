# Building Estimator - Project Log

## Project Overview
A desktop application (with future Android support) that estimates construction costs and materials for new buildings using photo analysis, user-provided dimensions, and building codes.

## Tech Stack
- **Framework**: Flet (Python) - cross-platform desktop/mobile
- **Photo AI**: OpenAI Vision API (GPT-4 Vision)
- **Data Storage**: SQLite for local data, JSON for defaults
- **Location**: `D:\work\building_estimator`

## Project Structure
```
building_estimator/
├── main.py                 # Flet app entry point
├── requirements.txt
├── config/
│   └── settings.py         # API keys, app configuration
├── core/
│   ├── photo_analyzer.py   # OpenAI Vision integration
│   ├── estimator.py        # Main estimation engine
│   └── accuracy.py         # Confidence/accuracy calculator
├── data/
│   ├── building_codes.json # Default IRC/IBC codes
│   ├── materials.json      # Material catalog with default prices
│   └── labor_rates.json    # Default labor rates by trade
├── database/
│   ├── db.py               # SQLite connection
│   └── models.py           # User overrides, saved estimates
├── ui/
│   ├── views/
│   │   ├── home.py         # Main dashboard
│   │   ├── photo_input.py  # Photo upload/capture
│   │   ├── dimensions.py   # Dimension input form
│   │   ├── codes.py        # Building code settings
│   │   ├── estimate.py     # Results display
│   │   └── settings.py     # User preferences/pricing
│   └── components/
│       ├── photo_preview.py
│       ├── dimension_form.py
│       └── estimate_card.py
└── utils/
    └── calculations.py     # Area, volume, quantity formulas
```

---

## Implementation Status

### COMPLETED FILES
| File | Description | Status |
|------|-------------|--------|
| `requirements.txt` | Dependencies (flet, openai, Pillow) | Done |
| `config/__init__.py` | Package init | Done |
| `config/settings.py` | App configuration, API keys, constants | Done |
| `core/__init__.py` | Package init | Done |
| `core/photo_analyzer.py` | OpenAI Vision API integration | Done |
| `utils/__init__.py` | Package init | Done |
| `utils/calculations.py` | All calculation functions (area, lumber, insulation, etc.) | Done |
| `main.py` | Flet app entry point (1200x800, async, FilePicker) | Done |
| `ui/__init__.py` | Package init | Done |
| `ui/app_state.py` | Centralized state management (image paths, callbacks) | Done |
| `ui/components/__init__.py` | Package init | Done |
| `ui/components/image_thumbnail.py` | 150x150 thumbnail with X remove button overlay | Done |
| `ui/components/image_gallery.py` | GridView of thumbnails (5 columns, responsive) | Done |
| `ui/views/__init__.py` | Package init | Done |
| `ui/views/photo_input.py` | Photo upload UI with gallery and action buttons | Done |

### REMAINING FILES TO CREATE
| Priority | File | Description |
|----------|------|-------------|
| 1 | `data/materials.json` | Material catalog with default prices |
| 2 | `data/building_codes.json` | IRC/IBC code requirements by climate zone |
| 3 | `data/labor_rates.json` | Labor rates by trade |
| 4 | `core/estimator.py` | Main estimation engine combining all inputs |
| 5 | `core/accuracy.py` | Confidence/accuracy scoring |
| 6 | `database/__init__.py` | Package init |
| 7 | `database/db.py` | SQLite connection management |
| 8 | `database/models.py` | Data models for estimates, user overrides |
| 9 | `ui/components/photo_preview.py` | Photo preview component |
| 10 | `ui/components/dimension_form.py` | Dimension input form component |
| 11 | `ui/components/estimate_card.py` | Estimate display card component |
| 12 | `ui/views/home.py` | Main dashboard view |
| 13 | `ui/views/dimensions.py` | Dimension input view |
| 14 | `ui/views/codes.py` | Building code settings view |
| 15 | `ui/views/estimate.py` | Results display view |
| 16 | `ui/views/settings.py` | User preferences view

---

## Key Features to Implement

### Photo Analyzer (DONE)
- Extracts building type, roof style, exterior material
- Counts windows, doors, garage doors
- Detects special features (porch, deck, dormers)
- Returns confidence score

### Estimation Engine (TODO)
- Combines photo analysis + dimensions + codes
- Calculates material quantities for all trades
- Applies material prices and labor rates
- Adds contingency and permit costs

### Accuracy Calculator (TODO)
- Scores confidence based on data quality
- Factors: photo quality, measured vs estimated dimensions, local vs default pricing

### User Flow
1. Upload Photos → AI Analysis
2. Enter Dimensions → Footprint, height, stories
3. Select Location → Climate zone, local codes
4. Review/Adjust → Override detected features
5. Generate Estimate → Materials + costs
6. View Results → Itemized breakdown with accuracy

---

## Running the App
```bash
cd D:\work\building_estimator
pip install -r requirements.txt
python main.py
# or: flet run main.py
```

## Environment Variables
- `OPENAI_API_KEY` - Required for photo analysis

---

## Last Updated
2026-01-19 - Completed UI for image upload and viewing

## Session Notes

### Flet 0.80.2 API Changes
The following adjustments were needed for compatibility with Flet 0.80.2:
| Old API | New API |
|---------|---------|
| `page.overlay.append(file_picker)` | `page.services.append(file_picker)` |
| `ft.ImageFit.COVER` | `ft.BoxFit.COVER` |
| `ft.alignment.center` | `ft.Alignment(0, 0)` |
| `ft.ElevatedButton` | `ft.Button` |
| `FilePicker(on_result=callback)` | `await file_picker.pick_files()` (async, returns files) |

## Next Steps
1. Create `data/materials.json` - Material catalog with prices
2. Create `data/building_codes.json` - Code requirements
3. Create `data/labor_rates.json` - Labor rates
4. Create `core/estimator.py` - Main calculation engine
5. Create `core/accuracy.py` - Confidence scoring
6. Create database layer
7. Wire up "Analyze Photos" button to `core/photo_analyzer.py`
8. Create remaining UI views (dimensions, codes, estimate, settings)
9. Add navigation between views
