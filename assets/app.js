const anchorDate = new Date(2025, 11, 1); // Monday, Week 2 anchor (local time)
const dayLabels = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
const dayShort = ["sun", "mon", "tue", "wed", "thu", "fri", "sat"];

function normalizeToLocal(date) {
  return new Date(date.getFullYear(), date.getMonth(), date.getDate());
}

function getWorkday(today) {
  const day = today.getDay();
  if (day === 6) {
    // Saturday
    const nextMonday = new Date(today);
    nextMonday.setDate(today.getDate() + 2);
    return normalizeToLocal(nextMonday);
  }
  if (day === 0) {
    // Sunday
    const nextMonday = new Date(today);
    nextMonday.setDate(today.getDate() + 1);
    return normalizeToLocal(nextMonday);
  }
  return normalizeToLocal(today);
}

function getWeekNumber(date) {
  const normalized = normalizeToLocal(date);
  const anchorNormalized = normalizeToLocal(anchorDate);
  const diffMs = normalized - anchorNormalized;
  const weeksSinceAnchor = Math.floor(diffMs / (7 * 24 * 60 * 60 * 1000));
  return weeksSinceAnchor % 2 === 0 ? 2 : 1;
}

function getSuggestedWeekday() {
  const today = new Date();
  const workday = getWorkday(today);
  const suggestedWeek = getWeekNumber(workday);
  const dayIndex = workday.getDay();
  return {
    week: suggestedWeek,
    dayShort: dayShort[dayIndex],
    dayLabel: dayLabels[dayIndex],
  };
}

function getWeekdayOptions() {
  const weekdays = [1, 2, 3, 4, 5];
  const options = [];
  [1, 2].forEach((week) => {
    weekdays.forEach((index) => {
      const dayShortValue = dayShort[index];
      const dayLabelValue = dayLabels[index];
      options.push({
        week,
        dayShort: dayShortValue,
        dayLabel: dayLabelValue,
        displayLabel: `Week ${week} · ${dayLabelValue}`,
      });
    });
  });
  return options;
}

function filterWeekdayOptions(options, query) {
  const text = query.trim().toLowerCase();
  if (!text) return [];
  return options.filter(
    (opt) =>
      opt.dayLabel.toLowerCase().startsWith(text) || opt.dayShort.toLowerCase().startsWith(text)
  );
}

function getQueryParams() {
  const params = new URLSearchParams(window.location.search);
  return Object.fromEntries(params.entries());
}

async function fetchJSON(path) {
  const response = await fetch(path, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`Failed to load ${path}`);
  }
  return response.json();
}

function renderMessage(target, text) {
  if (target) {
    target.textContent = text;
  }
}

function parseUserInput(text, fallbackWeek, fallbackDay) {
  if (!text) return null;
  const normalized = text.toLowerCase();
  const tokens = normalized.match(/[a-z0-9]+/g) || [];

  const dayMap = {
    mon: "mon",
    monday: "mon",
    tue: "tue",
    tues: "tue",
    tuesday: "tue",
    wed: "wed",
    weds: "wed",
    wednesday: "wed",
    thu: "thu",
    thur: "thu",
    thurs: "thu",
    thursday: "thu",
    fri: "fri",
    friday: "fri",
  };

  let week = fallbackWeek;
  let day = fallbackDay;
  let found = false;

  tokens.forEach((token) => {
    if (token === "1" || token === "2") {
      week = Number(token);
      found = true;
      return;
    }
    const mappedDay = dayMap[token];
    if (mappedDay) {
      day = mappedDay;
      found = true;
    }
  });

  if (!found) {
    return null;
  }

  if (!day || (week !== 1 && week !== 2)) {
    return null;
  }

  return { week, day };
}

function buildLocationOptions(items) {
  const set = new Set();
  items.forEach((item) => {
    if (item.location) {
      item.location.split(" | ").forEach((loc) => set.add(loc.trim()));
    }
  });
  return Array.from(set).sort();
}

function filterByLocations(items, selectedLocations) {
  if (!selectedLocations.length) return items;
  return items.filter((item) => {
    if (!item.location) return false;
    const itemLocs = item.location.split(" | ").map((s) => s.trim());
    return itemLocs.some((loc) => selectedLocations.includes(loc));
  });
}

// Page chrome shared by every page: utility bar, header with top menu, footer, and (on phones) a bottom bar.
const DAY_LONG = { mon: "Monday", tue: "Tuesday", wed: "Wednesday", thu: "Thursday", fri: "Friday" };

function renderChrome(active, week, day) {
  const hasDay = week && day;
  const links = [{ id: "home", label: "Home", href: "index.html" }];
  if (hasDay) {
    links.push(
      { id: "prep", label: "Prep", href: `prep.html?week=${week}&day=${day}` },
      { id: "dry", label: "Dry Store", href: `pick.html?week=${week}&day=${day}&list=dry` },
      { id: "freezer", label: "Freezer", href: `pick.html?week=${week}&day=${day}&list=freezer` }
    );
  }

  const makeNav = (className) => {
    const nav = document.createElement("nav");
    nav.className = className;
    nav.setAttribute("aria-label", "Main");
    links.forEach((item) => {
      const link = document.createElement("a");
      link.href = item.href;
      link.textContent = item.label;
      if (item.id === active) link.className = "active";
      nav.appendChild(link);
    });
    return nav;
  };

  const bar = document.createElement("div");
  bar.className = "utility-bar no-print";
  bar.innerHTML = '<div class="wrap"><span>Staff Caf\u00e9 \u00b7 internal prep tool</span><span id="util-day"></span></div>';
  if (hasDay) bar.querySelector("#util-day").textContent = `Week ${week} \u00b7 ${DAY_LONG[day] || day}`;

  const header = document.createElement("header");
  header.className = "site-header no-print";
  header.innerHTML =
    '<div class="wrap">' +
    '<a class="brand" href="index.html" aria-label="Home">' +
    '<svg class="brand-mark" viewBox="0 0 32 32" aria-hidden="true"><rect width="32" height="32" rx="7" fill="currentColor"/>' +
    '<path d="M9 16.5l4.5 4.5L23 11.5" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg>' +
    '<span class="brand-text"><strong>Staff Caf\u00e9 Prep</strong><small>Summer Menu</small></span></a></div>';
  header.querySelector(".wrap").appendChild(makeNav("top-nav"));

  const footer = document.createElement("footer");
  footer.className = "site-footer no-print";
  footer.innerHTML =
    '<div class="wrap"><strong>Staff Caf\u00e9 Prep</strong> \u00b7 Summer Menu. Internal kitchen tool, not an official website.</div>';

  document.body.insertBefore(header, document.body.firstChild);
  document.body.insertBefore(bar, document.body.firstChild);
  document.body.appendChild(footer);
  if (hasDay) {
    document.body.classList.add("has-nav");
    document.body.appendChild(makeNav("bottom-nav no-print"));
  }
}

// Older name, still used by the prep and pick pages.
function renderNav(active, week, day) {
  renderChrome(active, week, day);
}

// Ticks live in this browser only (localStorage can be blocked, so always try/catch).
function loadTicks(key) {
  try {
    return JSON.parse(localStorage.getItem(key) || "{}");
  } catch (e) {
    return {};
  }
}

function saveTicks(key, ticks) {
  try {
    localStorage.setItem(key, JSON.stringify(ticks));
  } catch (e) {}
}

window.PrepUtils = {
  renderNav,
  renderChrome,
  DAY_LONG,
  loadTicks,
  saveTicks,
  getSuggestedWeekday,
  getQueryParams,
  fetchJSON,
  renderMessage,
  buildLocationOptions,
  filterByLocations,
  parseUserInput,
  getWeekdayOptions,
  filterWeekdayOptions,
};

if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("sw.js").catch(() => {});
  });
}
