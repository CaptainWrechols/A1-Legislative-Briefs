#!/usr/bin/env python3
"""Export a combined "Lege Brief" .docx in the finalized Forum format.

The authoritative format sample is the working-group-approved
``templates/lege-brief/NV1-Water-Lege-Brief-v1.6.docx``. This exporter clones
that file (styles, numbering, theme, settings, footer plumbing) and rebuilds
only ``word/document.xml`` (content) and the footer label, so the output is
format-identical by construction: same fonts/sizes/colors, terracotta ALL-CAPS
section headers, navy subheads, bold-lead paragraphs, the 4-cell stat-card
table, square-bullet policy spotlights, and the two-column bulleted
glossaries with their exact section-break structure.

Source markdown conventions (see briefs/new-hampshire/.../lege-brief.md):

  # Title                         first = document title; later = new title block
  (paragraph after a title)       dek line
  ## Section name                 terracotta header (uppercased)
  *one italic line*               muted section intro
  ### Subhead                     navy subhead
  **Lead.** rest                  bold-navy lead + gray body
  <!--stats-->                    next bullet group becomes the stat table:
  - **289** caption               (exactly 4 items)
  - **HB1 (2025):** text          in spotlight sections: square-bullet item
  - **Term:** definition          in glossary sections: round-bullet entry
  ## Glossary / ## Legislative process glossary
                                  two-column glossary sections (template's
                                  exact sectPr fragments)

Usage:
  python collectors/export_docx_lege_brief.py \
      --source briefs/.../lege-brief.md --out briefs/.../NH1-Housing-Lege-Brief.docx \
      --footer "NH1 Housing Legislative Brief v1.0"
"""

from __future__ import annotations

import argparse
import re
import shutil
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

TEMPLATE = Path("templates/lege-brief/NV1-Water-Lege-Brief-v1.6.docx")

FONT = '<w:rFonts w:ascii="Arial" w:cs="Arial" w:eastAsia="Arial" w:hAnsi="Arial"/>'
BOLD = '<w:b w:val="1"/><w:bCs w:val="1"/>'
ITAL = '<w:i w:val="1"/><w:iCs w:val="1"/>'


def run(text, *, sz, color, bold=False, italic=False):
    extra = (BOLD if bold else '') + (ITAL if italic else '')
    return (f'<w:r><w:rPr>{FONT}{extra}<w:color w:val="{color}"/>'
            f'<w:sz w:val="{sz}"/><w:szCs w:val="{sz}"/><w:rtl w:val="0"/></w:rPr>'
            f'<w:t xml:space="preserve">{escape(text)}</w:t></w:r>')


def para(ppr, runs_xml):
    return f'<w:p>{ppr}{runs_xml}</w:p>'


def spacing(before=None, after=None, line=None):
    a = ''
    if before is not None:
        a += f' w:before="{before}"'
    if after is not None:
        a += f' w:after="{after}"'
    if line is not None:
        a += f' w:line="{line}" w:lineRule="auto"'
    return f'<w:spacing{a}/>'


# paragraph property templates (values transcribed from the NV1 v1.6 file)
P_TITLE = f'<w:pPr>{spacing(after=40, line=276)}<w:rPr/></w:pPr>'
P_DEK = f'<w:pPr>{spacing(after=120, line=276)}<w:rPr/></w:pPr>'
P_H2 = f'<w:pPr>{spacing(before=84, after=36, line=276)}<w:rPr/></w:pPr>'
P_INTRO = f'<w:pPr>{spacing(after=36, line=276)}<w:rPr/></w:pPr>'
P_H3 = f'<w:pPr>{spacing(before=70, after=30, line=276)}<w:rPr/></w:pPr>'
P_BODY = f'<w:pPr>{spacing(after=49, line=276)}<w:rPr/></w:pPr>'
P_POINTER = f'<w:pPr>{spacing(before=40, after=0, line=276)}<w:rPr/></w:pPr>'
P_EMPTY = f'<w:pPr>{spacing(after=120, line=276)}<w:rPr/></w:pPr>'
P_TITLE2 = f'<w:pPr>{spacing(after=40, line=252)}<w:rPr/></w:pPr>'
P_DEK2 = f'<w:pPr>{spacing(after=120, line=254)}<w:rPr/></w:pPr>'
P_H2S = f'<w:pPr>{spacing(before=84, after=36, line=254)}<w:rPr/></w:pPr>'
P_INTROS = f'<w:pPr>{spacing(after=60)}<w:rPr/></w:pPr>'
P_H3S = f'<w:pPr>{spacing(before=70, after=30, line=250)}<w:rPr/></w:pPr>'
P_SPOT = (f'<w:pPr>{spacing(after=80)}<w:ind w:left="200" w:firstLine="0"/>'
          '<w:rPr/></w:pPr>')
P_GLOSS = ('<w:pPr><w:numPr><w:ilvl w:val="0"/><w:numId w:val="2"/></w:numPr>'
           '<w:spacing w:after="0" w:afterAutospacing="0" w:line="276" w:lineRule="auto"/>'
           '<w:ind w:left="720" w:hanging="360"/>'
           f'<w:rPr>{FONT}<w:sz w:val="10"/><w:szCs w:val="10"/></w:rPr></w:pPr>')

LEAD_RE = re.compile(r'^\*\*(.+?)\*\*\s*(.*)$', re.S)


def body_runs(text):
    """Inline **bold** spans become bold navy; everything else gray, sz20."""
    parts = re.split(r'\*\*(.+?)\*\*', text)
    out = []
    for i, part in enumerate(parts):
        if not part:
            continue
        if i % 2:
            out.append(run(part, sz=20, color='1a2d4f', bold=True))
        else:
            out.append(run(part, sz=20, color='444444'))
    return ''.join(out) or run(text, sz=20, color='444444')


def parse_source(md):
    """Yield (kind, payload) blocks from the source markdown."""
    text = md.split('---', 2)[2] if md.startswith('---') else md
    lines = text.split('\n')
    blocks, i = [], 0
    while i < len(lines):
        line = lines[i].rstrip()
        if not line.strip():
            i += 1
            continue
        if line.startswith('<!--stats-->'):
            i += 1
            items = []
            while i < len(lines) and lines[i].strip().startswith('- '):
                items.append(lines[i].strip()[2:].strip())
                i += 1
            blocks.append(('stats', items))
            continue
        if line.startswith('# '):
            blocks.append(('title', line[2:].strip()))
            i += 1
            continue
        if line.startswith('## '):
            blocks.append(('h2', line[3:].strip()))
            i += 1
            continue
        if line.startswith('### '):
            blocks.append(('h3', line[4:].strip()))
            i += 1
            continue
        if line.strip().startswith('- '):
            items = []
            while i < len(lines) and lines[i].strip().startswith('- '):
                item = lines[i].strip()[2:].strip()
                while (i + 1 < len(lines) and lines[i + 1].strip()
                       and not lines[i + 1].strip().startswith(('- ', '#', '*', '<'))):
                    i += 1
                    item += ' ' + lines[i].strip()
                items.append(item)
                i += 1
            blocks.append(('bullets', items))
            continue
        # paragraph (may wrap)
        block = [line.strip()]
        while (i + 1 < len(lines) and lines[i + 1].strip()
               and not lines[i + 1].strip().startswith(('- ', '#', '<!--'))):
            i += 1
            block.append(lines[i].strip())
        p = ' '.join(block)
        if re.fullmatch(r'\*[^*].*\*', p, re.S):
            blocks.append(('intro', p[1:-1]))
        else:
            blocks.append(('para', p))
        i += 1
    return blocks


def build_stat_table(tpl_doc, stats):
    tbl = re.search(r'<w:tbl>.*?</w:tbl>', tpl_doc, re.S).group(0)
    texts = re.findall(r'(<w:t xml:space="preserve">)(.*?)(</w:t>)', tbl, re.S)
    slots = [t for t in texts if t[1].strip()]
    assert len(slots) == 8, f"stat table has {len(slots)} text slots, expected 8"
    new_vals = []
    for it in stats:
        m = LEAD_RE.match(it)
        num, cap = m.group(1), m.group(2)
        new_vals += [num, cap]
    assert len(new_vals) == 8, "stat strip needs exactly 4 items"
    out, idx = tbl, 0
    for (a, old, b) in slots:
        out = out.replace(a + old + b, a + escape(new_vals[idx]) + b, 1)
        idx += 1
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--source', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--footer', required=True)
    args = ap.parse_args()

    md = Path(args.source).read_text(encoding='utf-8')
    blocks = parse_source(md)

    with zipfile.ZipFile(TEMPLATE) as z:
        tpl_doc = z.read('word/document.xml').decode('utf-8')
        footer = z.read('word/footer1.xml').decode('utf-8')

    sectprs = re.findall(r'<w:sectPr.*?</w:sectPr>', tpl_doc, re.S)
    assert len(sectprs) == 5, f"template has {len(sectprs)} sectPr fragments"
    header_xml = tpl_doc[:tpl_doc.index('<w:body>') + len('<w:body>')]

    out, mode, titles_seen = [], 'brief', 0
    glossary_bufs = []       # [(header_text, [entries])]
    cur_gloss = None
    pending_dek = False

    for kind, payload in blocks:
        if kind == 'title':
            titles_seen += 1
            if titles_seen == 1:
                out.append(para(P_TITLE, run(payload, sz=36, color='1a2d4f', bold=True)))
            else:
                mode = 'spotlights'
                out.append(para(P_EMPTY, ''))
                out.append(para(P_EMPTY, ''))
                out.append(para(P_TITLE2, run(payload, sz=36, color='1a2d4f', bold=True)))
            pending_dek = True
        elif kind == 'h2':
            low = payload.lower()
            if low in ('glossary', 'legislative process glossary'):
                mode = 'glossary'
                cur_gloss = (payload.upper(), [])
                glossary_bufs.append(cur_gloss)
            elif mode == 'spotlights':
                out.append(para(P_H2S, run(payload.upper(), sz=25, color='c0392b', bold=True)))
            else:
                out.append(para(P_H2, run(payload.upper(), sz=25, color='c0392b', bold=True)))
        elif kind == 'h3':
            out.append(para(P_H3S if mode == 'spotlights' else P_H3,
                            run(payload, sz=24, color='2e4a78', bold=True)))
        elif kind == 'intro':
            out.append(para(P_INTROS if mode == 'spotlights' else P_INTRO,
                            run(payload, sz=20, color='666666', italic=True)))
        elif kind == 'stats':
            out.append(build_stat_table(tpl_doc, payload))
            out.append(para(P_EMPTY.replace('w:after="120"', 'w:after="40"'), ''))
        elif kind == 'bullets':
            for it in payload:
                m = LEAD_RE.match(it)
                lead, rest = (m.group(1), m.group(2)) if m else ('', it)
                if mode == 'glossary':
                    cur_gloss[1].append(
                        run(lead, sz=20, color='1a2d4f', bold=True)
                        + run(' ' + rest, sz=20, color='444444'))
                else:
                    out.append(para(
                        P_SPOT,
                        run('\u25aa  ', sz=20, color='c0392b')
                        + run(lead + (' ' if rest else ''), sz=20, color='1a2d4f', bold=True)
                        + run(rest, sz=20, color='444444')))
        elif kind == 'para':
            if pending_dek:
                out.append(para(P_DEK2 if mode == 'spotlights' else P_DEK,
                                run(payload, sz=20, color='444444')))
                pending_dek = False
            elif payload.startswith('Full '):
                out.append(para(P_POINTER, run(payload, sz=20, color='666666')))
            else:
                out.append(para(P_BODY, body_runs(payload)))

    # glossaries with the template's exact section-break structure:
    # [sectPr1 1col] HDR entries[:-1] [sectPr2 2col] last [sectPr3 1col]
    # HDR2 entries[:-1] [sectPr4 2col] last [sectPr5 final]
    assert len(glossary_bufs) == 2, "expected two glossary sections"
    out.append(f'<w:p><w:pPr>{sectprs[0]}</w:pPr></w:p>')
    for gi, (hdr, entries) in enumerate(glossary_bufs):
        out.append(para(P_H2S, run(hdr, sz=25, color='c0392b', bold=True)))
        for e in entries[:-1]:
            out.append(para(P_GLOSS, e))
        out.append(f'<w:p><w:pPr>{sectprs[1 + gi * 2]}</w:pPr></w:p>')
        out.append(para(P_GLOSS, entries[-1]))
        if gi == 0:
            out.append(f'<w:p><w:pPr>{sectprs[2]}</w:pPr></w:p>')
    doc = header_xml + ''.join(out) + sectprs[4] + '</w:body></w:document>'

    new_footer = re.sub(r'(<w:t xml:space="preserve">)NV1[^<]*(</w:t>)',
                        r'\g<1>' + escape(args.footer) + r'\g<2>', footer)

    out_path = Path(args.out)
    shutil.copy(TEMPLATE, out_path)
    import subprocess, os
    # rewrite the two members via a fresh zip (zipfile can't replace in place)
    tmp = out_path.with_suffix('.tmp.docx')
    with zipfile.ZipFile(TEMPLATE) as zin, zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            if item.filename == 'word/document.xml':
                zout.writestr(item, doc)
            elif item.filename == 'word/footer1.xml':
                zout.writestr(item, new_footer)
            else:
                zout.writestr(item, zin.read(item.filename))
    os.replace(tmp, out_path)
    print(f"Wrote {out_path} (format cloned from {TEMPLATE.name})")


if __name__ == '__main__':
    main()
