#!/usr/bin/env python3
"""Render the citizen front brief markdown into the Phase 2 print HTML shell.

Produces {BRIEF_DIR}/citizen-brief.html from {BRIEF_DIR}/citizen-brief.md,
using the same classes/modules as the packaged v1 briefs (masthead, terracotta
h2.sec headers, navy-bar stat strip, lead-item prose) plus the v2 additions:
h3.subsec subsection headers and p.explainer-block section explainers.

  python collectors/export_brief_html.py --brief-dir briefs/nevada/water-scarcity/citizen-v2
"""

from __future__ import annotations

import argparse
import html as html_mod
import re
from pathlib import Path

STYLE_BLOCK = """<style>
  /* adult prose layout ({version}, {slug}) */
  body {{ font-size: 8.5pt; line-height: 1.25; }}
  h2.sec {{ margin: 5pt 0 2.5pt; }}
  h3.subsec {{ margin: 2.5pt 0 1.5pt; }}
  p.lead-item {{ margin: 0 0 3.2pt; text-align: justify; }}
  p.lead-item strong.li {{ color: #1A2D4F; }}
  p.explainer-block {{ margin: 0 0 3pt; font-size: 8.1pt; }}
  .stat-strip {{ margin-bottom: 2pt; }}
  .stat-card {{ padding: 3pt 5pt 3.5pt; }}
  .stat-num {{ font-size: 18pt; }}
  .stat-num.compact {{ font-size: 13.5pt; padding-top: 3.5pt; }}
  /* v3 polish: no widow lines; balanced headers, deks, explainers, captions */
  h1.title, h2.sec, h3.subsec, .stat-cap, .dek, p.explainer-block {{ text-wrap: balance; }}
  p.lead-item {{ text-wrap: pretty; }}
</style>"""


def parse_front_matter(text: str) -> tuple[dict, str]:
    meta: dict[str, str] = {}
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            for line in text[3:end].splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    meta[k.strip()] = v.strip().strip('"')
            text = text[end + 4:].lstrip("\n")
    return meta, text


def typographize(text: str) -> str:
    """HTML-escape, then apply the house entity conventions."""
    t = html_mod.escape(text, quote=False)
    t = re.sub(r"(\w)'(\w)", r"\1&rsquo;\2", t)
    t = re.sub(r"(\w)'(\s|$|[,.;:)])", r"\1&rsquo;\2", t)
    t = re.sub(r'"([^"]*)"', r"&ldquo;\1&rdquo;", t)
    t = t.replace("\u2019", "&rsquo;").replace("\u2018", "&lsquo;")
    t = t.replace("\u201c", "&ldquo;").replace("\u201d", "&rdquo;")
    t = t.replace("\u2013", "&ndash;").replace("\u2014", "&mdash;")
    t = t.replace("\u00b7", "&middot;")
    t = t.replace("\u00a0", "&nbsp;")
    return t


def no_widow(text: str) -> str:
    """Glue the final words together with non-breaking spaces so the last
    line of a paragraph never holds fewer than three words (the glued run
    is kept short so justification gaps stay invisible)."""
    m = re.search(r"(\S+) (\S+) (\S+)$", text)
    if m and sum(len(g) for g in m.groups()) <= 22:
        return text[: m.start()] + "\u00a0".join(m.groups())
    m = re.search(r"(\S+) (\S+)$", text)
    if m and len(m.group(1)) + len(m.group(2)) <= 24:
        return text[: m.start()] + m.group(1) + "\u00a0" + m.group(2)
    return text


def inline_md(text: str) -> str:
    return re.sub(r"\*\*(.+?)\*\*", r'<strong class="li">\1</strong>', typographize(text))


def is_explainer(line: str) -> bool:
    s = line.strip()
    return (
        len(s) > 2
        and s.startswith("*")
        and s.endswith("*")
        and not s.startswith("**")
        and not s.endswith("**")
    )


def parse_body(text: str):
    lines = [l.rstrip() for l in text.splitlines()]
    title = ""
    dek = ""
    sections: list[dict] = []
    footline = ""
    current = None
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("# ") and not title:
            title = line[2:].strip()
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines) and not lines[j].startswith("#"):
                dek = lines[j].strip()
                i = j
        elif line.startswith("### ") and current is not None:
            current["items"].append(("h3", line[4:].strip()))
        elif line.startswith("## "):
            current = {"heading": line[3:].strip(), "items": []}
            sections.append(current)
        elif line.strip() == "---":
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            footline = " ".join(l.strip() for l in lines[j:] if l.strip())
            break
        elif line.strip().startswith("- ") and current is not None:
            current["items"].append(("bullet", line.strip()[2:].strip()))
        elif is_explainer(line) and current is not None:
            current["items"].append(("explainer", line.strip()[1:-1].strip()))
        elif line.strip() and current is not None:
            block = [line.strip()]
            while (
                i + 1 < len(lines)
                and lines[i + 1].strip()
                and not lines[i + 1].startswith(("#", "- "))
                and lines[i + 1].strip() != "---"
                and not is_explainer(lines[i + 1])
            ):
                i += 1
                block.append(lines[i].strip())
            current["items"].append(("para", " ".join(block)))
        i += 1
    return title, dek, sections, footline


def render_stat_strip(items) -> str:
    cards = []
    for kind, text in items:
        if kind != "bullet":
            continue
        m = re.match(r"\*\*(.+?)\*\*\s*(.*)", text)
        if not m:
            continue
        num, caption = m.group(1), m.group(2).lstrip("—-– ").strip()
        cls = "stat-num compact" if len(num) > 4 else "stat-num"
        cards.append(
            "    <div class=\"stat-card\">\n"
            f"      <div class=\"{cls}\">{typographize(num).replace(' ', '&nbsp;')}</div>\n"
            f"      <div class=\"stat-cap\">{inline_md(caption)}</div>\n"
            "    </div>"
        )
    return "  <div class=\"stat-strip\">\n" + "\n".join(cards) + "\n  </div>"


def render_section(sec: dict) -> str:
    out = ["<section>", f"  <h2 class=\"sec\">{typographize(sec['heading'])}</h2>"]
    if sec["heading"].strip().lower().startswith("key numbers"):
        for kind, text in sec["items"]:
            if kind == "explainer":
                out.append(f"  <p class=\"explainer-block\">{inline_md(text)}</p>")
        out.append(render_stat_strip(sec["items"]))
    else:
        for kind, text in sec["items"]:
            if kind == "h3":
                out.append(f"  <h3 class=\"subsec\">{typographize(text)}</h3>")
            elif kind == "explainer":
                out.append(f"  <p class=\"explainer-block\">{inline_md(no_widow(text))}</p>")
            else:
                out.append(f"  <p class=\"lead-item\">{inline_md(no_widow(text))}</p>")
    out.append("</section>")
    return "\n".join(out)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--brief-dir", required=True)
    args = parser.parse_args()
    brief_dir = Path(args.brief_dir)
    md_path = brief_dir / "citizen-brief.md"
    out_path = brief_dir / "citizen-brief.html"

    meta, body = parse_front_matter(md_path.read_text(encoding="utf-8"))
    title, dek, sections, footline = parse_body(body)
    version = meta.get("version", "citizen-v2.0")
    status = meta.get("status", "READY FOR HUMAN REVIEW")
    date = meta.get("date", "")
    slug = brief_dir.parent.name

    month_year = ""
    m = re.match(r"(\d{4})-(\d{2})", date)
    if m:
        months = ["January", "February", "March", "April", "May", "June", "July",
                  "August", "September", "October", "November", "December"]
        month_year = f"{months[int(m.group(2)) - 1]} {m.group(1)}"

    parts = [
        "<!DOCTYPE html>",
        "<html lang=\"en\">",
        "<head>",
        "<meta charset=\"utf-8\">",
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">",
        f"<meta name=\"review-status\" content=\"{status}\">",
        f"<!-- {version} tone/format revision · {date} · status: {status} -->",
        f"<title>{typographize(title)}</title>",
        "<link rel=\"stylesheet\" href=\"citizen-brief-print.css\">",
        STYLE_BLOCK.format(version=version, slug=slug),
        "</head>",
        "<body>",
        "",
        "<header class=\"masthead\">",
        "  <div class=\"forum\">The&nbsp;Forum</div>",
        "  <hr class=\"navy-rule\">",
        f"  <h1 class=\"title\">{typographize(title)}</h1>",
        f"  <p class=\"dek\">{inline_md(no_widow(dek))}</p>",
        "</header>",
        "",
    ]
    for sec in sections:
        parts.append(render_section(sec))
        parts.append("")
    foot = typographize(footline.rstrip("."))
    if month_year:
        foot += f" &middot; The Nevada Forum &middot; {month_year}"
    parts.append(f"<p class=\"footline\" style=\"margin-top: 2pt;\">{foot}</p>")
    parts.append("")
    parts.append("</body>")
    parts.append("</html>")

    out_path.write_text("\n".join(parts), encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
