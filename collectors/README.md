# Collectors

One script:

```bash
python collectors/pass1_bills.py
```

Reads `config/issues/nevada-water-scarcity.yaml`, searches NELIS + OpenStates, caches on disk, writes:

`sources/nevada/water-scarcity/pass1/bills.json`

Fields: session, identifier, title, abstract.
