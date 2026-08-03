"""New Hampshire General Court collector adapters (foundation).

Thin, isolated adapters that stand up NH data access without touching the
Nevada / NELIS collectors. See ``docs/nh-data-sources.md`` for what each route
provides and its coverage.

Modules:
  fortiweb      -- solve the gc.nh.gov FortiWeb anti-bot challenge
  gencourt_sql  -- public read-only SQL database (roll calls, docket, sponsors)
  gencourt_web  -- bill detail + full bill text (ASP.NET postback)
  hb2_sections  -- split the HB2 omnibus budget trailer into sections
"""
