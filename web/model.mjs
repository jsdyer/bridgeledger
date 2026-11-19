export function scopeBridges(bridges, query, scope) {
  const words = query.toLowerCase().trim().split(/\s+/).filter(Boolean);
  return bridges.filter((b) => {
    const text = [b.id, b.name, b.registryId || ""].join(" ").toLowerCase();
    return (
      words.every((w) => text.includes(w)) &&
      (scope === "all" ||
        (scope === "both"
          ? b.visits.some((r) => r.evidence.some((e) => e.release === 2023))
          : b.id.startsWith(scope)))
    );
  });
}
export function rating(level, value) {
  if (value === null)
    return level === "2v" ? "No repeated rating" : "No rating entered";
  if (level === "1")
    return (
      value +
      " · " +
      ({ 1: "Poor", 2: "Fair", 3: "Good" }[value] ?? "Unclassified")
    );
  return value + " / 9";
}
export function comparable(visits, level) {
  const rows = visits.filter(
    (v) =>
      v.level === level &&
      v.finalised &&
      v.rating != null &&
      !v.evidence.some((e) => e.inError === true),
  );
  const dates = new Map();
  for (const item of rows) {
    if (dates.has(item.date) && dates.get(item.date)?.rating !== item.rating)
      dates.set(item.date, null);
    else if (!dates.has(item.date)) dates.set(item.date, item);
  }
  return [...dates.values()]
    .filter(Boolean)
    .sort((a, b) => a.date.localeCompare(b.date));
}
