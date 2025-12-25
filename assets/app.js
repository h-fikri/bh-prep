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

window.PrepUtils = {
  getSuggestedWeekday,
  getQueryParams,
  fetchJSON,
  renderMessage,
  buildLocationOptions,
  filterByLocations,
};
