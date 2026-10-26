# Visualizing Epoch AI's Frontier AI Data Centers dataset

A step-by-step guide to building an interactive dashboard from
<https://epoch.ai/data/ai-data-centers> in **Power BI** (Part A) or **Tableau** (Part B).

> **Field names:** Epoch updates this dataset regularly, and its column names
> can change. The names below (`Name`, `Owner`, `Power (MW)`, …) are
> placeholders. In Step 2, match each one to the real column in your download.

---

## The dashboard you'll build

| # | Visual | Question it answers |
|---|--------|---------------------|
| 1 | KPI cards: total power (MW/GW), total compute (H100-equivalents), number of sites, total capital cost | How big is frontier AI infrastructure? |
| 2 | Map: one bubble per data center, sized by power, colored by owner | Where are they? |
| 3 | Horizontal bar: power by owner (company) | Who controls the most capacity? |
| 4 | Line/area chart: capacity over time (cumulative) | How fast is it growing? |
| 5 | Detail table | What are the facts for each site? |
| — | Slicers/filters: Owner, Country, Status | Lets readers explore |

---

## Step 1: Download the data

1. Open <https://epoch.ai/data/ai-data-centers>.
2. Click **Download** (usually a CSV or a ZIP of CSVs). Unzip it into its own folder.
3. Open the files and see what you have. You'll usually find:
   - a **data centers** file with one row per site (name, owner, location, power,
     compute, cost, status), and
   - sometimes a **timeline** file with one row per site *per date*, showing how
     capacity grows as buildings come online.
4. Write down the license/citation text from the page. Epoch data is usually
   CC BY, so you have to credit them. You'll add this credit to the dashboard
   in the final step.

## Step 2: Map your columns

Fill in this table before you open either tool:

| Guide name | Meaning | Your column |
|------------|---------|-------------|
| `Name` | Data center / campus name | |
| `Owner` | Company that owns or operates it | |
| `Users` | Main AI lab tenant, if listed | |
| `Country` / `State` | Location text | |
| `Latitude`, `Longitude` | Coordinates (if not given, use Country/State for a filled map) | |
| `Power (MW)` | Facility power capacity | |
| `H100e` | Compute in H100-equivalents | |
| `Capital cost (USD)` | Estimated build cost | |
| `Status` | Operational / under construction / planned | |
| `Date` | Milestone or online date (timeline file) | |

**Clean-up checklist**
- Numbers saved as text, like `"1,200"` or `"~500"`: convert them to decimals.
- Blank cells: leave them blank, not 0, so averages stay correct.
- If the timeline file reports *cumulative* capacity per site, take the
  **latest value per site per date**. Don't add up every row, or you'll
  double-count.

---

## Part A: Power BI Desktop (free, Windows)

### A1. Load and clean
1. **Home → Get data → Text/CSV** → select the data centers file → **Transform Data**.
2. In Power Query:
   - Right-click each numeric column → **Change Type → Decimal Number**.
   - Set `Latitude`/`Longitude` to Decimal Number. Then, in the Data pane, set
     **Column tools → Data category** to *Latitude* / *Longitude*.
   - Set `Country` to Data category **Country/Region**.
   - Rename the query to `DataCenters`.
3. If you have the timeline file, load it the same way, name it `Timeline`, and set
   `Date` to type **Date**.
4. **Close & Apply**.

### A2. Relationships (only if you have the timeline file)
**Model view** → drag `DataCenters[Name]` onto `Timeline[Name]`
(one-to-many, single direction).

### A3. Measures
**Home → New measure**, one at a time:

```DAX
Total Power (GW) = DIVIDE ( SUM ( DataCenters[Power (MW)] ), 1000 )

Total H100e (M) = DIVIDE ( SUM ( DataCenters[H100e] ), 1000000 )

Sites = DISTINCTCOUNT ( DataCenters[Name] )

Total Capex ($B) = DIVIDE ( SUM ( DataCenters[Capital cost (USD)] ), 1e9 )

Share of Power =
DIVIDE (
    SUM ( DataCenters[Power (MW)] ),
    CALCULATE ( SUM ( DataCenters[Power (MW)] ), ALLSELECTED ( DataCenters ) )
)
```

Cumulative capacity over time, using the timeline file. This takes each site's
latest reported value on or before each date and adds those values up:

```DAX
Capacity to Date (GW) =
VAR d = MAX ( Timeline[Date] )
RETURN
    DIVIDE (
        SUMX (
            VALUES ( DataCenters[Name] ),
            VAR lastDate =
                CALCULATE ( MAX ( Timeline[Date] ), Timeline[Date] <= d, REMOVEFILTERS ( Timeline[Date] ) )
            RETURN
                CALCULATE ( SUM ( Timeline[Power (MW)] ), Timeline[Date] = lastDate, REMOVEFILTERS ( Timeline[Date] ) )
        ),
        1000
    )
```

If your timeline lists *added* MW per milestone instead of a running total, use this:
`Capacity to Date (GW) = DIVIDE( CALCULATE( SUM(Timeline[Power (MW)]), Timeline[Date] <= MAX(Timeline[Date]), REMOVEFILTERS(Timeline[Date]) ), 1000 )`

### A4. Build the visuals
1. **KPI cards**: add 4 **Card** visuals, one each for `Total Power (GW)`,
   `Total H100e (M)`, `Sites`, and `Total Capex ($B)`. In Format, set display
   units to *None* and decimals to 1.
2. **Map**: add a **Map** (or **Azure Map**) visual.
   - Latitude → `Latitude`, Longitude → `Longitude`, Bubble size → `Power (MW)`,
     Legend → `Owner`, Tooltips → `Name`, `H100e`, `Status`.
   - No coordinates? Use **Filled map** with Location → `Country` instead.
3. **Bar chart**: add a **Clustered bar chart**.
   - Y-axis → `Owner`, X-axis → `Total Power (GW)`. Sort by the measure, descending.
   - Turn on data labels. For a cleaner chart, give all bars one color instead of
     one per owner.
4. **Growth chart**: add a **Line chart** (or Area).
   - X-axis → `Timeline[Date]` (switch from the date hierarchy to plain *Date*),
     Y-axis → `Capacity to Date (GW)`.
   - Optional: add a **constant line** at today's date (Analytics pane) to separate
     built capacity from planned capacity.
5. **Table**: add a **Table** with `Name`, `Owner`, `Country`, `Status`, `Power (MW)`,
   `H100e`, and `Capital cost (USD)`. Add a data-bar conditional format on `Power (MW)`.
6. **Slicers**: add three **Slicer** visuals for `Owner`, `Country`, and `Status`.
   Use the *Dropdown* style to save space.

### A5. Layout and polish
- Canvas: **View → Page view → Fit to page**, 16:9.
- Top row: title text box ("Frontier AI Data Centers"), then the 4 KPI cards.
- Middle row: the map (about 60% of the width) next to the bar chart (about 40%).
- Bottom row: the growth chart next to the table. Put the slicers in a slim column
  on the left.
- Give every owner the same color in every visual: **Format → Data colors**.
- Add a footer text box: *"Source: Epoch AI, Frontier Data Centers (accessed <date>). CC BY."*
- **File → Publish → Publish to Power BI** to share it, or export it as PDF.

---

## Part B: Tableau (Public is free; Desktop also works)

### B1. Connect and clean
1. **Connect → To a File → Text file** → choose the data centers CSV.
2. On the Data Source page, click the type icon above each numeric column → **Number (decimal)**.
   Set `Latitude` and `Longitude` to **Geographic Role → Latitude/Longitude**, and `Country` to
   **Geographic Role → Country/Region**.
3. Timeline file: drag it onto the canvas next to the first table, and create a
   **relationship** on `Name` = `Name`.

### B2. Calculated fields
**Analysis → Create Calculated Field**:

```
// Power (GW)
SUM([Power (MW)]) / 1000

// H100e (M)
SUM([H100e]) / 1000000

// Sites
COUNTD([Name])

// Capex ($B)
SUM([Capital cost (USD)]) / 1e9

// Share of Power  (table calc)
SUM([Power (MW)]) / TOTAL(SUM([Power (MW)]))
```

Cumulative capacity, if your timeline holds **added MW per milestone**: put
`SUM([Power (MW)])` on Rows, then right-click → **Quick Table Calculation → Running Total**
(compute using `Date`).
If it holds a **running total per site**, use this calculated field instead:

```
// Latest MW per site (LOD)
{ FIXED [Name], [Date] : MAX([Power (MW)]) }
```

Then sum it across sites with Running Total turned **off**, and fill in any missing
dates with *Show Missing Values* plus a `LOOKUP`/`PREVIOUS_VALUE` calculation,
or reshape the data beforehand.

### B3. Build one sheet per visual
1. **KPI sheet** (one sheet per KPI): drag the calculated field to **Text** on the Marks card,
   enlarge the font, and add a label such as "Total power (GW)".
2. **Map sheet**: double-click `Longitude`, then `Latitude`. Then drag:
   `Power (MW)` → **Size**, `Owner` → **Color**, `Name` and `H100e` → **Tooltip**.
   Set mark type to **Circle** and opacity to about 70%. Use the Map → Background Maps → *Light* style.
3. **Bar sheet**: `Owner` → Rows, `Power (GW)` → Columns. Sort descending with the toolbar
   button. Add labels with Marks → Label.
4. **Growth sheet**: `Date` (continuous, **Month**) → Columns, cumulative capacity → Rows,
   mark type **Area**. Add a reference line at TODAY() if you want.
5. **Table sheet**: `Name`, `Owner`, `Country`, `Status` → Rows; `Measure Values` → Text,
   filtered to Power, H100e, and Capex.

### B4. Assemble the dashboard
1. **New Dashboard**, Size → *Automatic* (or 1366 × 768).
2. Drag in sheets in this order: title, KPI row (a Horizontal container), map + bar,
   then growth chart + table.
3. Filters: on the map, open the sheet menu → **Filters → Owner / Country / Status** →
   **Apply to Worksheets → All Using This Data Source**.
4. Interactivity: **Dashboard → Actions → Add Action → Filter**. Source = Map and Bar,
   Target = all sheets, Run on = *Select*. Clicking an owner or site then filters
   everything else.
5. Use one owner color palette everywhere: right-click `Owner` → Default Properties → Color.
6. Add a footer text object with the Epoch AI citation.
7. **File → Save to Tableau Public** (Public) or **Server → Publish**.

---

## Insights to look for and annotate
- **Concentration**: what share of total power do the top 3 owners hold? Use `Share of Power`.
- **Scale**: how many of the sites are 1 GW or more? Add a filter `Power (MW) >= 1000`.
- **Cost per MW**: create `Capital cost (USD) / Power (MW)` and find which sites are outliers.
- **Compute per MW**: `H100e / Power (MW)` shows how efficient newer sites are.
- **Built vs. planned**: compare the growth curve before and after today.

## Common pitfalls
| Symptom | Fix |
|---------|-----|
| Map shows no points | Lat/Long are text or lack a geographic role. Retype them. |
| Totals look too big | The timeline rows were summed across dates. Use the latest-value logic. |
| Line chart drops to 0 | Dates are missing for some sites. Carry the last value forward. |
| Numbers show as "1.2E+3" | Set a number format (Power BI: Format pane; Tableau: Format → Numbers). |
