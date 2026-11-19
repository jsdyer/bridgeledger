import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
const edition = JSON.parse(
  readFileSync(new URL("../web/data/edition.json", import.meta.url), "utf8"),
);
import { scopeBridges, rating, comparable } from "../web/model.mjs";
test("the Anderson Brook entries compare within their inspection type", () => {
  const [b] = scopeBridges(edition.bridges, "ANN00002", "both");
  assert.equal(b.id, "ANN002");
  assert.deepEqual(
    comparable(b.visits, "1").map((r) => r.rating),
    [3, 2],
  );
  assert.equal(rating("1", 2), "2 · Fair");
  assert.equal(rating("2", 2), "2 / 9");
  assert.equal(rating("2v", null), "No repeated rating");
  assert.ok(b.visits.some((v) => v.evidence.length === 2));
});
test("unfinalised, flagged and contradictory dates stay out of comparisons", () => {
  const row = (date, rating, finalised = true, inError = false) => ({
    date,
    rating,
    level: "1",
    finalised,
    evidence: [{ inError }],
  });
  assert.deepEqual(
    comparable(
      [
        row("2020-01-01", 3),
        row("2020-01-01", 2),
        row("2022-01-01", 1, false),
        row("2023-01-01", 2, true, true),
      ],
      "1",
    ),
    [],
  );
  const invalidated = row("2020-01-02", 3);
  invalidated.evidence = [{ inError: null }, { inError: true }];
  assert.deepEqual(comparable([invalidated], "1"), []);
  assert.equal(
    scopeBridges(edition.bridges, "shad bay", "HFX")[0].id,
    "HFX146",
  );
});
