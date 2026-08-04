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
  /* adult prose layout ({version}, {slug}) — readable type: body 10pt, headers 12pt+ */
  body {{ font-size: 10pt; line-height: 1.19; }}
  .masthead .forum {{ font-size: 10pt; }}
  h1.title {{ font-size: 18pt; }}
  .dek {{ font-size: 10pt; }}
  h2.sec {{ font-size: 12.5pt; letter-spacing: 0.1em; margin: 5.2pt 0 2.5pt; }}
  h3.subsec {{ font-size: 12pt; margin: 2.5pt 0 1.5pt; }}
  p.lead-item {{ margin: 0 0 3.2pt; text-align: justify; }}
  p.lead-item strong.li {{ color: #1A2D4F; }}
  p.explainer-block {{ margin: 0 0 2.5pt; font-size: 10pt; }}
  .stat-strip {{ margin-bottom: 0; }}
  .stat-card {{ padding: 3.5pt 6pt 4pt; }}
  .stat-num {{ font-size: 20pt; }}
  .stat-num.compact {{ font-size: 15pt; padding-top: 4pt; }}
  .stat-cap {{ font-size: 10pt; line-height: 1.2; }}
  .footline {{ font-size: 10pt; text-transform: none; letter-spacing: 0.02em; padding-top: 4pt; }}
  /* no widow lines; balanced headers, deks, explainers, captions */
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


def render_section(sec: dict, columns: bool = False, tail_html: str = "") -> str:
    out = ["<section>", f"  <h2 class=\"sec\">{typographize(sec['heading'])}</h2>"]
    if columns:
        out.append("  <div class=\"cols\">")
    stat_bullets = [
        (k, t) for k, t in sec["items"]
        if k == "bullet"
        and (m := re.match(r"\*\*(.+?)\*\*\s", t))
        and len(m.group(1)) <= 12
        and not m.group(1).endswith(":")
    ]
    in_list = False
    for kind, text in sec["items"]:
        if kind == "bullet" and (kind, text) in stat_bullets:
            continue
        if kind == "bullet":
            if not in_list:
                out.append("  <ul class=\"plain\">")
                in_list = True
            out.append(f"    <li>{inline_md(no_widow(text))}</li>")
            continue
        if in_list:
            out.append("  </ul>")
            in_list = False
        if kind == "h3":
            out.append(f"  <h3 class=\"subsec\">{typographize(text)}</h3>")
        elif kind == "explainer":
            out.append(f"  <p class=\"explainer-block\">{inline_md(no_widow(text))}</p>")
        else:
            out.append(f"  <p class=\"lead-item\">{inline_md(no_widow(text))}</p>")
    if in_list:
        out.append("  </ul>")
    if stat_bullets:
        out.append(render_stat_strip(stat_bullets))
    if tail_html:
        out.append(tail_html)
    if columns:
        out.append("  </div>")
    out.append("</section>")
    return "\n".join(out)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--brief-dir", required=True)
    parser.add_argument("--file", default="citizen-brief",
                        help="basename of the markdown/html pair (default citizen-brief)")
    parser.add_argument("--footer", default=None,
                        help="footer label; in HTML it renders as a muted line at the end")
    parser.add_argument("--no-masthead", action="store_true",
                        help="omit the THE FORUM masthead block")
    parser.add_argument("--layout", choices=["brief", "glossary", "prose"], default=None,
                        help="brief: justified 2-page front-brief; glossary: two-column "
                             "Term: entries; prose: single-column left-aligned companion "
                             "at Word 1.15 line spacing")
    args = parser.parse_args()
    layout = args.layout or ("brief" if args.file == "citizen-brief" else "glossary")
    brief_dir = Path(args.brief_dir)
    md_path = brief_dir / f"{args.file}.md"
    out_path = brief_dir / f"{args.file}.html"

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
        STYLE_BLOCK.format(version=version, slug=slug)
        + ("\n<style>\n  /* glossary/companion docs: Phase 2 glossary layout — two columns,\n     left-aligned bulleted entries that never split */\n  body { line-height: 1.16; }\n  h2.sec { margin: 4.5pt 0 2pt; }\n  p.lead-item { break-inside: avoid; text-align: left; }\n  .cols { column-count: 2; column-gap: 14pt; }\n  ul.plain { margin: 0; }\n  ul.plain li { break-inside: avoid; margin-bottom: 2.8pt; text-align: left; }\n  ul.plain li strong.li { color: #1A2D4F; }\n  section:not(:first-of-type) { break-before: page; }\n</style>" if layout == "glossary" else "")
        + ("\n<style>\n  /* prose companion: single column, left-aligned, Word-style 1.15 spacing */\n  body { line-height: 1.35; }\n  p.lead-item { break-inside: avoid; text-align: left; margin: 0 0 5pt; }\n  p.explainer-block { margin: 0 0 4pt; }\n  h2.sec { margin: 8pt 0 3pt; }\n</style>" if layout == "prose" else ""),
        "</head>",
        "<body>",
        "",
        "<header class=\"masthead\">",
        *([] if args.no_masthead else [
            "  <div class=\"forum\">The&nbsp;Forum</div>",
            "  <hr class=\"navy-rule\">",
        ]),
        f"  <h1 class=\"title\">{typographize(title)}</h1>",
        f"  <p class=\"dek\">{inline_md(no_widow(dek))}</p>",
        "</header>",
        "",
    ]
    companion = layout == "glossary"
    foot = typographize(footline.rstrip("."))
    organization = meta.get("organization", "The Nevada Forum")
    if month_year:
        foot += f" &middot; {organization} &middot; {month_year}"
    foot_html = f"<p class=\"footline\" style=\"margin-top: 1pt;\">{foot}</p>"
    for i, sec in enumerate(sections):
        tail = foot_html if companion and i == len(sections) - 1 else ""
        parts.append(render_section(sec, columns=companion, tail_html=tail))
        parts.append("")
    if args.footer:
        parts.append(f"<p class=\"footline\" style=\"margin-top: 6pt;\">{typographize(args.footer)}</p>")
        parts.append("")
    elif not companion:
        parts.append(foot_html)
        parts.append("")
    parts.append("</body>")
    parts.append("</html>")

    out_path.write_text("\n".join(parts), encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
