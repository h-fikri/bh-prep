"""Quick health check for the site.  Run from anywhere:

    pip install playwright && playwright install chromium     (once)
    python3 tools/smoke_test.py

What it checks
  DATA   every (week, day) has prep rows and a dry + freezer pick list; every prep dishSlug exists in dishes.json
         and every dish is used; no empty item names.
  PAGES  index / prep / pick (dry + freezer) / dish load at 320, 375 and 1200 px wide with no JS errors,
         no console errors and no sideways scrolling; the header shows SITE_NAME from assets/app.js;
         prep and pick lists actually render rows.
It starts its own local web server and stops it again. Exit code 0 = all good, 1 = something failed.
"""
import json
import pathlib
import re
import subprocess
import sys
import time

from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
PORT = 8799
BASE = f"http://localhost:{PORT}/"
DAYS = ["mon", "tue", "wed", "thu", "fri"]
failures = []


def check(ok, message):
    print(("  ok    " if ok else "  FAIL  ") + message)
    if not ok:
        failures.append(message)


def data_checks():
    print("DATA")
    prep = json.loads((ROOT / "data/prep.json").read_text(encoding="utf-8"))
    dishes = json.loads((ROOT / "data/dishes.json").read_text(encoding="utf-8"))
    pick = json.loads((ROOT / "data/pick.json").read_text(encoding="utf-8"))
    slugs = {d["dishSlug"] for d in dishes}
    check(len(slugs) == len(dishes), f"{len(dishes)} dishes, all slugs unique")
    used = {r["dishSlug"] for r in prep if r["dishSlug"]}
    check(used <= slugs, "every prep dishSlug exists in dishes.json" + ("" if used <= slugs else f" (missing: {sorted(used - slugs)})"))
    check(slugs <= used, "every dish is used by a prep row" + ("" if slugs <= used else f" (unused: {sorted(slugs - used)})"))
    check(all(r["item"].strip() for r in prep), "no empty prep item names")
    for week in (1, 2):
        for day in DAYS:
            n_prep = sum(1 for r in prep if r["week"] == week and r["day"] == day)
            lists = {r["list"] for r in pick if r["week"] == week and r["day"] == day}
            check(n_prep > 0, f"Week {week} {day}: {n_prep} prep rows")
            check({"dry", "freezer"} <= lists, f"Week {week} {day}: pick lists present {sorted(lists)}")


def page_checks():
    print("PAGES")
    site_name = re.search(r'const SITE_NAME = "([^"]+)"', (ROOT / "assets/app.js").read_text(encoding="utf-8")).group(1)
    pages = [
        ("index.html", None),
        ("prep.html?week=1&day=mon", ".list-item"),
        ("prep.html?week=2&day=fri", ".list-item"),
        ("pick.html?week=1&day=mon&list=dry", ".pick-item"),
        ("pick.html?week=2&day=fri&list=freezer", ".pick-item"),
        ("dish.html?dish=beef-lasagne", "table.table tbody tr"),
    ]
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for width in (320, 375, 1200):
            ctx = browser.new_context(viewport={"width": width, "height": 800}, service_workers="block")
            page = ctx.new_page()
            errors = []
            page.on("pageerror", lambda e: errors.append(str(e)))
            # Only errors from our own files count (Google Fonts can be unreachable in a sandbox and that is fine).
            page.on("console", lambda m: errors.append(m.text) if m.type == "error" and (m.location.get("url") or BASE).startswith(BASE) else None)
            for url, selector in pages:
                errors.clear()
                page.goto(BASE + url)
                page.wait_for_timeout(600)
                label = f"{width:>4}px {url}"
                brand = page.locator(".brand-text strong").inner_text()
                overflow = page.evaluate("document.documentElement.scrollWidth > window.innerWidth")
                rows = page.locator(selector).count() if selector else 1
                check(brand == site_name, f"{label}: header says '{brand}'")
                check(not overflow, f"{label}: no sideways scroll")
                check(rows > 0, f"{label}: content rendered ({rows} rows)")
                check(not errors, f"{label}: no JS/console errors" + (f" {errors[:2]}" if errors else ""))
            ctx.close()
        browser.close()


def main():
    data_checks()
    server = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(PORT), "--bind", "127.0.0.1"],
        cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    try:
        time.sleep(1)
        page_checks()
    finally:
        server.terminate()
    print()
    if failures:
        print(f"{len(failures)} check(s) FAILED")
        sys.exit(1)
    print("All checks passed")


if __name__ == "__main__":
    main()
