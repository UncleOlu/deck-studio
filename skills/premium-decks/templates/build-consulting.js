// Consulting-register deck builder (references/consulting-grammar.md, storyline.md).
// All content comes from a deck JSON (schema: consulting-deck.schema.json; example:
// consulting-deck.sample.json). Usage: node build-consulting.js deck.json
"use strict";
const path = require("path");
const kit = require("./lib/deck-kit");

const spec = require(path.resolve(process.argv[2] || "./deck.json"));
spec.register = "consulting";
const answerFirst = s => {
  const i = s.slides.findIndex(sl => sl.type === "exec-summary");
  return i >= 0 && i <= 2 ? "" : "the exec-summary slide must be slide 2 or 3 (R4, answer first)";
};
kit.build(spec, [answerFirst]).then(f => console.log("wrote " + f)).catch(e => { console.error(e.message); process.exit(1); });
