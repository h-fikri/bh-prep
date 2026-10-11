# Handoff: McKellar Centre Kitchen Prep, version 1

Written on 11 October 2026, at the end of the first build session, for **a new person or a new Claude session whose job is to evaluate version 1 and improve it**.

Read in this order: this file → [`../README.md`](../README.md) → [`../data/README.md`](../data/README.md) → [`DESIGN.md`](DESIGN.md) → [`../tools/README.md`](../tools/README.md). Then run the site and the smoke test before changing anything.

- Live site: https://h-fikri.github.io/bh-prep/
- Repository: https://github.com/h-fikri/bh-prep (public, default branch `main`, 15 pull requests merged so far)
- Stack: static HTML, CSS and JavaScript, three JSON data files, a service worker. No build step.

**Contents:** [1 The person](#1-the-person-and-how-to-work-with-him) · [2 The project](#2-the-project) · [3 History](#3-what-was-built-and-in-what-order) · [4 Decisions](#4-decisions-and-why) · [5 Kitchen rules](#5-kitchen-rules-the-cook-has-stated) · [6 State of v1](#6-state-of-version-1) · [7 Issues and backlog](#7-known-issues-and-backlog) · [8 Evaluation plan](#8-how-to-evaluate-v1-properly) · [9 Questions to ask](#9-questions-to-ask-the-cook-first) · [10 Working agreement](#10-working-agreement-and-workflow) · [11 Starter prompt](#11-starter-prompt-for-the-new-chat) · [12 Gotchas](#12-environment-gotchas)

---

## 1. The person and how to work with him

- **Husain**, a cook at the Barwon Health McKellar staff cafe. Friendly, informal tone is welcome. He chats in casual English with typos; a screenshot from his phone is often the best bug report. (How he likes to be addressed is in his Claude preferences, which apply automatically in every session, so it is not repeated here.)
- **Short, direct answers. Bottom line first.** No long explanations or side details. When there is something for him to do (merge a PR, refresh), say it in one line.
- **Be persistent in research.** He asked not to jump to a conclusion in one shot: check the code, the data and the live behaviour before answering.
- He **knows a bit of HTML, CSS and JavaScript** and wants to **edit directly on GitHub** afterwards without re-asking. He does not want to fix things by hand if something is wrong with the site.
- He **merges the pull requests himself** on github.com. After a merge, he looks at the live site on his phone and sends a screenshot.
- Browser caching has confused him before (he saw the old design after a merge). When a change "does nothing", first check that it is merged, then tell him to hard-refresh (Ctrl + Shift + R, or reload twice on a phone).
- He reacts well to **"think about it first"** design work (the filter chips were redone because the selected state was unclear). He likes seeing the result, not a plan.

## 2. The project

**Goal.** A website for the kitchen team to see, on a phone, what to prep and pick each day of the **Summer Menu (Week 1 and Week 2, Monday to Friday)**: the prep list, the recipe for each main, a **Dry Store pick list** and a **Freezer pick list**, with tick boxes.

**Where the content came from.** Photos of printed prep sheets and recipe books → Excel files (made in earlier chats under the Claude Project "PREP SUMMER MENU") → JSON files via the scripts in `tools/` → the site.

**Project rules for anything recipe related** (from the Project's instructions): scan the image, extract the text, generate Excel files. For recipes keep **only the title, ingredients, amounts and notes**. Exclude times, temperatures, production amounts, production dates and method.

**Constraints that shaped the design:**
- Hosted free on GitHub Pages, so no server and no database.
- Must be editable by a cook who knows a little code, on github.com, with no tooling.
- Used on phones in a kitchen, sometimes with no signal.
- It is an internal tool, not an official Barwon Health site (no Barwon Health branding).

## 3. What was built, and in what order

The repository already existed as the cook's **autumn menu** site (pull requests 1 to 6: week rotation anchor, manual week/day override, an autocomplete box on the home page). The summer build replaced its content and then iterated on the front end.

| PR | Title | What it did |
|---|---|---|
| 7 | Summer menu prep lists | Converted the Excel files to `prep.json` (294 rows) and `dishes.json` (81 recipes, nested so one dish is one block), prep list page, recipe page, location filter. |
| 8 | Dry Store and Freezer pick lists | Added `pick.json` and `pick.html` with tick boxes, Print and Clear ticks. Dry lists copied from the cook's own sheets; freezer lists derived from recipes. |
| 9 | Front end v2 | One-tap home buttons, bigger text, tick boxes on the prep list, bottom navigation bar. |
| 10 | Front end v3 | Colour-coded sections, A4 print layout, offline support (service worker). |
| 11 | Home button and mains filter | Home button on inner pages; filter mains by serve time or by individual dish (mains only, not veg or soups). |
| 12 | Clearer filter design | Chips with visible selected state (tick), "Filtering: showing X of Y mains" bar, "Show list" and "Clear all". Service worker made to revalidate so edits show quickly. |
| 13 | Corporate look | Utility bar, header with menu, berry banners, slab headings, footer; inspired by the Barwon Health website without copying its branding. |
| 14 | Home: two cards and confirm | Home reduced to exactly two cards: "Next workday" and "Get started"; day picker hidden behind "Change day"; **Confirm** step before a list opens. |
| 15 | Site name in one place | `SITE_NAME` constant in `assets/app.js`. The cook had changed the `<title>` only, which changes the browser tab but not the header or footer. |
| 16 | Documentation | This documentation set, `tools/` scripts and screenshots. |

## 4. Decisions and why

| Decision | Why | Revisit if |
|---|---|---|
| **Static site, plain HTML/CSS/JS, no framework or build** | The cook can read and edit it; GitHub Pages serves it as is; nothing to install or break. | The app needs shared state, accounts or heavy interactivity. |
| **Content in JSON, never in HTML** | Fixing a typo is a one-line edit on github.com. | Editors keep breaking JSON (then add validation or a form). |
| **`dishes.json` is nested (one block per dish)** and prep rows link by `dishSlug` | A dish used on several days is stored once, so a fix happens in one place. | |
| **Separate `pick.json`** | Pick lists are keyed by day and list and have their own groups and rules. | |
| **Dry lists copied from the cook's sheets, freezer lists derived** | The dry lists already follow his detailed rules (tins, litres as kg). Freezer logic is simple enough to compute. | Rules change, or derived freezer lists miss items. |
| **Ticks in `localStorage` only** | No backend. Works offline. | The team wants ticks shared across phones (needs a backend). |
| **Network-first service worker** | Edits on GitHub must show up at once; cache is only the fallback when there is no signal. | |
| **Own identity, not Barwon Health's** | Avoids implying it is an official site; keeps the look professional. | The hospital wants it officially branded (their call, not ours). |
| **Week from an anchor date, with a manual override** | The kitchen alternates Week 1 / Week 2. Anchor confirmed in his work Google Calendar: Monday 12 October 2026 = Week 1. | The rotation ever breaks pattern. |
| **Saturday and Sunday show the next Monday** | Weekend visits are planning for Monday. | |
| **Home page: two cards and a Confirm step** | He found the earlier home confusing and wanted an explicit confirmation before a page opens. | |
| **Filters touch mains only (serve/dish); location touches everything** | He said he only cares about mains, not veg or soups. | |
| **Names and rules in one place** (`SITE_NAME`, `SITE_SUB`, `anchorDate` at the top of `app.js`) | So he can change them without hunting. | Move to a `data/config.json` (see backlog). |
| **All visible text set with `textContent`** | Safe against stray `<` and `&` in recipes. | |

## 5. Kitchen rules the cook has stated

These were stated by Husain during the Excel and pick-list work. They are applied in the data. If a future change touches quantities, check it against these.

- **Pick day:** he picks dry store ingredients **the day before** (for example Wednesday for Thursday). The site's pick lists are keyed by the **prep day**. See [question 1](#9-questions-to-ask-the-cook-first).
- **Dishes prepped a day early** (Week 2: *Moroccan Lamb Tagine* and *Beef Lasagne*, made Thursday for Friday) are picked on the earlier day in a separate section ("For Friday prep – pick today"), and shown on Friday as "Already picked Thursday – skip".
- **Pasta** picked on an earlier day's list (for example Thursday macaroni for Friday's dishes) counts as already picked. *Pasta Carbonara* uses 7 kg bowtie.
- **Units:** litres count as kilograms (1 L = 1 kg); mL and g stay as they are.
- **Tomato Crushed and Tomato Paste** come in **3 kg tins**. Each dish gets its own tins and a tin is **never shared between dishes**; each dish rounds up (1 kg = 1 tin).
- **10 kg box rule** applies only to Tomato Crushed and only when a dish needs exactly 9 kg or 10 kg (for example concasse 30 kg = 3 boxes). If any other case appears, tell him.
- **Tomato soup (A10 tins)** and **mandarin cans** come from the dry store. **Raspberries** are frozen.
- **Gravy and white sauce** are made by other cooks: leave them out of his pick lists.
- **BIP** = Bought In Product: no recipe, only a note on where to get it and how to cut it.
- **Prep-list items such as "Pear 5 boxes" and "2 fruits"** stay as separate rows with no combined total.
- **Dry Store Pick sheet format** he wanted: A4 portrait for printing, concise (what to pick first, which dish it is for second), subtle colours, not childish.
- **Veg items** will get a location of **Freezer** or **Processed Fridge** (he fills it in his Veg List file) so veg can later be mixed into the daily pick lists.
- **Folder layout (on his computer):** `2027 Summer/Prep-List` holds only the "… - Recipes" workbooks; plain prep lists, photos and docx notes were moved to "Prep-List extras".

## 6. State of version 1

Verified on 11 October 2026.

| Item | Status |
|---|---|
| Pages | Home, Prep list, Dry/Freezer pick list, Recipe: all working at 320, 375 and 1200 px wide, no JS errors (`python3 tools/smoke_test.py` passes). |
| Data | 294 prep rows, 81 dishes (750 ingredient lines, 14 bought-in), 175 pick rows (125 dry, 50 freezer). All 10 week/day pairs present. Every prep `dishSlug` resolves; every dish is used. |
| Data provenance | `tools/` regenerates the three JSON files **byte-for-byte** from the Excel files. |
| Size | JSON: 87 KB, 65 KB, 38 KB (about 20 KB gzipped in total); `app.js` 8 KB, `styles.css` 16 KB. Fast enough that performance is not a concern. |
| Week logic | Correct in the Australia/Melbourne time zone for a year of Mondays (tested). See P2-1 for other time zones. |
| Offline | Network-first service worker, cache `bh-prep-v4`. |
| Print | A4 portrait CSS exists and was checked as a PDF in Chromium. Not yet tested on a real printer. |
| Public exposure | Repository and site are **public**. |
| Not present | Web app manifest and icons, tests beyond the smoke test, CI, a data validator that gives friendly errors, veg on pick lists, shared ticks. |

## 7. Known issues and backlog

Ordered by how much they affect the kitchen. "Check" says how to confirm a fix.

### P1: affects daily use or correctness

1. **Ticks never reset.** Keys are `prep:{week}:{day}` and `pick:{week}:{day}:{list}`. Week 1 Monday comes back every fortnight, so **last fortnight's ticks will still be ticked**. The prep page has no "Clear ticks" button (only the pick pages do). *Options:* add Clear ticks to the prep page; include the date of the week (for example the ISO date of that Monday) in the key so each fortnight starts clean; auto-expire old keys. *Check:* tick items on Week 1 Monday, simulate the date two weeks later (Playwright `page.clock`), confirm boxes are empty and old keys are removed.
2. **Pick day versus prep day.** Lists are keyed by the prep day, but the cook picks the day before. Confirm what he expects Monday's list to mean, then make the labels say it ("Pick for Monday's prep"), or shift the data. Weekend behaviour (Saturday and Sunday show Monday) interacts with this.
3. **Veg is incomplete.** 71 VEG rows show only a name and serve time; the cook's Veg List file has a blank Location column; veg is not on the pick lists. *Needs input from the cook*, then extend `tools/` or edit JSON, then add a Veg group to the pick lists.
4. **Leftover transcription notes in recipes** (8, listed in `data/README.md`): "please verify", "cut off in the photo", "not readable". Check against the paper recipe and fix or delete. Includes *Beef Lasagne* sheets (30 or 70?), *Beef Burrito* tortillas, *Thai Curry Meatball* garlic (assumed grams).
5. **Odd quantities:** *Thai Ginger Fish* "199.62 serve" (freezer, Week 2 Friday); Basa fillet is counted in "serve" in three recipes (300, 225, 199.62). *Pasta Carbonara* has two unlabelled ingredient lists. Four blank amounts. Week 2 Wednesday's freezer list has 1 row and Week 2 Tuesday's dry list 8: check they are really that short.
6. **The repository is public.** Anyone with the link can read the recipes and prep lists. Decide: keep, or make private (GitHub Pages on a private repository needs a paid plan).

### P2: robustness and polish

1. **Week calculation is fragile outside Australia.** `getWeekNumber` divides a millisecond difference by seven days and floors it. It works for Melbourne because the anchor (1 Dec 2025) is in daylight saving time and winter dates are one hour later, which `floor` forgives. In Europe/London and America/New_York a test shows three Mondays in a year that do not alternate (for example 26 Oct 2026 in London) and many weekdays resolving to the wrong week. *Fix:* compare whole days (`Math.round(diff / 86400000)`), or use UTC dates. *Check:* run the same test under `TZ=Europe/London` and `TZ=America/New_York`.
2. **Configuration lives in code.** Move `SITE_NAME`, `SITE_SUB` and `anchorDate` to a `data/config.json` so there is a single, JSON-only editing surface (and the anchor and a "menu name / valid from / valid to" could live there).
3. **Recipe page has no context.** `dish.html?dish=slug` shows no week/day, no bottom bar, and "Back" uses `history.back()`, which does nothing if the link was opened directly or shared. Pass `week` and `day` in the link; add a "recipes" index with search.
4. **Inconsistent labels:** prep banner says "Week 1 · MON", others say "Monday".
5. **Dead code in `assets/app.js`:** `parseUserInput`, `getWeekdayOptions` and `filterWeekdayOptions` come from the autumn autocomplete and no page uses them any more; `renderNav` is an alias of `renderChrome`.
6. **CSS tidy-up:** rules are layered from successive redesigns (for example `.hero` shares a rule with `.header` and is overridden further down) and one class (`.primary-btn.secondary`) is unused; inline `<script>` blocks in each page could be separate files.
7. **Accessibility:** two colour pairs just miss 4.5:1 (muted grey on the page background 4.34; peach eyebrow on berry 4.38); the home radio group has no arrow-key support; the day segmented control uses `role=tab` without panels (should be toggle buttons or radios); no `aria-live` announcement when the filter count changes; `javascript:history.back()` link. Test at 200% zoom and with a screen reader.
8. **Add to Home Screen:** no `manifest.webmanifest` or icons, so the site cannot install as an app icon on a phone. Quick win.
9. **Filter state is not remembered** (lost on reload or when opening a recipe and coming back). Location values `Meat Fridge` and `Dairy Fridge` are supported by the code but never produced by the data.
10. **Print is untested on paper.** Check A4 margins, page breaks and whether the tick squares are big enough for a pen.
11. **Stale cache after deploys.** Network-first reduces it; consider a visible "new version available, reload" message or a version stamp in the footer.
12. **Fonts:** Zilla Slab comes from Google Fonts and is not cached offline. Self-host the font files (about 100 KB) if offline appearance matters.

### P3: ideas, only if the cook wants them

- **Test and validation safety net:** extend `tools/smoke_test.py` with tick persistence, the filter, the Confirm flow, offline mode and contrast; add a **GitHub Action** that validates the JSON (parse, slugs, codes, locations) on every push or pull request and fails with a plain-English message. This is the best protection for a site that is edited by hand on github.com.
- **Menu seasons:** the repository began as the autumn site. Decide whether future menus (winter, next summer) replace this one or live side by side (`data/summer-2026/…` with a switcher). Git history still holds the autumn version.
- **Shared ticks** across phones (needs a backend such as Firebase or Supabase). Probably unnecessary.
- Print a combined "day sheet" (prep + both pick lists); CSV export; dark mode; quantity scaling for different cover numbers.

## 8. How to evaluate v1 properly

The cook asked for persistent research, so evaluate with evidence, not impressions. Suggested order:

1. **Reproduce.** Clone, run `python3 -m http.server 8000`, run `python3 tools/smoke_test.py`, open each page at 320, 375 and 1200 px, take screenshots into a scratch folder.
2. **Data audit** (needs the Excel files re-attached by the cook, or the original photos):
   - Re-run the tools into a scratch folder and diff against `data/`.
   - Spot-check at least 10 recipes against the Excel files and the paper recipe (pay attention to units, circled or crossed-out handwriting, and the 8 flagged notes).
   - Recompute three freezer lists by hand.
   - Confirm every week/day has the right mains and serve times against the paper prep sheet (85 mains in total over the 10 days).
   - Search the data for typos, double spaces, mixed units (`L` vs `litre`), and amounts without units.
3. **Task walk-throughs** on a phone-sized screen, timing taps: *"It is 6 am Tuesday, open today's prep list"*; *"show only Wed Dinner mains"*; *"tick three items, reload, still ticked?"*; *"open a recipe and come back"*; *"print the dry store list"*; *"airplane mode: does everything still open?"*; *"two weeks later: are old ticks gone?"* (currently they are not).
4. **Code review:** `app.js` (week logic, chrome, storage), the inline scripts in the four pages, `sw.js` (cache strategy, `ignoreSearch` fallback, update behaviour), error handling when JSON is bad or `localStorage` is blocked.
5. **Accessibility pass:** contrast table in `DESIGN.md`, keyboard-only use, focus order, 200% zoom, screen reader labels.
6. **Resilience of editing:** break a JSON file on purpose and see what a cook would see; decide whether a friendlier error or a validation Action is needed.
7. **Report:** a ranked list of findings, each with evidence (screenshot, command output or file and line), a proposed fix, effort, and risk. Fix in small pull requests, one theme each.

## 9. Questions to ask the cook first

Ask these together at the start (one short message, with the answer options), since they change what to build:

1. **Pick lists:** is the Monday list for items to pick **on Monday morning** for Monday's prep, or to pick **the day before** (Friday or Sunday) for Monday? Should the labels say "pick for Monday prep"?
2. **Ticks:** should they reset each fortnight automatically, or only when someone taps "Clear ticks"? Does anyone need ticks to be shared between phones?
3. **Veg:** can he fill in the Location (Freezer or Processed Fridge) and quantity in the Veg List file so veg joins the pick lists?
4. **Name:** he typed "McKellar Kitchen Prep" in chat but the committed name is **"McKellar Centre Kitchen Prep"**. Which one?
5. **Public repository:** is it fine that anyone with the link can read the recipes? If not, make it private.
6. **Next menus:** will the next season replace this content, or should seasons live side by side?
7. **Who edits the data** and from what device (phone or computer)? That decides how much validation and friendliness the editing flow needs.

## 10. Working agreement and workflow

- **Branch, push, pull request, he merges.** Never push straight to `main`. One theme per PR. Description in plain words: what changed, how to check it, anything he must do.
- **Commit and PR attribution:** use the trailer lines the environment asks for. Previous sessions used `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>` and a `Claude-Session:` URL on commits, and `🤖 Generated with [Claude Code](https://claude.com/claude-code)` plus the session URL at the end of PR descriptions.
- **Test before reporting.** Run the smoke test; screenshot the pages you changed at phone width; read the screenshots back.
- **After he merges:** tell him to hard-refresh. If he says "nothing changed", check in this order: merged? (`gh api repos/h-fikri/bh-prep/pulls/N --jq .merged`), then cache, then whether the change is in the file that actually draws that text (the site name case: the title was edited, the header text lives in `app.js`).
- **Reply style:** bottom line first, short, friendly. One next step if there is a real one. No recap of the steps taken.
- **Do not start new features he has not asked for.** Propose, then wait.
- **Do not touch his data casually.** Quantities feed real kitchen decisions. Any data change should be traceable to his word or the source sheet.

## 11. Starter prompt for the new chat

Paste this as the first message of the new chat (inside the same Project, so the memory and these files are available):

```
Hi Claude. Please evaluate and then improve version 1 of my prep-list website.

Repo: https://github.com/h-fikri/bh-prep (live: https://h-fikri.github.io/bh-prep/)
Start by reading docs/HANDOFF.md, then README.md, data/README.md, docs/DESIGN.md and tools/README.md in the repo.

What I want:
1. First, evaluate v1 properly, with evidence: run it, run tools/smoke_test.py, check it on a phone-sized screen, audit the data, review the code and accessibility (section 8 of HANDOFF.md is the plan). Be persistent: do not conclude in one shot.
2. Show me a short ranked list of findings and ask me the questions in section 9 of HANDOFF.md in one go.
3. Then fix things in small pull requests (one theme each) and I will merge them. Start with the P1 items in section 7.

Keep answers short with the bottom line first, and do not start features I have not asked for.
```

## 12. Environment gotchas

Learned during the first build; they may or may not apply in a new session.

- **GraphQL was blocked** from the sandbox, so `gh pr create` failed with 403. Use the REST API: `gh api repos/h-fikri/bh-prep/pulls -f title=… -f head=BRANCH -f base=main -f body=…`. Merge status: `gh api repos/h-fikri/bh-prep/pulls/N --jq .merged`.
- **The GitHub Pages API and the live site were not reachable** from the sandbox (proxy). Verify the live result from his screenshots or in a browser that has access.
- **Google Fonts are unreachable in the sandbox**, so screenshots show a fallback serif and the console reports a failed font request (the smoke test ignores it on purpose).
- **Stop hook:** it complained that a branch had "unpushed commits and no remote branch" even after pushing. Fix: fetch the branch with an explicit refspec and set tracking by hand: `git fetch origin +refs/heads/X:refs/remotes/origin/X; git config branch.X.remote origin; git config branch.X.merge refs/heads/X`.
- **A local test server dies between shell commands.** Start it inside the same command as the test, or let `tools/smoke_test.py` start its own.
- **Playwright:** launch Chromium with `service_workers="block"` in tests, otherwise the service worker serves cached files between runs.
- **Browsers cache static files** (a plain static server sends `Last-Modified` and no `Cache-Control`, so they may reuse files heuristically): always hard-refresh when checking a change.
- **Excel files are not in the repo** and are not shared between sessions: ask the cook to attach the `2027 Summer` folder again if you need to re-run `tools/`.
