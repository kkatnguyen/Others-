# Visualizing Epoch AI's Frontier AI Data Centers dataset

A step-by-step guide to building an interactive dashboard from
<https://epoch.ai/data/ai-data-centers> in **Power BI** (Part A) or **Tableau Public** (Part B). Both parts are written for beginners.

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

## Part A: Power BI Desktop (free, Windows), for beginners

This part assumes you've never opened Power BI. Plan on about 2 hours for your
first time through. Every step says what you should see, so you can tell
right away if something went wrong.

### A0. Install and learn the screen (15 min)

1. **Install:** get **Power BI Desktop** free from the Microsoft Store (search
   "Power BI Desktop") or from <https://powerbi.microsoft.com/desktop>.
   - **Windows only.** There is no Mac version. On a Mac, use a school or work
     Windows computer, a Windows virtual machine (Parallels), or switch to the
     Tableau steps in Part B.
2. Open it. If it asks you to sign in, you can close that box. You don't need
   an account to build and save a report.

**The screen**

| Part | Where | What it's for |
|------|-------|---------------|
| **Three view icons** | Thin bar on the far left | **Report** (bar chart icon) is where you build. **Table** (grid icon) shows your data's rows. **Model** (three linked boxes) shows how your tables connect. |
| **Canvas** | Middle | Your report page. Visuals go here. |
| **Visualizations pane** | Right | Icons for each chart type. Under them are the **field wells** (boxes like *X-axis*, *Y-axis*, *Legend*) where you drop fields. |
| **Paintbrush icon** | Top of the Visualizations pane | **Format visual**: colors, fonts, titles, labels. |
| **Data pane** | Far right | Your tables and their columns. Click ▸ to open a table. |
| **Filters pane** | Between the canvas and the Visualizations pane | Filters. You can collapse it with its `<` arrow. |

**Two kinds of fields in the Data pane:**
- **Columns** come straight from your CSV. A **Σ** next to one means Power BI
  will add it up automatically.
- **Measures** (calculator icon) are formulas you write yourself, in step A4.

**To build any visual:** click an empty spot on the canvas, click a chart icon
in the Visualizations pane, and drag fields from the Data pane into its wells.
If a field lands in the wrong well, drag it back out. **Ctrl+Z** undoes
almost anything.

**Save often:** **File → Save as** → name it `AI Data Centers.pbix`.

### A1. Load the first file (10 min)

1. On the **Home** ribbon, click **Get data** → **Text/CSV**. (If you only see
   a big "Get data" button, click its lower half for the list.)
2. Choose `data/data_centers_clean.csv` → **Open**.
3. A preview window shows the first rows. Check that the columns are split
   correctly: `Name`, `Owner`, `Owner confidence`, … Then click
   **Transform Data**, *not* Load. This opens the **Power Query Editor**, where
   you fix column types before loading.
4. Look at the small icon on the left of each column header:
   `ABC` = text, `1.2` = decimal number, `123` = whole number, a calendar = date.
   - Click the icon on `ZIP` → **Text**. If asked, choose **Replace current**.
     ZIP codes are labels, not amounts to add up.
   - Check that these are `1.2` (decimal): `Latitude`, `Longitude`,
     `IT power (MW)`, `Facility power (MW)`, `H100 equivalents`,
     `Capital cost (2025 USD billions)`, `Planned facility power (MW)`.
     If one isn't, click its icon → **Decimal Number**.
   - `Planned completion` should be a calendar icon (**Date**).
5. On the right, under **Query Settings → Name**, change
   `data_centers_clean` to `DataCenters` and press Enter. The DAX formulas
   below use this name.
6. Don't click Close yet. Go on to A2.

### A2. Load the monthly file (5 min)

1. Still in Power Query: **Home → New Source → Text/CSV** →
   `data/capacity_by_month.csv` → **OK**.
2. Check the types: `Month` = **Date** (calendar icon), and the four number
   columns are decimal.
3. Rename the query `Monthly`.
4. Click **Close & Apply** (top-left). Power BI loads both files. In the Data
   pane, you should now see two tables: **DataCenters** and **Monthly**.
5. To check, click the **Table view** icon on the far left and select
   `DataCenters` in the Data pane. The bottom-left should say *95 rows*. Then
   select `Monthly`, which should show *7,273 rows*.

### A3. Set column details (10 min)

These settings tell Power BI how to treat some columns. Stay in **Table view**.

1. **Map columns:** in the Data pane, click `Latitude` (under DataCenters). A
   **Column tools** ribbon appears at the top. Set:
   - **Data category → Latitude**
   - **Summarization → Don't summarize** (otherwise Power BI adds the
     latitudes together, and the map breaks)

   Do the same for `Longitude` (Data category → **Longitude**).
2. Click `Country` → **Data category → Country/Region**.
3. Click `ZIP` → **Data category → Postal code**.
4. **Connect the two tables:** click the **Model view** icon (far left). You'll
   see two boxes, one per table.
   - Drag `Name` from the **DataCenters** box onto `Data center` in the
     **Monthly** box.
   - A **New relationship** window opens. Check that it says
     **Cardinality: One to many (1:\*)** and **Cross-filter direction: Single**.
     Click **OK** (or **Save**).
   - A line now joins the boxes, with **1** on the DataCenters side and **\***
     on the Monthly side. Now, filtering by Owner or Country also filters the
     growth chart.

### A4. Write the measures (20 min)

A **measure** is a saved formula, like a spreadsheet formula, written in a
language called DAX. You'll write six of them.

1. Go back to **Report view** (top icon on the left).
2. In the Data pane, **right-click the `DataCenters` table → New measure**.
   A formula bar opens above the canvas with `Measure = `.
3. Select all the text in the formula bar, paste the first formula below, and
   press **Enter**. A new field with a calculator icon appears under
   DataCenters.
4. Repeat for each formula. Paste them one at a time, not all at once:

```DAX
Total Power (GW) = DIVIDE ( SUM ( DataCenters[Facility power (MW)] ), 1000 )
```
```DAX
Total H100e (M) = DIVIDE ( SUM ( DataCenters[H100 equivalents] ), 1000000 )
```
```DAX
Sites = DISTINCTCOUNT ( DataCenters[Name] )
```
```DAX
Total Capex ($B) = SUM ( DataCenters[Capital cost (2025 USD billions)] )
```
```DAX
Share of Power =
DIVIDE (
    SUM ( DataCenters[Facility power (MW)] ),
    CALCULATE ( SUM ( DataCenters[Facility power (MW)] ), ALLSELECTED ( DataCenters ) )
)
```

5. For the last one, **right-click the `Monthly` table → New measure** so it's
   stored with the monthly data:

```DAX
Capacity (GW) = DIVIDE ( SUM ( Monthly[Facility power (MW)] ), 1000 )
```

**What the formulas mean:** `SUM(...)` adds up a column. `DIVIDE(a, b)` is
a ÷ b, and it returns blank instead of an error if b is 0. `DISTINCTCOUNT`
counts each site once. `Share of Power` divides one owner's power by the total
for whatever is currently filtered. `Capacity (GW)` is a plain sum, because
each monthly row already holds the site's total for that month.

6. **Round the numbers:** click a measure in the Data pane. On the
   **Measure tools** ribbon, set the decimal places to **1**. For
   `Share of Power`, click the **%** button instead. `Sites` needs 0 decimals.

**If a formula turns red or shows an error:** there's usually a typo in a
column name. Delete the column name, start typing `DataCenters[`, and pick the
column from the list that appears.

### A5. Headline number cards (15 min)

1. Click an empty spot on the canvas → in Visualizations, click **Card** (the
   icon showing "123"). If you see both **Card** and **Card (new)**, either
   works. These steps use Card.
2. Drag `Total Power (GW)` into the **Fields** well. The card shows
   **18.2**, with "Total Power (GW)" under it.
3. Make it look good: with the card selected, click the paintbrush
   (**Format visual**):
   - **Callout value** → font size 28, bold.
   - **Category label** → leave it on. It shows the measure's name.
4. **Make the other three:** select the card, press **Ctrl+C** and then
   **Ctrl+V**, drag the copy to the side, and swap the field in its Fields well
   for `Total H100e (M)`. Repeat for `Sites` and `Total Capex ($B)`.
5. **Check:** the cards read **18.2**, **14.8**, **95**, and **539.2**. If one
   is way off, open that measure (click it in the Data pane) and compare its
   formula with A4.
6. To make the labels friendlier, rename the measure in the well: double-click
   the field name in the visual's **Fields** well and type e.g.
   *"Facility power (GW)"*. This changes the label only on that card.

### A6. The map (20 min)

1. Click an empty spot → click **Azure Map** (a globe with a pin) in
   Visualizations. If there's no Azure Map, use **Map** (a plain globe).
2. Drag these fields from **DataCenters** into the wells:
   | Well | Field |
   |------|-------|
   | Latitude | `Latitude` |
   | Longitude | `Longitude` |
   | Size (or Bubble size) | `Facility power (MW)` |
   | Legend | `Owner` |
   | Tooltips | `Name`, `H100 equivalents`, `Status`, `Location precision` |
3. You should see bubbles across the US, plus a few in Europe and Asia.
   Bigger bubbles mean more power.
4. **If the map is blank with a message about map visuals being disabled:** go
   to **File → Options and settings → Options → Security** (under *Global*).
   Tick the box that allows map visuals, click **OK**, and then close and
   reopen Power BI.
5. **If all bubbles land in one spot or in the ocean:** `Latitude`/`Longitude`
   are being added up. Redo A3 step 1 (**Don't summarize**). Also check that
   their well entries don't read "Sum of Latitude". If they do, click the ▾ next
   to the field in the well → **Don't summarize**.
6. **Tooltip names:** in the Tooltips well, `Name` may show as
   "First Name". Click its ▾ → **First** is fine. Sites sharing a ZIP code
   (e.g. QTS Richmond 1–3 in Sandston, VA) share one bubble, and the tooltip
   shows only one name. That's the trade-off of ZIP-level positions.
7. Format → **Bubbles** (or **Bubble layer**): set transparency to about 30% so
   overlaps are visible. Zoom the map to the US with the mouse wheel. The
   dashboard keeps the view you leave it on.

### A7. Power by owner, as a bar chart (10 min)

1. Empty spot → **Clustered bar chart** (horizontal bars).
2. **Y-axis** → `Owner`. **X-axis** → `Total Power (GW)`.
3. Sort it: click the **…** (More options) at the top-right of the visual →
   **Sort axis** → **Total Power (GW)**, then **…** → **Sort axis → Sort
   descending**. Google should be on top at about 3.9.
4. Format → **Data labels → On** to show the number at the end of each bar.
5. `Unknown` (about 2.3 GW) is a real bar. It covers sites whose owner Epoch
   doesn't know. Keep it so the bars add up to the total.

### A8. Growth over time (15 min)

1. Empty spot → **Stacked area chart**.
2. **X-axis** → `Month` from the **Monthly** table.
   - Power BI turns dates into a *Date Hierarchy* (Year → Quarter → Month → Day)
     and shows only years. Click the **▾** next to `Month` in the X-axis well
     and choose **Month** (the field itself, not "Date Hierarchy"). You
     now get one point per month.
3. **Y-axis** → `Capacity (GW)` (the measure in Monthly).
4. **Legend** → `Period` (from Monthly). "To date" and "Planned" now show in
   different colors.
5. **Check:** hover over October 2026. It should read about **18.2**, the same
   as the power card. The far right (January 2030) shows about **49.9**.
6. Format → **Title → Text**: *"Total facility power, GW (planned after Oct 2026)"*.
7. **If the line is flat or jagged with 1,000+ values:** you used the
   `Facility power (MW)` *column* instead of the `Capacity (GW)` measure. Swap it.

### A9. Detail table (10 min)

1. Empty spot → **Table** visual (grid icon).
2. Drag these fields into **Columns**, in this order: `Name`, `Owner`,
   `Country`, `Status`, `Facility power (MW)`, `H100 equivalents`,
   `Capital cost (2025 USD billions)`.
3. Sort it by clicking the `Facility power (MW)` column header in the visual.
   Click it again to reverse the order.
4. **Data bars:** in the Columns well, click ▾ next to `Facility power (MW)` →
   **Conditional formatting → Data bars** → **OK**. Each row gets a small bar.
5. Shorter headers: double-click a field in the Columns well to rename it for
   this visual, e.g. *"Power (MW)"*, *"Capex ($B)"*.

### A10. Filters (slicers) (10 min)

1. Empty spot → **Slicer** (a funnel on a box). Drag `Owner` into **Field**.
2. Format → **Slicer settings → Options → Style → Dropdown**. This keeps it
   small.
3. Copy and paste it twice, and swap the field to `Country` and `Status`.
4. **Test:** choose *Meta* in the Owner slicer. Every visual should update,
   including the growth chart. That works because of the relationship from
   A3. Clear the slicer with its eraser icon.

**Click-to-filter is already on.** Clicking a bar or a bubble filters or
highlights the other visuals. To change how one visual reacts, select the
source visual, then **Format ribbon → Edit interactions**. Small icons appear
on each other visual: a funnel (filter), a pie (highlight), or ⊘ (none).

### A11. Layout and polish (20 min)

1. **Page size:** click an empty spot on the canvas → Format → **Canvas
   settings → Type → 16:9**. Then **View → Page view → Fit to page**.
2. **Title:** **Insert → Text box** → type *"Frontier AI Data Centers"* → size
   24, bold. Put it top-left.
3. Arrange it like this (drag the visuals, and resize them from their corners):
   ```
   ┌─────────────────────────────────────────────────────────┐
   │ Title                                                   │
   │ [Power] [H100e] [Sites] [Capex]       [Owner][Country]  │
   ├───────────────────────────────┬─────────────────────────┤
   │ Map (≈60%)                    │ Power by owner (≈40%)   │
   ├───────────────────────────────┼─────────────────────────┤
   │ Growth over time              │ Detail table            │
   ├───────────────────────────────┴─────────────────────────┤
   │ Source line                                             │
   └─────────────────────────────────────────────────────────┘
   ```
4. **Line things up:** select several visuals with Ctrl+click → **Format ribbon
   → Align** → *Align top* / *Distribute horizontally*.
5. **One color per owner everywhere:** on the bar chart, Format → **Bars →
   Colors**. Turn on *Show all*, then set each owner's color to match the map.
   Power BI usually keeps them consistent on its own, but check.
6. **Theme (optional):** **View → Themes** to change all the colors at once.
7. **Credit Epoch:** **Insert → Text box** at the bottom. Paste the credit line
   from Step 1, and add *"Map positions are approximate (ZIP code or city center)."*
8. **Save** (Ctrl+S).

### A12. Share it (10 min)

- **Easiest: PDF.** Use **File → Export → Export to PDF**. Good for a class
  submission or a slide.
- **Share the file:** put `AI Data Centers.pbix` in a shared folder. Anyone with
  Power BI Desktop can open it and click around. The data is stored inside the
  file.
- **Publish online:** **Home → Publish** uploads it to the Power BI website.
  This needs a **work or school Microsoft account**. Personal emails (Gmail,
  Outlook.com) can't sign up. If your school gives you one, sign in with it
  when Publish asks, then share the link from the website.

### Team plan, if you use Power BI

The same roles as the Tableau team plan work here. Each person builds their
visuals in their own `.pbix` file, and Kalven combines them:
1. Everyone does **A1–A4 exactly as written**, with the same table names
   (`DataCenters`, `Monthly`) and the same measure names. Kathy shares the
   formulas as text so everyone pastes the identical ones.
2. Each builder selects their finished visual, presses **Ctrl+C**, opens
   Kalven's main file, and presses **Ctrl+V**. A pasted visual keeps working when
   the field and measure names match. Test this with one visual early.
3. If a pasted visual shows errors, Kalven rebuilds it from its step (A5–A10).

### If you get stuck

| What you see | What to do |
|--------------|------------|
| A field is missing from the Data pane | Click ▸ next to the table name to open it. Check that you renamed the tables in A1/A2. |
| Measure shows an error / red squiggle | A column name typo. Retype it and pick from the suggestion list. |
| Card shows 18,246 instead of 18.2 | You dropped the *column* `Facility power (MW)`, not the *measure* `Total Power (GW)`. |
| Card shows 1,735 | You used `Monthly[Facility power (MW)]`, which adds up every month. Use the DataCenters version. |
| Growth chart shows only a few points | The X-axis is on *Date Hierarchy*. Click ▾ → **Month**. |
| Owner slicer doesn't change the growth chart | The relationship is missing. Redo A3 step 4. |
| Map shows bubbles in the ocean | Latitude/Longitude are being summed. Use **Don't summarize** (A3, A6 step 5). |
| A visual vanished or looks tiny | Ctrl+Z, or check **View → Selection** to find it. |

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
