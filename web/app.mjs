import {
  byId,
  choices,
  element,
  number,
  table,
  sourceLink,
  downloadCsv,
  loadEdition,
  failed,
} from "./ui.mjs";
import { scopeBridges, rating, comparable } from "./model.mjs";
try {
  const data = await loadEdition("inspection records");
  const catalog = data.bridges.sort(
    (a, b) => a.name.localeCompare(b.name) || a.id.localeCompare(b.id),
  );
  choices("scope", [
    ["all", "All covered structures"],
    ["both", "Includes 2023 transcription"],
    ["HFX", "Halifax County"],
    ["ANN", "Annapolis County"],
  ]);
  choices("level", [
    ["1", "Level 1 · general"],
    ["2", "Level 2 · detailed"],
    ["2v", "Level 2v · verification"],
    ["all", "All inspection types"],
  ]);
  const named = new Map(catalog.map((b) => [b.id, b]));
  let csv = [];
  function render() {
    const b = named.get(byId("bridge").value),
      level = byId("level").value;
    byId("location").replaceChildren();
    byId("csv").disabled = !b;
    if (!b) {
      byId("structure").textContent = "";
      byId("finding").textContent =
        "No matching structure in this edition. Try a shorter name or a different scope.";
      byId("visits").replaceChildren();
      return;
    }
    byId("structure").textContent = b.name + " · " + b.id;
    if (b.location) {
      const [lat, lon] = b.location;
      byId("location").append(
        sourceLink(
          "Map the registry location",
          "https://www.openstreetmap.org/?mlat=" +
            lat +
            "&mlon=" +
            lon +
            "#map=15/" +
            lat +
            "/" +
            lon,
        ),
        " · Provincial ID " +
          b.registryId +
          " · " +
          lat.toFixed(4) +
          ", " +
          lon.toFixed(4),
      );
    } else
      byId("location").textContent =
        "No unique coordinate match in the provincial registry.";
    const rows = b.visits.filter((r) => level === "all" || r.level === level);
    const comparableRows = comparable(rows, level),
      a = comparableRows[0],
      z = comparableRows.at(-1);
    if (level === "all")
      byId("finding").textContent =
        "Choose an inspection type to compare ratings on its own scale.";
    else if (level === "2v")
      byId("finding").textContent =
        "Verification entries refer to an earlier Level 2 inspection. Its rating can be read in the Level 2 history.";
    else if (a && z && a !== z)
      byId("finding").textContent =
        "Finalised Level " +
        level +
        " · " +
        a.date +
        " was " +
        rating(level, a.rating) +
        ". On " +
        z.date +
        " the recorded rating was " +
        rating(level, z.rating) +
        ".";
    else
      byId("finding").textContent = a
        ? "One distinct date has a finalised numerical rating for this inspection type."
        : "This selection has no finalised numerical rating in the included records.";
    table(
      "visits",
      [
        "Inspection date",
        "Type",
        "Recorded rating",
        "Record status",
        "Released evidence",
      ],
      rows.map((r) => {
        const sources = element("span");
        for (const [i, e] of r.evidence.entries()) {
          if (i) sources.append(" · ");
          sources.append(
            sourceLink(
              e.release + " PDF p. " + e.page,
              data.sources[e.release] + "#page=" + e.page,
            ),
          );
        }
        const state =
          (r.finalised ? "Finalised" : "Unfinished") +
          (r.evidence.some((e) => e.inError) ? " · flagged in error" : "");
        return [
          r.date,
          "Level " + r.level,
          rating(r.level, r.rating),
          state,
          sources,
        ];
      }),
    );
    csv = [
      [
        "structure",
        "name",
        "date",
        "level",
        "rating",
        "finalised",
        "release",
        "created_in_error",
        "source_page",
      ],
    ];
    for (const row of rows)
      for (const e of row.evidence)
        csv.push([
          b.id,
          b.name,
          row.date,
          row.level,
          row.rating,
          row.finalised,
          e.release,
          e.inError,
          data.sources[e.release] + "#page=" + e.page,
        ]);
    byId("csv").disabled = rows.length === 0;
  }
  function filter(preferred = byId("bridge").value) {
    const found = scopeBridges(
      catalog,
      byId("search").value,
      byId("scope").value,
    );
    choices(
      "bridge",
      found.map((b) => [b.id, b.name + " · " + b.id]),
    );
    if (found.some((b) => b.id === preferred)) byId("bridge").value = preferred;
    byId("matchcount").textContent =
      number(found.length) + " of " + number(catalog.length) + " structures";
    render();
  }
  byId("search").oninput = () => filter();
  byId("scope").onchange = () => filter();
  byId("bridge").onchange = render;
  byId("level").onchange = render;
  byId("csv").onclick = () => downloadCsv("bridge-inspections.csv", csv);
  const params = new URLSearchParams(location.search);
  if (["1", "2", "2v", "all"].includes(params.get("level"))) byId("level").value = params.get("level");
  filter(params.get("id") || "ANN002");
} catch {
  failed();
}
