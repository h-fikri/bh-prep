# Tools

Three small Python scripts. None of them is needed to **run** the site. They exist to (1) show exactly how the JSON was made from the kitchen's Excel files and (2) check that the site is healthy after a change.

| Script | Purpose | Needs |
|---|---|---|
| [`build_data.py`](build_data.py) | Excel prep workbooks → `prep.json` + `dishes.json` | `pip install openpyxl` |
| [`pick_data.py`](pick_data.py) | Excel prep workbooks → `pick.json` | `pip install openpyxl` |
| [`smoke_test.py`](smoke_test.py) | Data integrity checks + loads every page at 320, 375 and 1200 px wide | `pip install playwright` and `playwright install chromium` |

---

## Important: the JSON is the source of truth now

The two conversion scripts were run **once** to create `data/*.json`. From then on the plan is to fix things directly in the JSON on GitHub. If you re-run the scripts into the `data/` folder you will overwrite every hand edit.

Safe way to use them (for example when the Excel files change a lot, or to see what the conversion did):

```bash
python3 tools/build_data.py "<folder with the Excel files>" /tmp/new
python3 tools/pick_data.py  "<folder with the Excel files>" /tmp/new
for f in prep dishes pick; do
  diff <(python3 -m json.tool data/$f.json) <(python3 -m json.tool /tmp/new/$f.json) | head -50
done
```

Then copy across only what you want. On the day the scripts were added to the repository, the output was **byte-for-byte identical** to the committed JSON (294 prep rows, 81 dishes, 85 dish links, 175 pick rows: 125 dry and 50 freezer).

The Excel files are **not** in this repository (they are the kitchen's working files, kept in the cook's own `2027 Summer` folder). To re-run the scripts you need that folder.

---

## What the Excel files look like (input)

A folder containing ten workbooks named exactly `Prep Week <1|2> - <Monday..Friday> - Recipes.xlsx`. Each workbook has:

| Sheet | Content | Columns |
|---|---|---|
| 1 (any name) | **Prep list** for that day. Rows 1 to 3 are title lines; row 4 is the header. A row with text in column A only and in capitals (`MAINS`, `VEG`, `SOUPS`, `PREP`) starts a section. | Item, Serve, Qty, Notes, Done |
| 2 `Dry Store Pick` | The dry store pick list, already built (with the cook's rules applied). Group headings are rows with only column A filled. A second block starts at a row whose A cell is `Item` ("From the prep list"). | Ingredient, Pick, For (dish), ✓  (block 2: Item, Qty, Note, ✓) |
| 3 and onwards | **One recipe per sheet.** A1 = dish title. A2 = `Recipe: ...`, or starts with `BIP` for a bought-in product. Row 4 = header. Ingredients from row 5. A row with only column A filled is a sub-recipe heading. Rows labelled `Recipe notes`, `NOTE` or with only column D filled are notes. | Ingredient, Amount, Unit, Notes, Location |

Location codes in recipe sheets look like `6 - Dry Store`, `1 - Meat Fridge`, `2 - Vegetable Processed Fridge`, `4 - Dairy Fridge`, `7 - Prep Room`, `Freezer`. The leading number is dropped and the name is mapped (see `LOC_MAP` in `build_data.py`).

Other files that existed in the same folder during the project (not read by these scripts): `Barwon_Health_Recipes_ALL.xlsx` (master database: Recipe, Ingredient, Amount, Unit, Notes, Recipe Notes, Source File, Location; 748 rows), `Dry Store Pick List - Tuesday.xlsx` (the early format experiment), and `Veg List - Week 1 and 2.xlsx` (Week, Day, Item, Serve, Qty, Notes, Location, Picked; the Location column is still blank and is what is needed to put veg on the pick lists).

The Excel files were themselves made earlier from **photos** of the printed prep sheets and the recipe books (so notes such as "please verify" or "cut off in the photo" came from reading handwriting).

---

## `build_data.py`

```
python3 tools/build_data.py "<folder>" <output folder>
```

Writes `prep.json` and `dishes.json` into the output folder, then prints checks.

Rules it applies:

- **Units** are shortened: Kilogram → `kg`, Gram → `g`, Liter → `L`, Milliliter → `mL`, Each → `each`, Piece → `pc`, Serve → `serve`, Sheets → `sheets`. Pack units such as `Can/450g` become `0.5 can (450g)`.
- **Recipe sheets** keep title, ingredients, amounts and notes only. Times, temperatures, production amounts and method are not read.
- **BIP** sheets get the note `Bought in product (no recipe)`.
- **Sub-recipe headings** become `group` on the ingredients below them. A trailing "(used for ...)" is cut off.
- **Same dish on several days** is stored once when the ingredient lists match (group, name, amount, ingredient note and location must all match; recipe-level notes are ignored for the match). If the same name had *different* recipes it would be split into `<slug>-wk<N>-<day>` dishes and listed under `CONFLICTS`. Today there are none.
- **`dishSlug`**: lower case, `&` and `+` become "and", other characters become hyphens.
- **`location` on prep rows**: for mains, the Freezer / Dry Store locations of the recipe's ingredients; for other rows, picked up from the words freezer, dry store, meat fridge, dairy fridge in the note or qty.

What it prints, and what to look for:

```
prep rows 294 | dishes 81 | dish links 85
CONFLICTS (same name, different recipe):      <- should be empty
ODD AMOUNT: ...                               <- ingredients with a blank/odd amount (4 today)
missing slugs: []                             <- should be empty
unused dish sheets: 0                         <- should be 0
```

## `pick_data.py`

```
python3 tools/pick_data.py "<folder>" <output folder>
```

Writes `pick.json`, then prints row counts (`dry: 125, freezer: 50, total 175`) and three sample freezer lists.

- **Dry lists** are copied row for row from sheet 2 of each workbook. That sheet already follows the cook's rules (litres count as kg, 3 kg tins for Tomato Crushed and Paste, never share a tin between dishes, and so on; the full list is in [`../data/README.md`](../data/README.md)).
- **Freezer lists** are **derived**: every recipe ingredient whose location is Freezer, summed per ingredient across the day's dishes, plus prep-list lines that say freezer or frozen. Veg and soup rows are skipped. Bought-in dishes are skipped.
- **`EARLY`** at the top of the script lists dishes that are prepped a day early: `(2, "fri")` → picked on Thursday: *Moroccan Lamb Tagine*, *Beef Lasagne*. Their freezer lines move to Thursday under *For Friday prep – pick today*.
- **`UNITS`** maps `liter`/`l` to `kg` on purpose (the cook's rule: 1 L = 1 kg). There are no litre items in the freezer data today, so this has no visible effect yet.
- A special note is added to *Noodle Singapore (frozen)* on Week 1 Monday so the tofu noodle pack count is not double counted.

## `smoke_test.py`

```
python3 tools/smoke_test.py
```

Starts its own web server on port 8799 and stops it afterwards. Exit code 0 means everything passed.

**Data checks:** all dish slugs unique; every prep `dishSlug` exists in `dishes.json`; every dish is used by a prep row; no empty prep item names; each of the 10 week/day pairs has prep rows and both a dry and a freezer pick list.

**Page checks** (at 320, 375 and 1200 px wide, six pages: home, two prep lists, a dry list, a freezer list, a recipe): the header shows the `SITE_NAME` from `assets/app.js`; no sideways scrolling; list or table rows rendered; no JavaScript errors and no console errors from the site's own files (a blocked Google Fonts request is ignored on purpose).

It does **not** yet check: tick persistence, the filter, the Confirm flow on the home page, printing, offline mode or colour contrast. Those were checked by hand with throw-away Playwright scripts during the build; turning them into permanent tests is on the backlog in [`../docs/HANDOFF.md`](../docs/HANDOFF.md).
