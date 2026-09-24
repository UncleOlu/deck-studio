// Banking-register builder: board books and sell-side pitch books (references/banking-pitchbook.md).
// All content comes from a deck JSON (schema: pitchbook.schema.json; example: pitchbook.sample.json).
// Usage: node build-pitchbook.js deck.json
"use strict";
const path = require("path");
const kit = require("./lib/deck-kit");

const spec = require(path.resolve(process.argv[2] || "./deck.json"));
spec.register = "banking";
spec.meta = Object.assign({ label: "Confidential" }, spec.meta || {});
const answerPage = s => {  // board book: valuation summary by slide 4 (after cover + disclaimer); pitch: summary by 3
  const i = s.slides.findIndex(sl => sl.type === "football-field" || sl.type === "exec-summary");
  return i >= 0 && i <= 3 ? "" : "put the answer page (football field or summary) by slide 4 (R4)";
};
const disclaimer = s => (s.kind === "board-book" && !s.slides.some(sl => sl.type === "disclaimer")
  ? "a board book needs a disclaimer slide in your own words" : "");
kit.build(spec, [answerPage, disclaimer]).then(f => console.log("wrote " + f))
  .catch(e => { console.error(e.message); process.exit(1); });
