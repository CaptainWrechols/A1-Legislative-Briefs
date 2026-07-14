# Collect Nevada water bills (Pass 1)

```bash
pip install -r requirements.txt
export OPENSTATES_API_KEY=your-key-here   # needed for OpenStates
python collectors/pass1_bills.py
```

Output: `sources/nevada/water-scarcity/pass1/bills.json`

| Field | Meaning |
|-------|---------|
| session | OpenStates session id (80–83) |
| identifier | e.g. AB30 |
| title | Bill title |
| abstract | Short summary (NELIS list text and/or OpenStates abstract) |

Cache files in the same folder make re-runs fast. Use `--refresh` only to rebuild from scratch.

## GitHub Actions

Actions → **Collect Nevada Water Bills** → Run workflow.

## Later (Pass 2)

After this list is reviewed: votes, actions, sponsors, enactment — separate small enricher, not in this tree yet.
