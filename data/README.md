# Data guide

All content on the site comes from three JSON files in this folder. The pages never contain recipe or list text themselves, so fixing the data fixes the site.

| File | Rows | Used by |
|---|---|---|
| [`prep.json`](prep.json) | 294 prep lines (10 days) | `prep.html`, and links to `dish.html` |
| [`dishes.json`](dishes.json) | 108 recipes (mains and soups), ingredient lines in `dishes.json` | `dish.html` |
| [`pick.json`](pick.json) | 175 pick lines (125 dry store, 50 freezer) | `pick.html` |

**The JSON is now the source of truth.** It was converted once from the kitchen's Excel files (see [`../tools/README.md`](../tools/README.md)). Do not re-run the conversion over these files after you have edited them by hand, or your edits will be overwritten.

---

## Before you edit: JSON in 60 seconds

- Text goes in `"double quotes"`. Numbers (`week`) and `true`/`false` (`skip`) have no quotes.
- Every line in a `{ ... }` block ends with a comma **except the last one**. Every `{ ... }` block in a list ends with a comma **except the last one**.
- Do not use straight double quotes inside text. Use `'single quotes'` or the typographic `“ ”`.
- A backslash starts an escape code. Avoid `\` in text.
- Keep the **exact spelling** of codes: `mon tue wed thu fri`, `dry` / `freezer`, `MAINS VEG SOUPS PREP`.
- Easiest safe way to edit on GitHub: press `.` on the repository page to open github.dev, which underlines JSON mistakes in red. On github.com the plain editor does not.
- If a page says "Failed to load ... data" after an edit, the JSON is broken. Open the file's History and revert the last commit.

## Codes used everywhere

| Field | Allowed values |
|---|---|
| `week` | `1` or `2` (a number, no quotes) |
| `day` | `"mon"`, `"tue"`, `"wed"`, `"thu"`, `"fri"` (lower case) |

Every week and day combination (10 in total) has prep rows and both pick lists.

---

## `prep.json`: the daily prep list

One object per line on a day's prep list. Order in the file is the order on the page. Sections appear in order of first appearance (currently MAINS, then VEG, SOUPS, PREP).

```json
{
  "week": 1,
  "day": "mon",
  "section": "MAINS",
  "item": "Chicken w Creamy Pesto Sauce",
  "dishSlug": "chicken-w-creamy-pesto-sauce",
  "location": "Dry Store",
  "usageNote": "Wed Dinner",
  "qty": "",
  "notes": ""
}
```

| Field | Meaning | Rules |
|---|---|---|
| `week`, `day` | Which day's list this row is on | See codes above. |
| `section` | Heading the row sits under | `MAINS`, `VEG`, `SOUPS` or `PREP`. The heading also picks the colour stripe (maroon / green / amber / grey). Another word works but gets no stripe colour. |
| `item` | Name shown on the list | Also used as the tick-box identity (see below). |
| `dishSlug` | Recipe to open when the name is tapped | `""` for no link, otherwise **must equal** a `dishSlug` in `dishes.json`. Only the 85 MAINS rows and 30 SOUPS rows have one (VEG and PREP rows never do). |
| `location` | Badge(s) shown under the item, and the Location filter | `""`, `"Dry Store"`, `"Freezer"`, or both as exactly `"Freezer | Dry Store"` (space, bar, space). Other place names work too and become filter chips automatically. |
| `usageNote` | Serve time shown on the right, e.g. `"Wed Dinner"` | For MAINS this is also the value of the **Mains by serve** filter. An empty value appears in the filter as "No serve time". Includes weekend serves such as `Sat Dinner`, `Sun Lunch`. |
| `qty` | Quantity text, e.g. `"5 boxes"`, `"10 pkt"` | Free text. Mostly empty (245 of 294 rows). |
| `notes` | Note shown in small text under the item | Free text. Includes hand-written notes from the printed sheet. |

Section sizes today: PREP 108, MAINS 85, VEG 71, SOUPS 30. Rows per day range from 22 (Week 2 Tuesday) to 34 (Week 1 Friday).

**How `location` was worked out** (the cook was told to check these): for a main it is the Freezer and Dry Store locations of that dish's recipe ingredients; for other rows it is picked up from the words "freezer", "dry store", "meat fridge" or "dairy fridge" in `notes` or `qty`. Today only `Dry Store`, `Freezer` and both appear.

**Veg rows** (`section: "VEG"`) carry a name and serve time only. Their quantities and locations are still blank in the source Veg List file.

### Tick boxes and what changing `item` does

The saved tick for a prep row is identified by the text `section|item|usageNote`. If you rename an item (or change its serve time), any tick someone already made on that row is forgotten. Two rows with identical section, item and usageNote on the same day would share one tick.

---

## `dishes.json`: recipes

One object per dish. Sorted alphabetically by `dishName`. Only the **title, ingredients, amounts and notes** are kept; times, temperatures, production quantities, dates and method are deliberately left out.

```json
{
  "dishSlug": "beef-lasagne",
  "dishName": "Beef Lasagne",
  "ingredients": [
    { "ingredient": "Beef Mince 90% Lean", "amountText": "15 kg" },
    { "ingredient": "Pasta Lasagne Sheets", "amountText": "70 sheets",
      "notes": "Printed 30 is circled with a handwritten 7 in front (reads as 70) - please verify" }
  ],
  "notes": ["Optional recipe-level note", "Another one"]
}
```

| Field | Meaning | Rules |
|---|---|---|
| `dishSlug` | The dish's id, used in links (`dish.html?dish=beef-lasagne`) | Lower case letters, digits and hyphens. **Must be unique** and must match the `dishSlug` in the prep rows that link to it. Do not change it unless you change those rows too. |
| `dishName` | Title shown at the top of the recipe page | Free text. |
| `ingredients[]` | The ingredient table, in order | At least one. |
| `ingredients[].ingredient` | Ingredient name | |
| `ingredients[].amountText` | Amount **as text**, already formatted with its unit | e.g. `"15 kg"`, `"500 g"`, `"200 mL"`, `"1.5 L"`, `"300 each"`, `"70 sheets"`, `"3 pkt (1kg)"`. `""` is allowed (4 ingredients have no amount in the source). |
| `ingredients[].notes` | Optional note for that ingredient | If **any** ingredient in the dish has one, the table gets a Notes column. 44 dishes have at least one. |
| `ingredients[].group` | Optional sub-recipe heading, e.g. a sauce made inside the dish | Rows with the same `group` must sit **next to each other**; a heading row is drawn each time the group changes. Used by 3 dishes: *Roast Chicken with creamy mushroom sauce*, *Thai Curry Meatball in Coconut Sauce*, *Thai Ginger Fish*. |
| `notes[]` | Optional list of recipe-level notes | Shown in a "Notes" box under the table (39 dishes). |

**Bought-in products (BIP).** 14 dishes are bought in and have no real recipe. Their `notes` contain `"Bought in product (no recipe)"` and the ingredient list says where to get or how to cut them (for example *Roast Beef*, *Crumbed Whiting*, *Vegetable Pattie*).

**Unit style used in `amountText`:** `kg`, `g`, `L`, `mL`, `each`, `pc`, `sheets`, `serve`, and pack forms such as `2 tub (1kg)`, `0.5 can (450g)`, `1 ctn (6x1.5kg)`.

### Known data issues in `dishes.json`

These came straight from the Excel files, which were typed from photos. Fix or delete them when checked against the paper recipe.

1. **Transcription remarks left in notes (8 places)**: *Baked Fish, bechamel herb crumb* (sticky note, "check list on board"), *Beef Pastitsio* (cut off at the edge of the photo), *Butter Chicken* (sheet text cut off), *Thai Curry Meatball in Coconut Sauce* (a hand-written line "not readable" and the garlic amount "assumed grams, please verify"), *Vegetable Cottage Cheese Slice* (sticker edge cut off), *Beef Burrito* (tortilla amount "please verify"), *Beef Lasagne* (lasagne sheets "please verify").
2. **Pasta Carbonara** has two full ingredient lists back to back with no label saying which is which (the first has "Changed by hand" notes and smaller amounts, the second has the larger amounts). Decide which is correct or add a `group` to each.
3. **Blank amounts:** *Chickpea & Potato Curry* (Spice blend), *Vegetarian Parmigiana* (Tomato Concasse, Cheese Tasty Shredded), *Vegetarian Quiche – spinach* (Quiche).
4. *White Sauce* appears in some recipes (for example Beef Lasagne, 20 L). The cook makes neither gravy nor white sauce; they were kept out of the **pick lists**, not out of the recipes.

### Adding a dish

1. Add a new object to `dishes.json` (keep alphabetical order if you can).
2. Choose a new, unique `dishSlug` (lower case, hyphens).
3. Add or edit a row in `prep.json` with the same `dishSlug`.
4. Run `python3 tools/smoke_test.py`. It fails if a prep row points to a missing dish, or a dish is used by no row.

---

## `pick.json`: dry store and freezer pick lists

One object per line on a pick list. Order in the file is the order on the page; rows with the same `group` are gathered under one heading (headings appear in order of first appearance).

```json
{
  "week": 1,
  "day": "mon",
  "list": "dry",
  "group": "Tinned tomato, beans & lentils",
  "item": "Tomato Crushed",
  "pick": "5 tins",
  "forDish": "Chicken w Creamy Pesto Sauce (1), Indian Butter Chickpea (1), Beef Tomato & Vegetable Mince (2), Ratatouille with Beans (1)",
  "note": "",
  "skip": false
}
```

| Field | Meaning | Rules |
|---|---|---|
| `week`, `day` | Which day the pick is for | Each list is keyed by the **prep day**, the day those dishes are prepped. (The cook usually picks the day before. Whether the site should label lists by prep day or by pick day is an open question, see `docs/HANDOFF.md`.) |
| `list` | Which list | `"dry"` or `"freezer"`. |
| `group` | Heading to sit under | `""` for no heading. |
| `item` | What to pick | Also the tick identity (`group|item`). |
| `pick` | How much, as text | e.g. `"5 tins"`, `"2.5 kg"`, `"8 pkt (12)"`. |
| `forDish` | Which dish(es) it is for, with the share in brackets | Small grey text. |
| `note` | Extra note | Joined to `forDish` with " · ". |
| `skip` | `true` greys the row out and disables its tick box | Used for lines such as "Already above – skip" and items already picked the day before. |

**Groups used on dry lists:** *Tinned tomato, beans & lentils*; *Pastes, sauces, milks & liquids*; *Pasta & grains*; *Tinned fruit & dried fruit*; *Other*; *From the prep list* (items such as "Pear 5 boxes" that come straight from the prep sheet and stay as separate rows). **Freezer lists** use *Freezer* (ingredients from recipes) and *From the prep list* (plus *For Friday prep – pick today* on Week 2 Thursday).

**Dishes prepped a day early** are picked on the earlier day. Week 2: *Moroccan Lamb Tagine* and *Beef Lasagne* are made on Thursday for Friday, so Thursday has groups *For Friday prep – pick today*, and Friday's dry list has *Already picked Thursday – skip* (rows with `skip: true`).

### Rules the pick lists follow (from the cook)

- Litres count as kilograms (1 L = 1 kg); mL and g stay as they are.
- Tomato Crushed and Tomato Paste come in 3 kg tins. Each dish gets its own tin(s); a tin is never shared between dishes (each dish rounds up, for example 1 kg = 1 tin).
- The 10 kg box rule applies only to Tomato Crushed, and only when a dish needs exactly 9 kg or 10 kg (for example concasse 30 kg = 3 boxes). If any other case appears, tell the cook.
- Pasta already picked on an earlier day's list (for example Thursday macaroni for Friday's dishes) counts as already picked.
- Gravy and white sauce are made by other cooks, so they are left out of the lists.
- Tomato soup (A10 tins) and mandarin cans come from the dry store. Raspberries are frozen.
- **Veg** is not on the pick lists yet (needs a Freezer or Processed Fridge location per veg item).

### Known data issues in `pick.json`

- **Fish Basa Fillet Frozen** is counted in "serve": `300 serve` for *Baked Fish, bechamel herb crumb* (Week 1 Thursday), `225 serve` for *Fish with Golden Coconut Sauce* (Week 2 Tuesday) and `199.62 serve` for *Thai Ginger Fish* (Week 2 Friday). The same figures are in `dishes.json` (copied from the recipes). 199.62 looks like a calculation leftover. Decide whether to show a round serve count or kg or fillets.
- Week 2 Wednesday's freezer list has one row only, and Week 2 Tuesday's dry list has 8. Check these against the real week.
- Freezer lists are **derived** (recipe ingredients located in the freezer, summed per item, plus prep-list lines that say freezer or frozen), so they can miss frozen items that the recipe sheets list under another location.

---

## Pre-commit checklist

1. JSON still valid (github.dev shows red squiggles if not).
2. Any new `dishSlug` in `prep.json` exists in `dishes.json`, and vice versa.
3. `day` is lower-case three letters and `week` is a number.
4. Locations use exactly `Dry Store` / `Freezer`, joined by ` | `.
5. After the change goes live: hard-refresh and open the page you edited.
6. Optional but best: run `python3 tools/smoke_test.py`.
