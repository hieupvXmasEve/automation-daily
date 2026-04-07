# CLI Flow Wireframe

```text
$ python main.py compare \
    --excel shopee/orders.xlsx \
    --pdf shopee/labels.pdf \
    --formats csv excel pdf

[1/4] Validate input files
  Excel: shopee/orders.xlsx
  PDF  : shopee/labels.pdf

[2/4] Parse sources
  Excel rows       : 478
  Excel orders     : 287
  PDF pages/labels : 38

[3/4] Compare orders
  Matched          : 38
  Mismatch         : 0
  Missing in Excel : 0
  Missing in PDF   : 249

[4/4] Export reports
  CSV   : output/20260406-2331/comparison.csv
  Excel : output/20260406-2331/comparison.xlsx
  PDF   : output/20260406-2331/comparison.pdf

Done.
```

## Notes

- `Missing in PDF` is expected when the PDF contains only a subset of printed labels.
- Terminal output stays brief; detailed records go to exported files.
