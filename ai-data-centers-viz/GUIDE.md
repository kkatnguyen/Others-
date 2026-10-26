# Visualizing Epoch AI's Frontier AI Data Centers dataset

A step-by-step guide to building an interactive dashboard from
<https://epoch.ai/data/ai-data-centers> in **Power BI** (Part A) or **Tableau Public** (Part B, written for beginners).

> **The data is ready.** The `data/` folder has two cleaned files built from
> the Epoch download, and every field name in this guide matches them exactly.
> Step 1 explains what's in them and what was changed.

---

## The dashboard you'll build

| # | Visual | Question it answers |
|---|--------|---------------------|
| 1 | KPI cards: total power (GW), total compute (H100-equivalents), number of sites, total capital cost | How big is frontier AI infrastructure? |
| 2 | Map: one bubble per data center, sized by power, colored by owner | Where are they? |
| 3 | Horizontal bar: power by owner (company) | Who controls the most capacity? |
| 4 | Area chart: total power by month, to date and planned | How fast is it growing? |
| 5 | Detail table | What are the facts for each site? |
| — | Filters: Owner, Country, Status | Lets readers explore |

**Check your numbers against these.** With the files in `data/`, your dashboard
should show:

| KPI | Expected value |
|-----|----------------|
| Sites | 95 (74 operating, 21 not yet operating) |
| Facility power | 18.2 GW |
| H100 equivalents | 14.8 million |
| Capital cost | $539 billion |
| Planned facility power, January 2030 (growth chart, far right) | 49.9 GW |

---

## Team plan (Tableau, 5 people)

Everyone builds their own pieces in their own Tableau Public workbook, and
Kalven combines them at the end. Tableau Public doesn't support several people
editing one workbook at the same time, so this avoids conflicts.

| Who | Role | Owns | Guide steps | Also |
|-----|------|------|-------------|------|
| **Kathy** | Data lead | Shares the two cleaned files, the 4 calculated fields, the expected numbers | Step 1, B1, B2 (formulas only) | Checks every dashboard number against the table above before publishing |
| **Anthony** | Cards and table | 4 headline number cards and the detail table | B2, B6 | Writes the label and tooltip wording |
| **Mark** | Map | The map | B3 | Picks the owner color list everyone uses |
| **Benjamin** | Charts | Bar chart and growth chart | B4, B5 | Checks that the growth chart reads 18.2 GW at October 2026 |
| **Kalven** | Dashboard lead | Layout, filters, title, citation, publishing | B7, B8 | Early on, sketches the layout and drafts the "Insights" text |

### Order of work

1. **Kathy goes first (about 15 min).** The files are already cleaned, so this
   step is quick. Meanwhile, everyone else installs Tableau Public and reads B0.
   Kathy then posts these in the shared folder:
   - `data_centers_clean.csv` and `capacity_by_month.csv`,
   - the four formulas from B2 as text (copy-paste them exactly),
   - the "Check your numbers" table above.
2. **Anthony, Mark, and Benjamin build in parallel (about 1 hour).** Each starts
   from Kathy's files and names sheets exactly as in the guide (`KPI Power`,
   `Map`, `By Owner`, `Growth`, `Table`, …). During this time, Kalven sketches
   the layout and drafts the insights text, and Kathy helps whoever is stuck.
3. **Merge (about 45 min).** Each builder right-clicks their sheet tab →
   **Copy** and sends it to Kalven, who pastes it into the main workbook. Pasting
   only works when everyone used the same files and the same calculated-field
   names. Test it with one sheet early. If pasting doesn't work, Kalven rebuilds
   that sheet by following its guide step (10–20 min per sheet).
4. **Check and publish.** Kathy compares every headline number with the
   expected values, and then Kalven publishes (B8) and shares the link.

### Agree on these before starting
- **The same two files:** use the files in `data/` only, never your own download.
- **Exact names:** field and calculated-field names match exactly, including
  capitals and brackets.
- **One color list:** owner colors follow Mark's list.
- **One shared folder and one group chat:** use them for files and questions.

Swap roles freely. The plan only depends on someone owning each row.

---

## Step 1: The data files

Epoch's download (`data_centers.zip`) has seven CSVs. This dashboard uses two
of them. The originals are in `data/raw/`, and `scripts/prepare_data.py` turns
them into two clean files:

### `data/data_centers_clean.csv`: one row per data center (95 rows)

| Field | Meaning |
|-------|---------|
| `Name` | Data center / campus name |
| `Owner` | Company that owns it. Epoch's confidence tags (`#confident`, …) are removed. Blank owners are shown as `Unknown` |
| `Owner confidence` | Epoch's confidence in the owner: confident / likely / speculative / unknown |
| `Users` | AI labs using it, comma-separated |
| `Country`, `State`, `City`, `ZIP`, `Address` | Location |
| `Latitude`, `Longitude` | **Approximate** map position (see the note below) |
| `Location precision` | `ZIP code center`, `City (approx.)`, or `Unknown` |
| `Facility power (MW)` | Whole-site power today, including cooling. **Use this as "power".** |
| `IT power (MW)` | Power used by the computers alone. This is what Epoch's site calls "Current power". |
| `H100 equivalents` | Compute, counted in NVIDIA H100 chips |
| `Capital cost (2025 USD billions)` | Estimated build cost, **already in billions** |
| `Status` | `Operating` (IT power > 0) or `Not yet operating` |
| `Planned facility power (MW)`, `Planned completion` | Size and date of the last milestone in Epoch's timeline |
| `Chip types`, `Project` | Chip models in use; project name, e.g. Stargate |

### `data/capacity_by_month.csv`: one row per data center per month (7,273 rows)

| Field | Meaning |
|-------|---------|
| `Data center` | Matches `Name` in the file above |
| `Month` | First day of the month, December 2018 to January 2030 |
| `Period` | `To date` (up to October 2026) or `Planned` (after) |
| `Facility power (MW)`, `IT power (MW)`, `H100 equivalents`, `Total capital cost (2025 USD billions)` | The site's size in that month |

**What was changed from Epoch's files, and why:**
- **Running totals made summable:** Epoch's timeline lists each site's *total so
  far* at irregular dates. Adding those rows together would count the same
  megawatts many times. The monthly file carries each site's latest value
  forward to every month. So in any month, **SUM across sites = total
  capacity**. You never need a running total.
- **Approximate map positions:** Epoch gives street addresses, not coordinates.
  Latitudes and longitudes come from the site's ZIP code (60 US sites) or its
  city (34 sites; the non-US ones are hand-entered city centers). They are
  accurate to a few miles, not to the building. One site (Anthropic Barber
  Lake) has no location and won't appear on the map.
- **Data as of:** "Today" is 2026-10-26, the date the data was downloaded.
- **Updating the data:** download a new zip, replace the CSVs in `data/raw/`,
  and run `pip install pandas zipcodes` followed by
  `python scripts/prepare_data.py YYYY-MM-DD`, using the download date.

**Credit Epoch on the dashboard.** The data is licensed CC BY 4.0
(`data/raw/EPOCH_LICENSE.md`). Use this text:
*"Source: Epoch AI, 'AI data centers', epoch.ai/data/ai-data-centers (retrieved Oct 2026). CC BY 4.0."*

---

## Part A: Power BI Desktop (free, Windows)

### A1. Load
1. **Home → Get data → Text/CSV** → `data_centers_clean.csv` → **Transform Data**.
2. In Power Query:
   - Make sure the number columns are **Decimal Number**. Power BI usually
     detects them on its own.
   - Set `ZIP` to **Text** so leading zeros are kept.
   - Rename the query to `DataCenters`.
3. Load `capacity_by_month.csv` the same way. Name it `Monthly`, and check that
   `Month` is typed **Date**.
4. **Close & Apply**. Then, in the Data pane, select `Latitude` and set
   **Column tools → Data category → Latitude**. Do the same for `Longitude`
   (Longitude) and `Country` (Country/Region).

### A2. Relationship
**Model view** → drag `DataCenters[Name]` onto `Monthly[Data center]`
(one-to-many, single direction). Now an Owner or Country filter also filters the
growth chart.

### A3. Measures
**Home → New measure**, one at a time:

```DAX
Total Power (GW) = DIVIDE ( SUM ( DataCenters[Facility power (MW)] ), 1000 )

Total H100e (M) = DIVIDE ( SUM ( DataCenters[H100 equivalents] ), 1000000 )

Sites = DISTINCTCOUNT ( DataCenters[Name] )

Total Capex ($B) = SUM ( DataCenters[Capital cost (2025 USD billions)] )

Share of Power =
DIVIDE (
    SUM ( DataCenters[Facility power (MW)] ),
    CALCULATE ( SUM ( DataCenters[Facility power (MW)] ), ALLSELECTED ( DataCenters ) )
)

Capacity (GW) = DIVIDE ( SUM ( Monthly[Facility power (MW)] ), 1000 )
```

`Capacity (GW)` is a plain sum, because each row of the monthly file already
holds the site's total for that month.

### A4. Build the visuals
1. **KPI cards**: add 4 **Card** visuals, one each for `Total Power (GW)`,
   `Total H100e (M)`, `Sites`, and `Total Capex ($B)`. In Format, set display
   units to *None* and decimals to 1.
2. **Map**: add a **Map** (or **Azure Map**) visual.
   - Latitude → `Latitude`, Longitude → `Longitude`, Bubble size →
     `Facility power (MW)`, Legend → `Owner`. Tooltips → `Name`,
     `H100 equivalents`, `Status`, `Location precision`.
3. **Bar chart**: add a **Clustered bar chart**.
   - Y-axis → `Owner`, X-axis → `Total Power (GW)`. Sort by the measure, descending.
   - Turn on data labels. For a cleaner chart, give all bars one color instead of
     one per owner.
4. **Growth chart**: add a **Stacked area chart**.
   - X-axis → `Monthly[Month]` (switch from the date hierarchy to plain *Month*),
     Y-axis → `Capacity (GW)`, Legend → `Monthly[Period]`. The planned months
     then show in a different color.
5. **Table**: add a **Table** with `Name`, `Owner`, `Country`, `Status`,
   `Facility power (MW)`, `H100 equivalents`, and
   `Capital cost (2025 USD billions)`. Add a data-bar conditional format on the
   power column.
6. **Slicers**: add three **Slicer** visuals for `Owner`, `Country`, and `Status`.
   Use the *Dropdown* style to save space.

### A5. Layout and polish
- Canvas: **View → Page view → Fit to page**, 16:9.
- Top row: title text box ("Frontier AI Data Centers"), then the 4 KPI cards.
- Middle row: the map (about 60% of the width) next to the bar chart (about 40%).
- Bottom row: the growth chart next to the table. Put the slicers in a slim column
  on the left.
- Give every owner the same color in every visual: **Format → Data colors**.
- Add a footer text box with the Epoch credit from Step 1.
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
*dimensions*. Numbers (power) are *measures*, which Tableau adds up
automatically (`SUM(...)`).

**Undo is your friend.** Ctrl+Z (Cmd+Z on Mac) undoes almost anything.

### B1. Load the data (10 min)

1. On the start screen, under **Connect → To a File**, click **Text file**. Pick
   `data_centers_clean.csv`.
2. You're now on the **Data Source** page. It shows your columns and a preview
   of the rows.
3. **Check the column types.** The small icon above each column name shows the
   type: `Abc` = text, `#` = number, a calendar = date, a globe = location.
   - `Latitude` and `Longitude` should already show a globe. If they don't,
     click the icon → **Geographic Role → Latitude** (or Longitude).
   - Click the icon on `Country` → **Geographic Role → Country/Region**.
   - If `ZIP` shows `#`, click it → **String**, so it isn't added up as a number.
4. **Add the monthly file.** On the left, under *Files*, click **Add** →
   **Text file** → `capacity_by_month.csv`. Drag it onto the canvas next to the
   first table. A line (a *relationship*) appears. In the box below, choose
   `Name` on the left and `Data center` on the right. This lets one Owner
   filter control every chart.
5. Click **Sheet 1** at the bottom-left to start building.

In the Data pane you'll now see two folders, one per file. Fields from the
monthly file are in the `capacity_by_month.csv` folder. **Use the
`data_centers_clean.csv` folder unless a step says otherwise.** Both files have
a `Facility power (MW)`, and the monthly one is only for the growth chart.

### B2. Make the headline numbers (15 min)

These are simple formulas called **calculated fields**.

1. Top menu: **Analysis → Create Calculated Field**.
2. Name it `Power (GW)`, type the formula below, and click **OK**:
   ```
   SUM([Facility power (MW)]) / 1000
   ```
   Tip: when you start typing `[`, Tableau suggests column names. Pick from the
   list so the spelling matches exactly. If it offers two `Facility power (MW)`
   fields, pick the one from `data_centers_clean.csv`.
3. Repeat for the other three:
   ```
   H100e (M)    →  SUM([H100 equivalents]) / 1000000
   Sites        →  COUNTD([Name])
   Capex ($B)   →  SUM([Capital cost (2025 USD billions)])
   ```
   (`COUNTD` means "count distinct": each site is counted once. Capex needs no
   division because the column is already in billions.)
4. **Build a number card:**
   - Rename the sheet: double-click the **Sheet 1** tab and type `KPI Power`.
   - Drag `Power (GW)` from the Data pane onto **Text** on the Marks card.
     A single number appears. It should be about **18.2**.
   - Click **Text** on the Marks card → the **…** button. In the editor, type
     `Total power (GW)` on a new line above the number, then make the number
     large (for example, 28 pt bold). Click **OK**.
   - To round it: right-click the pill → **Format** → Numbers → **Number (Custom)**
     → 1 decimal place.
5. **Make the other three cards:** right-click the `KPI Power` tab →
   **Duplicate**. On the copy, drag the old pill off the Marks card and drop in
   `H100e (M)`. Edit the label text. Repeat for `Sites` and `Capex ($B)`.
   You should get about 14.8, 95, and 539.

### B3. The map (15 min)

1. Click the **New Worksheet** icon (bottom bar, the small "+" sheet). Name the
   sheet `Map`.
2. In the Data pane, find **your** `Longitude` (in `data_centers_clean.csv`) and
   double-click it. Then double-click **your** `Latitude`. A map appears.
   ⚠ Tableau also adds fields called `Latitude (generated)` and
   `Longitude (generated)` in italics. Don't use those. They place points by
   country name, not by your coordinates.
3. **Beginner trap: you'll see only one dot.** That's because Tableau averaged
   all the coordinates. Fix it by dragging `Name` onto **Detail** on the Marks
   card. Now there's one dot per data center.
4. Drag `Facility power (MW)` onto **Size**. Bigger dots now mean more power.
   Click **Size** and drag the slider to the right if the dots look too small.
5. Drag `Owner` onto **Color**. Then click **Color** and set opacity to about 70%
   so overlapping dots stay visible.
6. Drag `H100 equivalents`, `Status`, and `Location precision` onto **Tooltip**.
   Hover over a dot to check that the pop-up shows them.
7. For a cleaner background: top menu **Map → Background Maps → Light**.
8. Bottom-right of the map, Tableau shows "**1 unknown**". That's Anthropic
   Barber Lake, which has no location. Right-click it → **Hide Indicator**.

Most sites are in the US (84% of the power), so the world view looks crowded
there. Zoom in on the US for a second view, or leave it zoomable on the dashboard.

### B4. Power by owner, as a bar chart (10 min)

1. New worksheet, named `By Owner`.
2. Drag `Owner` onto **Rows**. Drag `Power (GW)` onto **Columns**. Bars appear.
3. Click the **sort descending** button in the toolbar (bars with a down arrow) to
   put the biggest owner at the top. Google should be first, at about 3.9 GW.
4. Drag `Power (GW)` onto **Label** to show the number at the end of each bar.
5. To keep the colors consistent with the map: drag `Owner` onto **Color** too.
   For a calmer look, skip this and leave every bar the same color.

`Unknown` is a real bar (about 2.3 GW). It covers sites where Epoch doesn't know
the owner. Keep it, and mention it in a note, so the totals still add up.

### B5. Growth over time (15 min)

This chart uses the **monthly** file. It's already set up so that you just add
up each month, with no running totals.

1. New worksheet, named `Growth`.
2. From the `capacity_by_month.csv` folder, drag `Month` onto **Columns**. By
   default it shows as a blue pill reading `YEAR(Month)`. Right-click the pill
   and choose the **second** "Month" in the menu (the one that shows example
   dates like *May 2025*). The pill turns green, which means a continuous timeline.
3. From the same folder, drag `Facility power (MW)` onto **Rows**. The line
   climbs from near 0 in 2019 to about 50,000 MW in 2030.
4. In the Marks card dropdown (it says *Automatic*), choose **Area**.
5. From the same folder, drag `Period` onto **Color**. Planned months (after
   October 2026) now show in a different color.
6. Check it: hover over October 2026. It should read about **18,246 MW**,
   matching the `KPI Power` card.
7. Optional: to show GW instead, create a calculated field
   `Capacity (GW)` = `SUM([Facility power (MW)]) / 1000`, using the monthly
   file's field, and use it on Rows instead.

### B6. Detail table (10 min)

1. New worksheet, named `Table`.
2. Drag `Name`, `Owner`, `Country`, and `Status` onto **Rows**, one after another.
3. Double-click `Facility power (MW)`, `H100 equivalents`, and
   `Capital cost (2025 USD billions)` in the Data pane. Tableau adds them as
   columns of numbers.
4. To sort by power: hover over the `Facility power (MW)` column header and click
   the small sort icon that appears.

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
     Source**, so one filter controls every chart, including the growth chart.
   - ▾ → **Single Value (dropdown)** or **Multiple Values (dropdown)** saves space.
8. **Click-to-filter:** click the map, then click its **funnel icon** ("Use as
   Filter"). Do the same on `By Owner`. Now clicking a company's bar highlights
   only its sites everywhere. Press **Esc** or click an empty space to reset.
9. **Credit Epoch:** drag another **Text** object to the bottom. Paste the
   credit line from Step 1. Add a second line: *"Map positions are approximate
   (ZIP code or city center)."*

### B8. Save and share (5 min)

1. **File → Save to Tableau Public As…**, give it a name, and click **Save**.
   Your browser opens the published dashboard.
2. Copy the browser link to share it. On the web page, the **Share** button
   also gives you embed code.
3. To keep working later: in the app, **File → Open from Tableau Public**.

### If you get stuck

| What you see | What to do |
|--------------|------------|
| A field I need isn't in the Data pane | Look in both folders (one per file). Field names are listed in Step 1. |
| Calculated field says "The calculation contains errors" | Click the red message: usually a column name typo or a missing `]`. |
| Chart shows one big bar or one dot | Something got added up that shouldn't be. Drag `Name` onto **Detail**. |
| KPI power shows about 1,735 instead of 18.2 | You used `Facility power (MW)` from the monthly file. Use the one from `data_centers_clean.csv`. |
| Line chart shows only a few points | The date pill is blue. Right-click → the second "Month" option. |
| Owner filter doesn't change the growth chart | The relationship in B1 step 4 is missing, or the filter isn't set to **All Using This Data Source**. |
| A sheet looks crushed on the dashboard | Click it → ▾ → **Fit → Entire View**. |
| Everything went wrong | Ctrl+Z, or right-click the sheet tab → **Clear Sheet** and start that sheet again. |

---

## Insights to look for and annotate

Here's what the data shows as of 26 October 2026. Use these as starting points
for the dashboard notes, and re-check them if you update the data.

- **Fast growth:** total facility power went from 0.7 GW (January 2024) to
  2.7 GW (January 2025), 9.5 GW (January 2026), and 18.2 GW today. Planned
  sites take it to about 50 GW by 2030.
- **A few companies:** Google (21%), Meta (16%), Amazon (12%), and Microsoft
  (11%) together hold about 60% of today's power. Another 12% has an unknown
  owner.
- **Mostly American:** US sites hold 84% of today's facility power.
- **Gigawatt sites:** two sites already pass 1 GW (Colossus 2 and
  Anthropic-Amazon New Carlisle). 16 are planned to reach it.
- **Cost:** operating sites cost roughly $38 million per MW of IT power.
  To explore it, create `SUM([Capital cost (2025 USD billions)]) * 1000 / SUM([IT power (MW)])`.
- **Compute per MW:** `SUM([H100 equivalents]) / SUM([IT power (MW)])`
  shows which sites pack in more compute per megawatt, usually the ones with
  newer chips.

## Common pitfalls
| Symptom | Fix |
|---------|-----|
| Map shows no points | Lat/Long are text or lack a geographic role. Retype them. |
| Totals look too big | Power was summed from the monthly file across many months. Use the clean file for KPIs. |
| Your power totals differ from Epoch's website | Epoch's "Current power" is IT power (14.2 GW total). This guide uses facility power (18.2 GW). Both are correct, so say which one your dashboard shows. |
| Numbers show as "1.2E+3" | Set a number format (Power BI: Format pane; Tableau: Format → Numbers). |
