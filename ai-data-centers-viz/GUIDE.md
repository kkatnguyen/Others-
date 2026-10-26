# Visualizing Epoch AI's Frontier AI Data Centers dataset

A step-by-step guide to building an interactive dashboard from
<https://epoch.ai/data/ai-data-centers> in **Power BI** (Part A) or **Tableau Public** (Part B, written for beginners).

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

## Part B: Tableau Public (free, Mac or Windows), for beginners

This part assumes you've never opened Tableau. Plan on about 2 hours for your
first time through.

### B0. Install and learn the screen (15 min)

1. Go to <https://public.tableau.com>, create a free account, and download
   **Tableau Public** (the desktop app). Install it and sign in.
2. Know before you start: Tableau Public **saves only to your online profile**,
   not to your computer, and anyone can see what you save. That's fine for
   Epoch's public data.

**The four words you need**

| Term | What it is |
|------|------------|
| **Data pane** | The list of your columns on the left side of a sheet. |
| **Columns / Rows shelves** | The two bars across the top. Drop a field on *Columns* to spread it left to right, or on *Rows* to stack it top to bottom. |
| **Marks card** | The box with *Color*, *Size*, *Label*, *Detail*, *Tooltip*. Drop a field on one of these to change how the marks look. |
| **Pill** | The colored capsule a field becomes when you drop it on a shelf. You can right-click a pill for options. |

**Blue vs. green pills:** Blue (*discrete*) means separate categories, like owner
names. Green (*continuous*) means a smooth range, like megawatts or a timeline.
If a chart looks wrong, check the pill color first.

**Dimensions vs. measures:** Text and category columns (Owner, Country) are
*dimensions*. Numbers (Power) are *measures*, which Tableau adds up
automatically (`SUM(...)`).

**Undo is your friend.** Ctrl+Z (Cmd+Z on Mac) undoes almost anything.

### B1. Load the data (10 min)

1. On the start screen, under **Connect → To a File**, click **Text file**. Pick
   the data centers CSV.
2. You're now on the **Data Source** page. It shows your columns and a preview
   of the rows.
3. **Check each column's type.** The small icon above each column name shows it:
   `Abc` = text, `#` = number, a calendar = date, a globe = location.
   - If a number column shows `Abc`, click the icon → **Number (decimal)**.
     If its values then turn into `null`, the cells contain text like `~500`.
     Fix those in Excel first, then reload the file.
   - Click the icon on `Latitude` → **Geographic Role → Latitude**. Do the same
     for `Longitude` (choose Longitude) and `Country` (choose
     Country/Region).
4. **Optional: the timeline file.** Drag it from the left side onto the canvas
   next to the first table. A line (a *relationship*) appears, and Tableau asks
   which fields match. Choose `Name` on both sides. This lets filters work
   across both files.
5. Click **Sheet 1** at the bottom-left to start building.

### B2. Make the headline numbers (15 min)

These are simple formulas called **calculated fields**.

1. Top menu: **Analysis → Create Calculated Field**.
2. Name it `Power (GW)`, type the formula below, and click **OK**:
   ```
   SUM([Power (MW)]) / 1000
   ```
   Tip: when you start typing `[`, Tableau suggests column names. Pick yours
   from the list so the spelling matches exactly.
3. Repeat for the other three:
   ```
   H100e (M)    →  SUM([H100e]) / 1000000
   Sites        →  COUNTD([Name])
   Capex ($B)   →  SUM([Capital cost (USD)]) / 1000000000
   ```
   (`COUNTD` means "count distinct": each site is counted once.)
4. **Build a number card:**
   - Rename the sheet: double-click the **Sheet 1** tab and type `KPI Power`.
   - Drag `Power (GW)` from the Data pane onto **Text** on the Marks card.
     A single number appears.
   - Click **Text** on the Marks card → the **…** button. In the editor, type
     `Total power (GW)` on a new line above the number, then make the number
     large (for example, 28 pt bold). Click **OK**.
   - To round it: right-click the pill → **Format** → Numbers → **Number (Custom)**
     → 1 decimal place.
5. **Make the other three cards:** right-click the `KPI Power` tab →
   **Duplicate**. On the copy, drag the old pill off the Marks card and drop in
   `H100e (M)`. Edit the label text. Repeat for `Sites` and `Capex ($B)`.

### B3. The map (15 min)

1. Click the **New Worksheet** icon (bottom bar, the small "+" sheet). Name the
   sheet `Map`.
2. In the Data pane, find **your** `Longitude` and double-click it. Then
   double-click **your** `Latitude`. A map appears.
   ⚠ Tableau also adds fields called `Latitude (generated)` and
   `Longitude (generated)` in italics. Don't use those. They place points by
   country name, not by your coordinates.
3. **Beginner trap: you'll see only one dot.** That's because Tableau averaged
   all the coordinates. Fix it by dragging `Name` onto **Detail** on the Marks
   card. Now there's one dot per data center.
4. Drag `Power (MW)` onto **Size**. Bigger dots now mean more power. Click
   **Size** and drag the slider to the right if the dots look too small.
5. Drag `Owner` onto **Color**. Then click **Color** and set opacity to about 70%
   so overlapping dots stay visible.
6. Drag `H100e` and `Status` onto **Tooltip**. Hover over a dot to check that the
   pop-up shows them.
7. For a cleaner background: top menu **Map → Background Maps → Light**.

*No coordinates in your file?* Double-click `Country` instead. Then use the
**Show Me** panel (top-right) → filled map.

### B4. Power by owner, as a bar chart (10 min)

1. New worksheet, named `By Owner`.
2. Drag `Owner` onto **Rows**. Drag `Power (GW)` onto **Columns**. Bars appear.
3. Click the **sort descending** button in the toolbar (bars with a down arrow) to
   put the biggest owner at the top.
4. Drag `Power (GW)` onto **Label** to show the number at the end of each bar.
5. To keep the colors consistent with the map: drag `Owner` onto **Color** too.
   For a calmer look, skip this and leave every bar the same color.

### B5. Growth over time (20 min)

This sheet needs the timeline file (or any date column).

1. New worksheet, named `Growth`.
2. Drag `Date` onto **Columns**. By default it shows as a blue pill reading
   `YEAR(Date)`. Right-click the pill and choose the **second** "Month" in the
   menu (the one that shows example dates like *May 2025*). The pill turns
   green, which means a continuous timeline.
3. Drag `Power (MW)` from the timeline file onto **Rows**.
4. Next, check what your timeline numbers mean. Open the file and look at one site:

   - **Each row is new MW added at that milestone** (the numbers don't
     repeat): right-click the `SUM(Power (MW))` pill → **Quick Table Calculation →
     Running Total**. The line now climbs as capacity adds up. Done.
   - **Each row is the site's total so far** (the number keeps growing for the
     same site): *don't* use Running Total, or you'll count the same megawatts
     many times. This case needs the data reshaped first, which is hard to do in
     Tableau. Send me the file and I'll convert it to the "MW added" format.
5. In the Marks card dropdown (it says *Automatic*), choose **Area**.
6. Optional "today" line: right-click the date axis → **Add Reference Line** →
   Value: *Constant*, pick today's date. Built capacity is to the left of the
   line and planned capacity to the right.

### B6. Detail table (10 min)

1. New worksheet, named `Table`.
2. Drag `Name`, `Owner`, `Country`, and `Status` onto **Rows**, one after another.
3. Double-click `Power (MW)`, `H100e`, and `Capital cost (USD)` in the Data pane.
   Tableau adds them as columns of numbers.
4. To sort by power: hover over the `Power (MW)` column header and click the
   small sort icon that appears.

### B7. Put it on a dashboard (25 min)

1. Click the **New Dashboard** icon on the bottom bar (the grid icon next to
   New Worksheet).
2. Left panel → **Size** → choose **Automatic** so it fits any screen.
3. **Title:** drag **Text** (under *Objects*, bottom-left) to the top. Type
   "Frontier AI Data Centers".
4. **Card row:** drag a **Horizontal** object under the title. Then drag the four
   KPI sheets into it, one beside the next. Tableau sizes them evenly.
5. **Middle row:** drag `Map` below the cards. Drag `By Owner` to the right edge
   of the map. A grey shaded area shows where it will land before you let go.
6. **Bottom row:** drag `Growth` under the map, and `Table` to the right of it.
7. **Filters:**
   - Click the map on the dashboard. Small icons appear on its border. Click
     the **▾ (More options)** arrow → **Filters** → tick `Owner`, `Country`,
     `Status`. Filter boxes appear on the right.
   - On each filter box: ▾ → **Apply to Worksheets → All Using This Data
     Source**, so one filter controls every chart.
   - ▾ → **Single Value (dropdown)** or **Multiple Values (dropdown)** saves space.
8. **Click-to-filter:** click the map, then click its **funnel icon** ("Use as
   Filter"). Do the same on `By Owner`. Now clicking a company's bar highlights
   only its sites everywhere. Press **Esc** or click an empty space to reset.
9. **Credit Epoch:** drag another **Text** object to the bottom. Type
   *"Source: Epoch AI, Frontier Data Centers (accessed <date>). CC BY."*

### B8. Save and share (5 min)

1. **File → Save to Tableau Public As…**, give it a name, and click **Save**.
   Your browser opens the published dashboard.
2. Copy the browser link to share it. On the web page, the **Share** button
   also gives you embed code.
3. To keep working later: in the app, **File → Open from Tableau Public**.

### If you get stuck

| What you see | What to do |
|--------------|------------|
| A field I need isn't in the Data pane | Check its name on the Data Source tab (bottom-left). It may be spelled differently. |
| Calculated field says "The calculation contains errors" | Click the red message: usually a column name typo or a missing `]`. |
| Chart shows one big bar or one dot | Something got added up that shouldn't be. Drag `Name` onto **Detail**. |
| Line chart shows only a few points | The date pill is blue. Right-click → the second "Month" option. |
| A sheet looks crushed on the dashboard | Click it → ▾ → **Fit → Entire View**. |
| Everything went wrong | Ctrl+Z, or right-click the sheet tab → **Clear Sheet** and start that sheet again. |

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
