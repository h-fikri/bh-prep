# Design notes

How the site looks and why. Everything lives in [`../assets/styles.css`](../assets/styles.css) (about 1000 lines, one file, no preprocessor) and the small DOM builders in [`../assets/app.js`](../assets/app.js) and the pages.

## Intent

A tool used on a phone or tablet in a working kitchen: wet or gloved hands, glare, arm's length, quick glances. So: big tap targets, big text, high contrast, one obvious next step, and no clever interactions.
The visual language is "corporate healthcare website": warm neutral page, deep berry accent, slab-serif headings, flat square-ish cards, a dark utility bar and footer. It was inspired by the look of the Barwon Health website (screenshots and computed styles were studied for colour, type and layout), but it has **its own name, own logo mark (a tick in a rounded square) and own palette**. No Barwon Health logo, name or artwork is used, and the footer says it is an internal tool, not an official website. Keep it that way.

## Tokens (`:root`)

| Token | Value | Used for |
|---|---|---|
| `--bg` | `#f3f1f0` | Page background (warm grey) |
| `--text` | `#3c3838` | Body text, utility bar and footer background |
| `--muted` | `#69727b` | Secondary text, inactive bottom-nav items |
| `--accent` | `#86204f` | Deep berry: banners, links, selected chips, buttons, brand |
| `--accent-dark` | `#5e1537` | "Get started" card, confirm button text, card headings |
| `--accent-soft` | `#f6e9ef` | Active nav tint, filter summary bar |
| `--peach` | `#f2a27a` | Highlight on berry (eyebrow text, selected dot, confirm button), focus ring |
| `--surface` | `#ffffff` | Cards and list items |
| `--border` | `#ddd7d4` | Hairlines |
| `--radius` | `6px` | Corners everywhere (chips are fully round) |
| `--heading` | Zilla Slab, Rockwell, Roboto Slab, Georgia, serif | h1 to h3, brand name, hero subtitle |
| `--wrap` | `960px` | Maximum content width |

Section stripes (left border and heading colour on the prep list): `MAINS` berry `#86204f`, `VEG` green `#5f9a6b` (text `#2f6a3d`), `SOUPS` amber `#e0a15e` (text `#9a5f12`), `PREP` grey `#69727b` (text `#4b5563`).

Body font is the system UI stack at **17px**, line height 1.45. Headings use Zilla Slab from Google Fonts (weights 500, 600, 700 and italic 400); if it cannot load (offline, blocked) the fallbacks apply and nothing breaks.

## Layout

- One centred column, max 960px, 16px side gutters (`.wrap`, `.container`).
- **Utility bar** (dark, small): "Internal prep tool" on the left, "Week N · Day" on the right once a day is chosen.
- **Header** (white): tick-mark logo + name + "Summer Menu" subtitle; on screens 720px and wider the top menu (Home, Prep, Dry Store, Freezer) sits on the right with an underline for the current page.
- **Page banner** (`.header` on inner pages, `.hero` on home): solid berry block, peach eyebrow label, white slab heading, italic subtitle; action buttons sit inside it as white-outlined buttons.
- **Footer** (dark): site name and the "not an official website" line.
- **Bottom bar** on phones (below 720px), only when a week and day are known: four equal tabs, fixed to the bottom with the iPhone safe-area inset, current tab tinted. Pages add 76px bottom padding (`body.has-nav`) so nothing hides behind it.

## Components

| Component | Classes | Notes |
|---|---|---|
| Hero card | `.hero`, `.hero-top`, `.hero-btn` | Eyebrow = "Next workday" / "Today" / "Selected day". "Change day" outline button reveals the picker. |
| Day picker | `.picker`, `.segmented` + `.seg`, `.day-grid` + `.day-btn` | Week 1/2 toggle and five day buttons. Hidden until "Change day". |
| Get-started card | `.quick`, `.quick-option`, `.opt-dot`, `.quick-note`, `.confirm-btn` | Radio group of three options on dark berry. Selected = peach dot with a tick and a peach bar on the left. Confirm is translucent and disabled until a choice is made. |
| Buttons | `.filter-btn`, `.primary-btn`, `.reset-btn` | Outline (`.filter-btn`) and solid berry (`.primary-btn`). |
| Tick box | `input.tick`, `.pick-item input` | Native checkbox, 28 x 28px, `accent-color` berry. |
| Prep row | `.list-item`, `.item-main`, `.qty`, `.item-notes`, `.badges` / `.badge`, `.note` | Tick, name (link if a dish exists), quantity, note, location badges, serve time on the right. |
| Pick row | `.pick-item`, `.pick-name`, `.pick-qty` | Whole row is a `<label>`, so tapping anywhere ticks it. `.skipped` = 55% opacity and no tick. |
| Section | `.section`, `.sec-mains` `.sec-veg` `.sec-soups` `.sec-prep` | Coloured left border; heading is uppercase, letter-spaced, in the section's colour. |
| Filter chip | `.chip`, `.chip.on` | Off: white with a grey outline and hollow circle. On: solid berry, white text, tick in the circle. `aria-pressed` kept in sync. |
| Filter summary | `.active-filters`, `.active-head`, `.pill`, `.pill.clear` | Always visible when something is on, even if the panel is closed: "Filtering: showing X of Y mains", one removable pill per choice, "Clear all". |
| Recipe table | `.table`, `.group-row`, `.dish-notes` | Ingredient, Amount, optional Notes columns; sub-recipe heading rows; notes box with a peach left border. |

## Responsive rules

| Breakpoint | Change |
|---|---|
| default (phones) | Bottom bar, top menu hidden, hero title 1.75rem |
| max 480px | Hero title 1.5rem, no wrap |
| max 350px | Hero title 1.25rem and smaller "Change day" button (fixes 320px-wide phones) |
| min 720px | Top menu shown, bottom bar hidden, hero title 2.6rem, more padding |

## Print

`@page { size: A4 portrait; margin: 12mm }`. In print: chrome, filter panel, buttons and bottom bar are hidden; the banner becomes black text on white with a heavy rule; rows are white with thin grey borders and cannot split across pages; strike-through from ticks is removed (so a printed list is clean); tick boxes are 16px so they can be ticked with a pen. Print is available on the prep and pick pages via the Print button.

## Accessibility measures in place

- Native `<button>`, `<input type=checkbox>` and `<label>` elements; `aria-pressed` on chips and day buttons, `role=radiogroup` / `radio` + `aria-checked` on the home options, `aria-expanded` on Change day and Filter, `aria-label` on tick boxes ("Done: item") and on filter pills.
- Visible focus ring (3px peach outline, 2px offset) on keyboard focus.
- Selected state is shown by shape (tick) as well as colour.
- Page text is set with `textContent`, headings are real `h1`/`h2`, language is set (`lang="en"`).
- Touch targets: bottom tabs about 50px high, tick boxes 28px, list rows 14px padding, confirm button 16px padding.

### Measured contrast (WCAG ratios; 4.5 needed for small text, 3 for large)

| Pair | Ratio | Verdict |
|---|---|---|
| Body text `#3c3838` on page `#f3f1f0` | 10.3 | pass |
| Muted `#69727b` on page `#f3f1f0` | 4.34 | **just under** for small text (used for notes, subtitles, inactive tabs) |
| Muted `#69727b` on white | 4.89 | pass |
| Berry `#86204f` on white / white on berry | 9.0 | pass |
| Peach `#f2a27a` on berry `#86204f` | 4.38 | **just under** for the small uppercase eyebrow label |
| Peach on dark berry `#5e1537` | 6.24 | pass |
| Error red `#b00020` on page | 6.51 | pass |
| Utility bar text `#e9e4e1` on `#3c3838` | 9.17 | pass |

## Known design debt

- `styles.css` grew through several redesigns, so some rules are layered rather than clean (for example `.hero` first shares the banner rule with `.header`, then overrides padding and title size further down). Nothing is wrong on screen, but it is harder to read than it should be. A scan found one unused class (`.primary-btn.secondary`); every other class in the file is used by a page.
- Inconsistent day labels: the prep page banner says "Week 1 · MON" while the pick pages and home say "Week 1 · Monday".
- Heading font is a web font with no offline copy.
- No dark mode (the page forces `color-scheme: light`; a bright kitchen is the main use).
- Large inline `<script>` blocks in each page could move to separate files.
