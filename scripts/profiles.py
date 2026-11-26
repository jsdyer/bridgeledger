"""Compare dated inspections only within the same provincial rating scale."""
from collections import defaultdict
from html import escape
import json
from urllib.parse import urlencode
from result_pages import link, publish, slug, table


def comparable(visits, level):
    by_date = defaultdict(list)
    for row in visits:
        if (row["level"] == level and row["finalised"] and row["rating"] is not None
                and row["evidence"] and not any(e["inError"] for e in row["evidence"])):
            by_date[row["date"]].append(row)
    return [group[0] for _, group in sorted(by_date.items())
            if len({row["rating"] for row in group}) == 1]


def rating(level, value):
    if level == "1":
        return {1: "1 (Poor)", 2: "2 (Fair)", 3: "3 (Good)"}[value]
    return f"{value} out of 9"


def publish_profiles(stage, tool):
    data = json.loads((stage / "data/edition.json").read_text())
    records = []
    for bridge in data["bridges"]:
        identifier, name = bridge["id"], bridge["name"]
        histories = {level: comparable(bridge["visits"], level) for level in ("1", "2")}
        histories = {level: rows for level, rows in histories.items() if len(rows) >= 2}
        if not histories:
            continue
        county = {"HFX": "Halifax County", "ANN": "Annapolis County"}[identifier[:3]]
        level, rows = next(iter(histories.items()))
        first, last = rows[0], rows[-1]
        intro = (f"In {county}, Nova Scotia Public Works recorded a Level {level} rating of "
                 f"{rating(level, first['rating'])} at {name} on {first['date']} and "
                 f"{rating(level, last['rating'])} on {last['date']}.")
        body = ""
        for level, visits in histories.items():
            caption = "General inspections (Level 1)" if level == "1" else "Detailed inspections (Level 2)"
            body += table(caption, ["Inspection date", "Finalised rating"],
                          [(row["date"], rating(level, row["rating"])) for row in reversed(visits)])
            query = urlencode({"id": identifier, "level": level})
            body += '<p>' + link(tool["url"] + "?" + query, f"Open the Level {level} inspection history for {name}") + '</p>'
        pages = sorted({(e["release"], e["page"]) for visits in histories.values() for row in visits for e in row["evidence"]})
        body += ('<h2>Inspection records</h2><p>The table uses finalised ratings from distinct dates on the same scale. '
                 'It excludes error-flagged records and dates with conflicting ratings. These observations describe '
                 'the bridge at its historical inspection dates.</p><p>'
                 + " · ".join(link(data["sources"][str(release)] + f"#page={page}", f"{release} provincial release, p. {page}")
                              for release, page in pages)
                 + f'</p><p>Structure {escape(identifier)}. Source files checked {escape(data["retrieved"])}.</p>')
        if identifier.startswith("HFX"):
            body += '<p>' + link('/halifaxtimelens/', 'Explore historical aerial photographs of Halifax') + '</p>'
        title = f"{name} ({identifier}) inspection history"
        records.append((slug(identifier), f"{name} · {identifier}", title, intro, body))
    publish(stage, tool, "bridges", "Historical Nova Scotia bridge inspections by structure",
            "Choose a bridge in Halifax or Annapolis County with finalised ratings on at least two dates on the same inspection scale.", records)
