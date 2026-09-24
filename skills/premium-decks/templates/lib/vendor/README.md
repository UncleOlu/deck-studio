# Vendored JavaScript dependencies

The deck kit runs offline, with no `npm install`. These files are unmodified
copies of the published npm packages; only `package.json` is reduced to the
fields Node needs to resolve them.

| Package | Version | License | File | SHA-256 |
|---|---|---|---|---|
| pptxgenjs | 3.12.0 | MIT (`pptxgenjs/LICENSE`) | `pptxgenjs/dist/pptxgen.cjs.js` | `16adaa60d6ed22ea263786652b6c219750281a5e51cb205be1cf59e0d2eed8ce` |
| jszip | 3.10.2 | MIT or GPL-3.0-or-later, used under MIT (`jszip/LICENSE.markdown`) | `jszip/dist/jszip.min.js` | `7f839b2d4688b845c105ebf5d2f9803075f91ea0fe72bdaac176c3a04dd3d2c1` |

To upgrade: copy the new `dist` file, update the version and hash here, and
rebuild both samples through `scripts/qa-deck.py`.
