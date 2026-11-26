# Bridge Ledger

Find a named bridge in the Halifax and Annapolis County records. Compare dated ratings within one inspection type and open the relevant page of the original release.

[Open Bridge Ledger](https://coolcode.ca/bridgeledger/)

## Try it

<!-- coolcode:guide -->
Anderson Brook Bridge in Annapolis County received a general rating of Good on April 22, 2020 and Fair on April 26, 2023. Its detailed inspections use a separate scale. The place link comes from a unique match on the provincial structure ID.
<!-- /coolcode:guide -->

[Browse bridge inspection histories](https://coolcode.ca/bridgeledger/bridges/) for named structures with two or more qualifying inspection dates on one rating scale. Each profile links to the cited release pages and opens that structure and inspection level in the explorer.

## Sources and interpretation

The 2020 information release supplies entries for the two county prefixes ANN and HFX. The 2023 scan contributes 28 reviewed structures from PDF pages 3, 100 and 103. The first edition has 727 structures and 1,619 distinct inspection records. A case can appear in both releases. Identical inspection details share one history entry with both citations. The CSV preserves a row for each supporting source.

Level 1 uses 1 (Poor), 2 (Fair) and 3 (Good). Level 2 uses 0–9. A Level 2v verification can leave the rating field empty. The comparison uses finalised, comparable dates of the selected inspection type. Unfinished or error-flagged records are labelled, and conflicting ratings on one date are omitted from the comparison. Use the original dated documents to interpret a change. The tool does not assess a bridge’s present condition. Coordinates are joined only on a unique provincial ID, preserving letter suffixes.

[2020 inspection release](https://openinformation.novascotia.ca/api/views/8psg-54u5/files/d1162ffb-acd0-4911-8983-5074ef4c8bd9?download=true&filename=2020-00906-TIR_PublicPackage.pdf) · [2023 inspection release and scale](https://openinformation.novascotia.ca/download/5twe-uvhv/application/pdf#page=2) · [Nova Scotia Structures Database](https://data.novascotia.ca/Roads-Driving-and-Transport/Structures-Database/gs26-c3fm)

## Refresh and verification

Monthly. Install Poppler’s pdftotext program for the 2020 report. The importer verifies both PDFs, reads the reviewed 2023 rows and refreshes the registry join. The retrieval date records the last successful source check in UTC. The coverage on the homepage and in the tool describes the underlying records. A changed archive requiring review or a failed download leaves the previous edition available. The scheduled workflow validates the data, runs the tests and publishes the resulting snapshot. For a manual refresh, run `python3 scripts/refresh.py`.

The interface, selections and CSV exports run locally in the browser. Visiting a source or map link opens the publisher’s site. The offline build uses the checked-in edition. To build and preview it, run the following commands.

```sh
node --test tests/*.test.mjs
python3 -m unittest discover -s tests -v
python3 scripts/build.py
python3 -m http.server 8000 --directory dist
```

The Pages workflow also exercises the tool in Chromium at its project subpath and checks the mobile layout. Update the source sentence in `tool.json` and the marked guide above when changing coverage or interpretation.

<!-- schedule-reliability -->
## Schedule reliability

Public GitHub repositories can have scheduled workflows disabled after 60 days of inactivity. A separate weekly [schedule guard](.github/workflows/schedule-guard.yml) calls GitHub's enable-workflow API for an explicit list of refresh workflows and itself. It can restore workflows disabled for inactivity, preserves manually disabled workflows, and runs independently of collection failures.

This is an interim mitigation, not a scheduling guarantee: GitHub does not document active-workflow renewal as a permanent exemption, and scheduled runs can be delayed or dropped. A scheduler on our own Linux server is the planned independent trigger. The guard does not collect data, create dummy commits, or change source/check timestamps; successful collection and published data freshness still need monitoring.
<!-- /schedule-reliability -->
