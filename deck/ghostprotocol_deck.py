#!/usr/bin/env python3
"""
GhostProtocol — Hack-to-Ween 2026 pitch deck generator.

Run:
    python -m pip install python-pptx
    python ghostprotocol_deck.py

Output:
    GhostProtocol_HackToWeen_2026.pptx

The deck is intentionally self-contained: no images, icon packs, or network calls.
Everything is drawn with native PowerPoint shapes so the file stays editable.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable, Sequence

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.dml import MSO_LINE_DASH_STYLE
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.oxml.xmlchemy import OxmlElement
from pptx.util import Inches, Pt


# ---------------------------------------------------------------------------
# EDIT THESE BEFORE SUBMISSION
# ---------------------------------------------------------------------------
TEAM_NAME = "NullVoid"
TEAM_MEMBERS = "Hariprasath  ·  Dhanush S  ·  Jaidev S P  ·  Kalaiyarasan P"
COLLEGE = "AWS Student Builder Group  ·  IIT Jodhpur"
# Set to True only after you have a real public demo and GitHub repo.
PUBLIC_LINKS = False
DEMO_URL = "https://ghostprotocol-demo.vercel.app"
GITHUB_URL = "https://github.com/your-team/ghostprotocol"
CONTACT = "Contact via Unstop team profile"

OUTPUT_FILE = "GhostProtocol_HackToWeen_2026.pptx"


# ---------------------------------------------------------------------------
# Palette + type
# ---------------------------------------------------------------------------
BG = RGBColor(15, 17, 23)          # requested #0F1117
OBSIDIAN = RGBColor(13, 15, 18)    # #0D0F12
PANEL = RGBColor(20, 24, 31)
PANEL_2 = RGBColor(25, 30, 39)
BORDER = RGBColor(43, 49, 61)
GRID = RGBColor(31, 36, 46)
WHITE = RGBColor(248, 250, 252)
MUTED = RGBColor(148, 163, 184)
DIM = RGBColor(100, 116, 139)
ORANGE = RGBColor(249, 115, 22)    # #F97316
PURPLE = RGBColor(168, 85, 247)    # #A855F7
GREEN = RGBColor(34, 197, 94)
RED = RGBColor(239, 68, 68)
SKY = RGBColor(56, 189, 248)

FONT_DISPLAY = "Bahnschrift"
FONT_BODY = "Segoe UI"
FONT_MONO = "Consolas"

SLIDE_W = 13.333
SLIDE_H = 7.5


# ---------------------------------------------------------------------------
# Low-level drawing helpers
# ---------------------------------------------------------------------------
def _hex(rgb: RGBColor) -> str:
    return str(rgb)


def set_alpha(shape, pct: int) -> None:
    """Apply transparency to a solid-filled shape. pct is 0-100 opacity."""
    sp_pr = shape._element.spPr
    solid = sp_pr.find(qn("a:solidFill"))
    if solid is None:
        return
    srgb = solid.find(qn("a:srgbClr"))
    if srgb is None:
        return
    for old in srgb.findall(qn("a:alpha")):
        srgb.remove(old)
    alpha = OxmlElement("a:alpha")
    alpha.set("val", str(int(pct * 1000)))
    srgb.append(alpha)


def add_glow(shape, color: RGBColor, radius_pt: float = 12, opacity_pct: int = 30) -> None:
    sp_pr = shape._element.spPr
    effect = sp_pr.find(qn("a:effectLst"))
    if effect is None:
        effect = OxmlElement("a:effectLst")
        sp_pr.append(effect)
    glow = OxmlElement("a:glow")
    glow.set("rad", str(int(radius_pt * 12700)))
    srgb = OxmlElement("a:srgbClr")
    srgb.set("val", _hex(color))
    alpha = OxmlElement("a:alpha")
    alpha.set("val", str(int(opacity_pct * 1000)))
    srgb.append(alpha)
    glow.append(srgb)
    effect.append(glow)


def add_shadow(shape, color: RGBColor = RGBColor(0, 0, 0), blur_pt: float = 18, dist_pt: float = 4,
               opacity_pct: int = 30) -> None:
    sp_pr = shape._element.spPr
    effect = sp_pr.find(qn("a:effectLst"))
    if effect is None:
        effect = OxmlElement("a:effectLst")
        sp_pr.append(effect)
    shadow = OxmlElement("a:outerShdw")
    shadow.set("blurRad", str(int(blur_pt * 12700)))
    shadow.set("dist", str(int(dist_pt * 12700)))
    shadow.set("dir", "5400000")
    shadow.set("algn", "ctr")
    shadow.set("rotWithShape", "0")
    srgb = OxmlElement("a:srgbClr")
    srgb.set("val", _hex(color))
    alpha = OxmlElement("a:alpha")
    alpha.set("val", str(int(opacity_pct * 1000)))
    srgb.append(alpha)
    shadow.append(srgb)
    effect.append(shadow)


def rect(slide, x, y, w, h, fill=PANEL, line=None, radius=0.06, glow=None,
         shadow=False, dash=None, alpha=None):
    shp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    shp.adjustments[0] = radius
    shp.fill.solid()
    shp.fill.fore_color.rgb = fill
    if alpha is not None:
        set_alpha(shp, alpha)
    if line is None:
        shp.line.fill.background()
    else:
        shp.line.color.rgb = line
        shp.line.width = Pt(0.8)
        if dash:
            shp.line.dash_style = dash
    shp.shadow.inherit = False
    if glow:
        add_glow(shp, glow, 16, 24)
    if shadow:
        add_shadow(shp)
    return shp


def oval(slide, x, y, w, h, fill=PANEL, line=None, alpha=None, glow=None, line_width=0.8):
    shp = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x), Inches(y), Inches(w), Inches(h))
    if fill is None:
        shp.fill.background()
    else:
        shp.fill.solid()
        shp.fill.fore_color.rgb = fill
        if alpha is not None:
            set_alpha(shp, alpha)
    if line is None:
        shp.line.fill.background()
    else:
        shp.line.color.rgb = line
        shp.line.width = Pt(line_width)
    shp.shadow.inherit = False
    if glow:
        add_glow(shp, glow, 18, 25)
    return shp


def line(slide, x1, y1, x2, y2, color=BORDER, width=0.8, dash=None, arrow=False):
    conn = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    conn.line.color.rgb = color
    conn.line.width = Pt(width)
    if dash:
        conn.line.dash_style = dash
    if arrow:
        ln = conn.line._get_or_add_ln()
        tail = OxmlElement("a:tailEnd")
        tail.set("type", "triangle")
        tail.set("w", "med")
        tail.set("len", "med")
        ln.append(tail)
    return conn


def _style_run(run, size, color, bold=False, font=FONT_BODY, italic=False, spc=0.0):
    run.font.name = font
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    if spc:
        run.font._rPr.set("spc", str(int(spc * 100)))


def text(slide, value, x, y, w, h, size=12, color=WHITE, bold=False, font=FONT_BODY,
         align=PP_ALIGN.LEFT, valign=MSO_ANCHOR.TOP, line_spacing=1.0,
         margins=(0, 0, 0, 0), spc=0.0, italic=False, opacity=None):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.auto_size = None
    tf.margin_left = Inches(margins[0])
    tf.margin_right = Inches(margins[1])
    tf.margin_top = Inches(margins[2])
    tf.margin_bottom = Inches(margins[3])
    tf.vertical_anchor = valign
    for i, raw in enumerate(str(value).split("\n")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = line_spacing
        r = p.add_run()
        r.text = raw
        _style_run(r, size, color, bold=bold, font=font, italic=italic, spc=spc)
        if opacity is not None:
            r.font.color.rgb = color
    return box


def rich_text(slide, runs, x, y, w, h, size=12, align=PP_ALIGN.LEFT,
              valign=MSO_ANCHOR.TOP, line_spacing=1.0, margins=(0, 0, 0, 0)):
    """runs: iterable of (text, kwargs). kwargs can override size/color/bold/font/spc."""
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.auto_size = None
    tf.margin_left = Inches(margins[0])
    tf.margin_right = Inches(margins[1])
    tf.margin_top = Inches(margins[2])
    tf.margin_bottom = Inches(margins[3])
    tf.vertical_anchor = valign
    p = tf.paragraphs[0]
    p.alignment = align
    p.line_spacing = line_spacing
    for value, opts in runs:
        r = p.add_run()
        r.text = value
        _style_run(
            r,
            opts.get("size", size),
            opts.get("color", WHITE),
            bold=opts.get("bold", False),
            font=opts.get("font", FONT_BODY),
            italic=opts.get("italic", False),
            spc=opts.get("spc", 0.0),
        )
    return box


def bullets(slide, items: Sequence[str], x, y, w, h, size=9, color=MUTED,
            bullet_color=ORANGE, font=FONT_BODY, line_spacing=1.08,
            space_after=4, bullet_char="▸"):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.auto_size = None
    tf.margin_left = 0
    tf.margin_right = 0
    tf.margin_top = 0
    tf.margin_bottom = 0
    tf.vertical_anchor = MSO_ANCHOR.TOP
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.line_spacing = line_spacing
        p.space_after = Pt(space_after)
        p_pr = p._p.get_or_add_pPr()
        p_pr.set("marL", str(Inches(0.17)))
        p_pr.set("indent", str(-Inches(0.17)))
        bu_clr = OxmlElement("a:buClr")
        srgb = OxmlElement("a:srgbClr")
        srgb.set("val", _hex(bullet_color))
        bu_clr.append(srgb)
        bu_font = OxmlElement("a:buFont")
        bu_font.set("typeface", "Arial")
        bu_char = OxmlElement("a:buChar")
        bu_char.set("char", bullet_char)
        p_pr.append(bu_clr)
        p_pr.append(bu_font)
        p_pr.append(bu_char)
        r = p.add_run()
        r.text = item
        _style_run(r, size, color, font=font)
    return box


def shape_text(shape, value, size=8, color=WHITE, bold=True, font=FONT_BODY,
               align=PP_ALIGN.CENTER, margins=(0.02, 0.02, 0.01, 0.01)):
    tf = shape.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.auto_size = None
    tf.margin_left = Inches(margins[0])
    tf.margin_right = Inches(margins[1])
    tf.margin_top = Inches(margins[2])
    tf.margin_bottom = Inches(margins[3])
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = align
    r = p.add_run()
    r.text = value
    _style_run(r, size, color, bold=bold, font=font)
    return shape


def pill(slide, value, x, y, w, h, fill=PANEL_2, line=BORDER, color=MUTED,
         size=7, bold=True, font=FONT_BODY):
    shp = rect(slide, x, y, w, h, fill=fill, line=line, radius=0.5)
    return shape_text(shp, value, size=size, color=color, bold=bold, font=font)


def icon_badge(slide, symbol, x, y, d=0.45, fill=PANEL_2, line=BORDER,
               color=ORANGE, size=12):
    shp = oval(slide, x, y, d, d, fill=fill, line=line)
    shape_text(shp, symbol, size=size, color=color, bold=True)
    return shp


def add_logo(slide, x=0.72, y=0.34, scale=1.0):
    # A tiny geometric ghost: body, three skirt bumps, two eyes.
    d = 0.23 * scale
    body = rect(slide, x, y, d, d * 1.08, fill=ORANGE, line=None, radius=0.45)
    add_glow(body, ORANGE, 8, 18)
    for i in range(3):
        oval(slide, x + d * (0.10 + i * 0.30), y + d * 0.94, d * 0.27, d * 0.27, fill=ORANGE, line=None)
    for i in range(2):
        oval(slide, x + d * (0.28 + i * 0.30), y + d * 0.34, d * 0.10, d * 0.13, fill=BG, line=None)
    text(slide, "GHOSTPROTOCOL", x + d + 0.12, y - 0.015, 2.0, 0.20,
         size=8.2, color=WHITE, bold=True, font=FONT_DISPLAY, spc=1.1)
    text(slide, "ZOMBIE CREDENTIAL & PHISHING EXORCIST", x + d + 0.12, y + 0.18, 2.8, 0.15,
         size=4.8, color=DIM, bold=True, font=FONT_BODY, spc=0.9)


def add_footer(slide):
    line(slide, 0.72, 7.03, 12.61, 7.03, color=RGBColor(29, 34, 43), width=0.6)
    text(slide, "GhostProtocol  ·  Hack-to-Ween 2026", 0.72, 7.10, 4.2, 0.18,
         size=6.4, color=DIM, font=FONT_BODY)
    text(slide, "AWS Student Builder Group  ·  IIT Jodhpur", 8.0, 7.10, 4.61, 0.18,
         size=6.4, color=DIM, font=FONT_BODY, align=PP_ALIGN.RIGHT)


def background(slide, page=None, accent=ORANGE):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = BG

    # Atmospheric glows. These are deliberately subtle so text stays readable.
    oval(slide, 10.2, -2.8, 6.0, 6.0, fill=PURPLE, line=None, alpha=6)
    oval(slide, -2.4, 5.3, 5.4, 5.4, fill=ORANGE, line=None, alpha=5)
    oval(slide, 4.7, 2.4, 4.2, 4.2, fill=accent, line=None, alpha=2)

    # Blueprint grid.
    for x in [i * 0.75 for i in range(1, 18)]:
        line(slide, x, 0, x, SLIDE_H, color=GRID, width=0.35)
    for y in [i * 0.75 for i in range(1, 10)]:
        line(slide, 0, y, SLIDE_W, y, color=GRID, width=0.35)

    # Corner ticks.
    for x, y, dx, dy in [(0.55, 0.55, 0.18, 0), (0.55, 0.55, 0, 0.18),
                         (12.78, 6.95, -0.18, 0), (12.78, 6.95, 0, -0.18)]:
        line(slide, x, y, x + dx, y + dy, color=RGBColor(55, 62, 76), width=0.7)


def content_slide(prs, kicker, title, subtitle, page, accent=ORANGE):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    background(slide, page=page, accent=accent)
    add_logo(slide)
    text(slide, f"{page:02d} / 08", 11.82, 0.40, 0.80, 0.20,
         size=6.8, color=DIM, bold=True, font=FONT_MONO, align=PP_ALIGN.RIGHT)
    text(slide, kicker, 0.72, 0.80, 8.0, 0.20, size=7.5, color=accent,
         bold=True, font=FONT_BODY, spc=1.5)
    text(slide, title, 0.72, 1.00, 11.7, 0.52, size=29, color=WHITE,
         bold=True, font=FONT_DISPLAY, line_spacing=0.95)
    text(slide, subtitle, 0.72, 1.57, 11.5, 0.30, size=9.5, color=MUTED,
         font=FONT_BODY, line_spacing=1.0)
    add_footer(slide)
    return slide


def notes(slide, value):
    slide.notes_slide.notes_text_frame.text = value


# ---------------------------------------------------------------------------
# Slide 1 — Title
# ---------------------------------------------------------------------------
def slide_title(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    background(slide, page=1, accent=PURPLE)
    add_logo(slide)

    pill(slide, "HACK-TO-WEEN 2026  ·  CLOUD SECURITY & THREAT TRIAGE",
         9.22, 0.40, 3.39, 0.34, fill=RGBColor(24, 20, 32), line=RGBColor(80, 46, 111),
         color=RGBColor(216, 180, 254), size=6.4)

    # Left: editorial title block.
    text(slide, "THE ZOMBIE CREDENTIAL & PHISHING EXORCIST", 0.74, 1.55, 7.1, 0.22,
         size=7.8, color=ORANGE, bold=True, font=FONT_BODY, spc=1.6)
    text(slide, "GHOST", 0.70, 1.78, 7.3, 1.02, size=72, color=WHITE,
         bold=True, font=FONT_DISPLAY, line_spacing=0.82, spc=0.5)
    text(slide, "PROTOCOL", 0.70, 2.63, 7.4, 1.02, size=72, color=ORANGE,
         bold=True, font=FONT_DISPLAY, line_spacing=0.82, spc=0.5)
    add_glow(slide.shapes[-1], ORANGE, 26, 12)

    text(slide, "Find the undead. Break the lure. Prove the fix.", 0.76, 3.92, 7.0, 0.38,
         size=20, color=WHITE, bold=False, font=FONT_BODY)
    text(slide,
         "A developer-first threat triage cockpit for exposed secrets and phishing lures.\n"
         "Serverless on AWS. Built for teams without a 24/7 SOC.",
         0.78, 4.45, 6.55, 0.65, size=9.4, color=MUTED, font=FONT_BODY, line_spacing=1.22)

    # Right: spectral mascot + radar rings.
    oval(slide, 8.72, 1.72, 4.05, 4.05, fill=None, line=RGBColor(82, 53, 113), line_width=0.8)
    oval(slide, 8.98, 1.98, 3.53, 3.53, fill=None, line=RGBColor(59, 47, 76), line_width=0.6)
    line(slide, 10.74, 1.45, 10.74, 6.05, color=RGBColor(58, 46, 74), width=0.5)
    line(slide, 8.45, 3.75, 13.0, 3.75, color=RGBColor(58, 46, 74), width=0.5)

    # Ghost body.
    gx, gy, gw, gh = 9.62, 2.12, 2.20, 2.62
    body = rect(slide, gx, gy, gw, gh, fill=RGBColor(242, 240, 250), line=None, radius=0.48)
    add_glow(body, PURPLE, 34, 28)
    for i in range(3):
        oval(slide, gx + 0.26 + i * 0.58, gy + gh - 0.18, 0.55, 0.55,
             fill=RGBColor(242, 240, 250), line=None)
    # Eyes + mouth.
    oval(slide, gx + 0.58, gy + 0.78, 0.19, 0.27, fill=BG, line=None)
    oval(slide, gx + 1.38, gy + 0.78, 0.19, 0.27, fill=BG, line=None)
    oval(slide, gx + 0.92, gy + 1.36, 0.34, 0.20, fill=RGBColor(203, 196, 221), line=None)
    # Keyhole chest mark.
    oval(slide, gx + 0.99, gy + 1.73, 0.20, 0.20, fill=ORANGE, line=None)
    rect(slide, gx + 1.05, gy + 1.87, 0.08, 0.23, fill=ORANGE, line=None, radius=0.5)

    # Floating labels.
    label_data = [
        ("STALE KEY", 8.44, 2.18, 1.28, 0.29, ORANGE, RGBColor(61, 36, 20)),
        ("PHISH LURE", 11.18, 2.62, 1.34, 0.29, PURPLE, RGBColor(48, 28, 65)),
        ("MFA BYPASS", 8.54, 4.58, 1.48, 0.29, RED, RGBColor(61, 24, 24)),
    ]
    for label, lx, ly, lw, lh, color, fill_color in label_data:
        pill(slide, label, lx, ly, lw, lh, fill=fill_color, line=color, color=color, size=5.9)
    line(slide, 9.73, 2.42, 9.72, 2.42, color=ORANGE, width=0.6)
    line(slide, 10.58, 2.50, 9.86, 2.36, color=RGBColor(94, 63, 50), width=0.55, dash=MSO_LINE_DASH_STYLE.DASH)
    line(slide, 11.15, 2.77, 11.10, 2.77, color=PURPLE, width=0.6)
    line(slide, 10.36, 2.83, 11.14, 2.77, color=RGBColor(76, 54, 96), width=0.55, dash=MSO_LINE_DASH_STYLE.DASH)
    line(slide, 10.30, 4.68, 9.97, 4.65, color=RGBColor(96, 49, 49), width=0.55, dash=MSO_LINE_DASH_STYLE.DASH)

    # Bottom: team / track / stack.
    panel = rect(slide, 0.72, 5.62, 11.88, 1.02, fill=RGBColor(17, 20, 26), line=BORDER, radius=0.05)
    add_glow(panel, PURPLE, 18, 8)
    line(slide, 4.68, 5.82, 4.68, 6.44, color=RGBColor(45, 51, 64), width=0.6)
    line(slide, 8.30, 5.82, 8.30, 6.44, color=RGBColor(45, 51, 64), width=0.6)

    text(slide, "TEAM", 0.94, 5.82, 1.0, 0.18, size=6.0, color=ORANGE, bold=True, spc=1.2)
    text(slide, TEAM_NAME, 0.94, 6.00, 3.4, 0.22, size=10.5, color=WHITE, bold=True, font=FONT_DISPLAY)
    text(slide, TEAM_MEMBERS, 0.94, 6.23, 3.5, 0.18, size=6.8, color=MUTED)

    text(slide, "TRACK", 4.92, 5.82, 1.0, 0.18, size=6.0, color=PURPLE, bold=True, spc=1.2)
    text(slide, "Cloud Security & Threat Triage", 4.92, 6.00, 3.1, 0.22, size=10.5, color=WHITE,
         bold=True, font=FONT_DISPLAY)
    text(slide, COLLEGE, 4.92, 6.23, 3.2, 0.18, size=6.8, color=MUTED)

    text(slide, "BUILT WITH", 8.54, 5.82, 1.2, 0.18, size=6.0, color=GREEN, bold=True, spc=1.2)
    text(slide, "Next.js  ·  Tailwind  ·  Python / Node", 8.54, 6.00, 3.7, 0.22, size=10.5,
         color=WHITE, bold=True, font=FONT_DISPLAY)
    text(slide, "AWS Lambda  ·  DynamoDB  ·  Cognito", 8.54, 6.23, 3.7, 0.18, size=6.8, color=MUTED)

    notes(slide,
          "Open with the tagline, not the feature list: find the undead, break the lure, prove the fix. "
          "GhostProtocol is a threat-triage cockpit for the teams that feel cloud security pain first: "
          "developers, college labs, and small DevOps teams. We are not trying to replace an enterprise SOC. "
          "We are closing the gap between a scary alert and a safe, verified fix. "
          "The demo is designed to run in under 60 seconds on deterministic data.")


# ---------------------------------------------------------------------------
# Slide 2 — Problem
# ---------------------------------------------------------------------------
def slide_problem(prs):
    slide = content_slide(
        prs,
        "01  /  THE HAUNTING",
        "The dead don't stay buried.",
        "Zombie credentials and phishing lures turn small cloud estates into easy targets.",
        2,
        accent=ORANGE,
    )

    # Three big numbers.
    stats = [
        ("23.8M", "new secrets exposed on public GitHub in 2024", "+25% year over year", ORANGE, "◉"),
        ("21 sec", "median time to click a phishing lure", "28 sec to submit credentials", PURPLE, "◈"),
        ("1 key", "can pivot from a test repo into production", "AWS keys do not expire by default", RED, "◆"),
    ]
    for i, (number, label, sub, color, glyph) in enumerate(stats):
        y = 1.94 + i * 1.40
        card = rect(slide, 0.72, y, 3.86, 1.24, fill=RGBColor(18, 22, 28), line=BORDER, radius=0.06)
        line(slide, 0.72, y + 0.10, 0.72, y + 1.14, color=color, width=2.0)
        text(slide, number, 0.96, y + 0.10, 2.2, 0.48, size=30, color=color,
             bold=True, font=FONT_DISPLAY, line_spacing=0.9)
        text(slide, glyph, 3.92, y + 0.15, 0.35, 0.25, size=12, color=color, bold=True)
        text(slide, label, 0.96, y + 0.60, 3.15, 0.30, size=7.6, color=WHITE, bold=True,
             font=FONT_BODY, line_spacing=1.0)
        text(slide, sub, 0.96, y + 0.91, 3.10, 0.20, size=6.6, color=MUTED, font=FONT_MONO)

    # Right: the three hauntings.
    text(slide, "THREE WAYS THE DEAD WALK", 5.05, 1.94, 4.0, 0.20, size=6.8, color=MUTED,
         bold=True, spc=1.2)
    haunts = [
        ("☠", "ZOMBIE CREDENTIALS", "Keys outlive owners, demos, and environments.",
         "No expiry. No owner. Full access.", ORANGE, "ACCESS"),
        ("◈", "PHISHING DOPPELGÄNGERS", "A fake MFA reset page steals a real session.",
         "One click. One code. One compromised identity.", PURPLE, "IDENTITY"),
        ("▣", "THE TRIAGE GRAVEYARD", "Alerts live in five tools. Answers live nowhere.",
         "Small team. 40 tabs. 3 a.m.", SKY, "PROCESS"),
    ]
    for i, (glyph, title, desc, punch, color, tag) in enumerate(haunts):
        y = 2.24 + i * 1.28
        card = rect(slide, 5.05, y, 7.55, 1.10, fill=RGBColor(18, 22, 28), line=BORDER, radius=0.05)
        icon_badge(slide, glyph, 5.22, y + 0.24, 0.52, fill=RGBColor(24, 28, 36), line=RGBColor(58, 64, 78), color=color, size=15)
        text(slide, title, 5.92, y + 0.18, 3.3, 0.22, size=8.6, color=color, bold=True,
             font=FONT_DISPLAY, spc=0.7)
        text(slide, desc, 5.92, y + 0.43, 4.3, 0.20, size=7.6, color=WHITE, bold=True)
        text(slide, punch, 5.92, y + 0.69, 4.9, 0.18, size=6.8, color=MUTED)
        pill(slide, tag, 11.38, y + 0.36, 0.94, 0.26, fill=RGBColor(24, 28, 36), line=color,
             color=color, size=5.2)

    # Insight band.
    band = rect(slide, 0.72, 6.18, 11.88, 0.55, fill=RGBColor(24, 20, 18), line=RGBColor(76, 44, 24), radius=0.04)
    line(slide, 0.72, 6.28, 0.72, 6.62, color=ORANGE, width=2.0)
    text(slide, "The gap isn't detection. It's context — and a safe next step.", 0.98, 6.32, 8.0, 0.24,
         size=10.2, color=WHITE, bold=True, font=FONT_DISPLAY)
    text(slide, "Sources: GitGuardian State of Secrets Sprawl 2025; Verizon DBIR 2024; AWS IAM documentation.",
         0.72, 6.82, 8.8, 0.16, size=5.8, color=DIM, font=FONT_BODY)

    notes(slide,
          "The problem is not that small teams lack another scanner. It is that secrets are invisible, "
          "phishing is fast, and triage is manual. A leaked key can be valid for months because nobody "
          "owns it. A phishing page can steal a session in under a minute. And the person who has to fix it "
          "is usually a developer with three other jobs. That is the haunted gap GhostProtocol attacks.")


# ---------------------------------------------------------------------------
# Slide 3 — Solution
# ---------------------------------------------------------------------------
def slide_solution(prs):
    slide = content_slide(
        prs,
        "02  /  THE RITUAL",
        "Exorcise the risk in three moves.",
        "GhostProtocol turns scattered signals into one prioritized, evidence-backed remediation path.",
        3,
        accent=PURPLE,
    )

    steps = [
        ("01", "HUNT", "Find what is still breathing.",
         ["Connect GitHub, AWS, and phishing reports",
          "Scheduled sweeps + signed webhooks",
          "Metadata-only scanning — never secret values"],
         ORANGE, "◉", "one normalized signal queue"),
        ("02", "JUDGE", "Explain the blast radius.",
         ["Score exposure × privilege × age × reach",
          "Assign an owner and a plain-English 'why'",
          "Suppress noise with tenant-safe exceptions"],
         PURPLE, "◈", "one ranked next action"),
        ("03", "EXORCISE", "Fix it without breaking prod.",
         ["Dry-run the blast radius first",
          "Rotate, revoke, or disable with approval",
          "Verify the old credential is denied; seal evidence"],
         GREEN, "✓", "one verified outcome"),
    ]

    for i, (num, title, sub, items, color, glyph, outcome) in enumerate(steps):
        x = 0.72 + i * 4.07
        card = rect(slide, x, 1.92, 3.76, 2.92, fill=RGBColor(18, 22, 28), line=BORDER, radius=0.05)
        line(slide, x + 0.18, 1.92, x + 3.58, 1.92, color=color, width=2.0)
        text(slide, num, x + 0.22, 2.10, 0.55, 0.22, size=7.0, color=color, bold=True, font=FONT_MONO, spc=1.0)
        icon_badge(slide, glyph, x + 2.92, 2.07, 0.50, fill=RGBColor(24, 28, 36),
                   line=RGBColor(58, 64, 78), color=color, size=15)
        text(slide, title, x + 0.22, 2.40, 2.5, 0.30, size=15.0, color=WHITE, bold=True,
             font=FONT_DISPLAY, spc=0.8)
        text(slide, sub, x + 0.22, 2.76, 3.2, 0.22, size=8.2, color=color, bold=True)
        bullets(slide, items, x + 0.22, 3.10, 3.28, 1.08, size=7.5, color=MUTED,
                bullet_color=color, line_spacing=1.10, space_after=4)
        line(slide, x + 0.22, 4.30, x + 3.52, 4.30, color=RGBColor(43, 49, 61), width=0.6)
        text(slide, "→  " + outcome, x + 0.22, 4.43, 3.20, 0.20, size=6.5, color=color,
             bold=True, font=FONT_MONO)

    # Flow arrows between cards.
    for x in (4.34, 8.41):
        text(slide, "›", x, 3.13, 0.28, 0.40, size=24, color=RGBColor(92, 100, 116),
             bold=True, font=FONT_DISPLAY, align=PP_ALIGN.CENTER)

    # Value proposition.
    quote = rect(slide, 0.72, 5.02, 11.88, 1.00, fill=RGBColor(22, 18, 27), line=RGBColor(74, 48, 92), radius=0.04)
    add_glow(quote, PURPLE, 20, 12)
    text(slide, "Detection is table stakes.", 0.96, 5.16, 3.2, 0.24, size=8.0, color=PURPLE, bold=True, spc=1.0)
    text(slide, "We close the last mile: safe remediation with proof.", 0.96, 5.42, 8.2, 0.30,
         size=15.0, color=WHITE, bold=True, font=FONT_DISPLAY)
    text(slide, "One queue. One owner. One verified outcome.", 9.32, 5.42, 3.0, 0.24,
         size=8.2, color=MUTED, font=FONT_MONO, align=PP_ALIGN.RIGHT)

    # Proof chips.
    chips = ["AWS-native serverless", "10-minute setup", "No plaintext secrets", "Explainable scoring"]
    x = 0.72
    for chip in chips:
        w = 0.30 + len(chip) * 0.064
        pill(slide, chip, x, 6.24, w, 0.30, fill=RGBColor(19, 23, 29), line=RGBColor(52, 59, 72),
             color=RGBColor(203, 213, 225), size=6.2)
        x += w + 0.12
    text(slide, "Built for developers, college labs, and small DevOps teams.", 0.74, 6.68, 7.8, 0.16,
         size=6.2, color=DIM, font=FONT_MONO)

    notes(slide,
          "This is the product in one breath: hunt, judge, exorcise. Hunt finds the stale key or the phishing lure. "
          "Judge translates it into blast radius and a next action. Exorcise gives a safe runbook with a dry run, "
          "a verified revoke or rotation, and an audit trail. The differentiator is not detection. It is the last mile.")


# ---------------------------------------------------------------------------
# Slide 4 — Architecture
# ---------------------------------------------------------------------------
def slide_architecture(prs):
    slide = content_slide(
        prs,
        "03  /  THE MACHINE",
        "Serverless by design. Boringly secure by default.",
        "Event-driven AWS pipeline — with a demo-safe fallback that works without a live cloud account.",
        4,
        accent=ORANGE,
    )

    text(slide, "SOLID = MVP  ·  DASHED = POST-HACKATHON", 8.52, 1.72, 4.08, 0.18,
         size=5.4, color=DIM, bold=True, font=FONT_MONO, align=PP_ALIGN.RIGHT)

    # Panels.
    rect(slide, 0.66, 1.94, 3.30, 3.98, fill=RGBColor(17, 21, 27), line=BORDER, radius=0.035)
    rect(slide, 4.16, 1.94, 4.50, 3.98, fill=RGBColor(17, 21, 27), line=BORDER, radius=0.035)
    rect(slide, 8.88, 1.94, 3.78, 3.98, fill=RGBColor(17, 21, 27), line=BORDER, radius=0.035)

    text(slide, "SIGNALS", 0.86, 2.12, 2.0, 0.18, size=6.4, color=ORANGE, bold=True, spc=1.3)
    text(slide, "INGEST & REASON", 4.36, 2.12, 2.6, 0.18, size=6.4, color=ORANGE, bold=True, spc=1.3)
    text(slide, "TRIAGE & PROVE", 9.08, 2.12, 2.4, 0.18, size=6.4, color=ORANGE, bold=True, spc=1.3)

    # Left sources.
    sources = [
        ("◈", "GitHub / GitLab", "commits · PRs · OAuth apps"),
        ("◆", "AWS Secrets Manager", "rotation age · access keys"),
        ("▣", "IAM + CloudTrail", "privilege · last used · usage"),
        ("✉", "Phishing reports", "SES inbox · Slack button"),
    ]
    for i, (glyph, title, sub) in enumerate(sources):
        y = 2.42 + i * 0.82
        card = rect(slide, 0.84, y, 2.94, 0.68, fill=RGBColor(23, 27, 34), line=RGBColor(47, 53, 65), radius=0.04)
        icon_badge(slide, glyph, 0.94, y + 0.15, 0.36, fill=RGBColor(17, 21, 27),
                   line=RGBColor(53, 60, 73), color=ORANGE if i < 3 else PURPLE, size=9)
        text(slide, title, 1.40, y + 0.12, 2.2, 0.18, size=7.0, color=WHITE, bold=True)
        text(slide, sub, 1.40, y + 0.34, 2.25, 0.16, size=5.4, color=MUTED, font=FONT_MONO)

    # Center pipeline.
    center = [
        ("01", "API Gateway + Node Lambda", "signed webhooks · auth · rate limit", ORANGE, False),
        ("02", "EventBridge Scheduler", "daily sweep · tenant fan-out", ORANGE, False),
        ("03", "Python analyzers on Lambda", "exposure · privilege · phishing score", ORANGE, False),
        ("04", "Amazon Bedrock", "plain-English 'why' — optional", PURPLE, True),
    ]
    for i, (num, title, sub, color, dashed) in enumerate(center):
        y = 2.42 + i * 0.82
        card = rect(slide, 4.36, y, 4.10, 0.68, fill=RGBColor(23, 27, 34),
                    line=color if dashed else RGBColor(47, 53, 65), radius=0.04,
                    dash=MSO_LINE_DASH_STYLE.DASH if dashed else None)
        text(slide, num, 4.48, y + 0.13, 0.35, 0.18, size=5.8, color=color, bold=True, font=FONT_MONO)
        text(slide, title, 4.88, y + 0.11, 3.3, 0.18, size=7.1, color=WHITE, bold=True)
        text(slide, sub, 4.88, y + 0.33, 3.3, 0.16, size=5.4, color=MUTED, font=FONT_MONO)
        if i < 3:
            line(slide, 6.40, y + 0.68, 6.40, y + 0.82, color=RGBColor(74, 83, 99), width=0.8, arrow=True)

    # Right outputs.
    outputs = [
        ("▣", "DynamoDB", "findings · owners · audit log"),
        ("◈", "S3 + KMS", "encrypted evidence packets"),
        ("◉", "SNS / SES / Slack", "digest + critical alerts"),
        ("◆", "Next.js on Amplify", "Cognito auth · tenant RBAC"),
        ("✓", "Secrets Manager + IAM", "rotate · disable · verify"),
    ]
    for i, (glyph, title, sub) in enumerate(outputs):
        y = 2.42 + i * 0.66
        card = rect(slide, 9.08, y, 3.38, 0.54, fill=RGBColor(23, 27, 34), line=RGBColor(47, 53, 65), radius=0.04)
        icon_badge(slide, glyph, 9.18, y + 0.11, 0.30, fill=RGBColor(17, 21, 27),
                   line=RGBColor(53, 60, 73), color=GREEN if i == 4 else PURPLE, size=7)
        text(slide, title, 9.58, y + 0.09, 2.6, 0.16, size=6.7, color=WHITE, bold=True)
        text(slide, sub, 9.58, y + 0.28, 2.7, 0.14, size=5.0, color=MUTED, font=FONT_MONO)

    # Cross-panel arrows.
    line(slide, 3.62, 3.70, 4.08, 3.70, color=ORANGE, width=1.1, arrow=True)
    line(slide, 8.70, 3.70, 9.00, 3.70, color=PURPLE, width=1.1, arrow=True)
    text(slide, "events", 3.64, 3.48, 0.48, 0.14, size=4.8, color=ORANGE, bold=True, font=FONT_MONO)
    text(slide, "findings", 8.68, 3.48, 0.55, 0.14, size=4.8, color=PURPLE, bold=True, font=FONT_MONO)

    # Trust boundary.
    band = rect(slide, 0.66, 6.10, 12.00, 0.55, fill=RGBColor(18, 24, 23), line=RGBColor(37, 74, 53), radius=0.04)
    text(slide, "TRUST BOUNDARY", 0.86, 6.25, 1.45, 0.18, size=5.8, color=GREEN, bold=True, spc=1.0)
    text(slide, "Metadata only  ·  secrets never leave the vault  ·  least-privilege roles  ·  human approval for destructive actions",
         2.24, 6.24, 9.9, 0.20, size=7.0, color=RGBColor(203, 213, 225), bold=True)

    notes(slide,
          "The architecture is deliberately boring. Sources emit signed events. API Gateway and Lambda normalize them. "
          "EventBridge handles scheduled sweeps. Python analyzers score exposure, privilege, and phishing signals. "
          "DynamoDB stores findings and the audit log. S3 and KMS hold evidence. Cognito protects the Next.js dashboard. "
          "Bedrock is optional and gets metadata only — never a secret value. Destructive actions require human approval.")


# ---------------------------------------------------------------------------
# Slide 5 — Features + demo
# ---------------------------------------------------------------------------
def slide_demo(prs):
    slide = content_slide(
        prs,
        "04  /  THE DEMO",
        "From alert to exorcism in under 60 seconds.",
        "A working MVP with deterministic demo data — so the story never depends on conference Wi-Fi.",
        5,
        accent=PURPLE,
    )

    features = [
        ("N", "NECROSCAN", "Finds stale IAM keys, leaked .env files, and over-privileged roles.", ORANGE),
        ("L", "LURELENS", "Scores phishing emails + URLs, extracts IOCs, flags lookalike domains.", PURPLE),
        ("T", "TRIAGE CRYPT", "One queue ranked by blast radius, owner, and SLA.", ORANGE),
        ("E", "EXORCISM RUNBOOK", "Dry-run → rotate or revoke → verify → seal evidence.", GREEN),
    ]
    for i, (glyph, title, desc, color) in enumerate(features):
        col, row = i % 2, i // 2
        x = 0.72 + col * 3.06
        y = 1.94 + row * 2.04
        card = rect(slide, x, y, 2.90, 1.86, fill=RGBColor(18, 22, 28), line=BORDER, radius=0.05)
        line(slide, x + 0.16, y, x + 2.74, y, color=color, width=1.6)
        icon_badge(slide, glyph, x + 0.18, y + 0.20, 0.46, fill=RGBColor(24, 28, 36),
                   line=RGBColor(56, 63, 77), color=color, size=12)
        pill(slide, "MVP", x + 2.14, y + 0.20, 0.52, 0.22, fill=RGBColor(24, 28, 36),
             line=RGBColor(56, 63, 77), color=color, size=4.8, font=FONT_MONO)
        text(slide, title, x + 0.18, y + 0.82, 2.50, 0.22, size=8.8, color=color, bold=True,
             font=FONT_DISPLAY, spc=0.6)
        text(slide, desc, x + 0.18, y + 1.10, 2.45, 0.60, size=7.0, color=MUTED, line_spacing=1.12)

    # Demo timeline.
    panel = rect(slide, 7.10, 1.94, 5.52, 4.02, fill=RGBColor(17, 21, 27), line=BORDER, radius=0.04)
    text(slide, "LIVE WALKTHROUGH  ·  60 SECONDS", 7.30, 2.12, 4.6, 0.18,
         size=6.4, color=ORANGE, bold=True, spc=1.1)
    steps = [
        ("09:41", "Four alerts surface", "prod-deploy-key, legacy-admin, MFA lure, stale OAuth."),
        ("09:42", "Triage the key", "Status: HAUNTING → TRIAGING. Owner assigned."),
        ("09:43", "Dry-run the fix", "Blast radius: 3 repos, 1 prod role, 2 services."),
        ("09:44", "Exorcise + verify", "Rotate, deny old key, seal audit evidence."),
    ]
    for i, (time_value, title, desc) in enumerate(steps):
        y = 2.44 + i * 0.76
        circle = oval(slide, 7.30, y, 0.28, 0.28, fill=RGBColor(24, 28, 36), line=ORANGE if i == 3 else RGBColor(63, 70, 84))
        shape_text(circle, str(i + 1), size=6.2, color=ORANGE if i == 3 else MUTED, bold=True)
        if i < 3:
            line(slide, 7.44, y + 0.28, 7.44, y + 0.48, color=RGBColor(62, 70, 84), width=0.7)
        text(slide, time_value, 7.74, y - 0.01, 0.50, 0.15, size=5.8, color=ORANGE, bold=True, font=FONT_MONO)
        text(slide, title, 8.30, y - 0.02, 3.9, 0.18, size=7.6, color=WHITE, bold=True)
        text(slide, desc, 8.30, y + 0.20, 3.95, 0.20, size=6.4, color=MUTED)

    toast = rect(slide, 7.30, 5.32, 5.10, 0.46, fill=RGBColor(18, 32, 25), line=RGBColor(37, 84, 57), radius=0.04)
    line(slide, 7.30, 5.38, 7.30, 5.72, color=GREEN, width=2.0)
    text(slide, "✓  CONTAINED  ·  old key denied  ·  audit event #GP-1042 sealed", 7.48, 5.44, 4.7, 0.20,
         size=6.5, color=RGBColor(134, 239, 172), bold=True, font=FONT_MONO)

    # MVP boundary.
    band = rect(slide, 0.72, 6.14, 11.90, 0.50, fill=RGBColor(18, 22, 28), line=BORDER, radius=0.04)
    text(slide, "MVP BOUNDARY", 0.90, 6.28, 1.30, 0.16, size=5.6, color=PURPLE, bold=True, spc=1.0)
    text(slide, "Discovery + phishing scoring + triage + guided remediation + audit. Live connectors are feature-flagged.",
         2.05, 6.27, 10.2, 0.18, size=6.6, color=MUTED)

    notes(slide,
          "This is the demo path. The dashboard starts with four seeded alerts. Click Triage on the exposed key; "
          "the status moves from Haunting to Triaging to Contained. Then run the exorcism: dry-run shows blast radius, "
          "rotate and verify, and the audit event is sealed. The important part is that every state change is visible, "
          "and no real secret value is ever displayed.")


# ---------------------------------------------------------------------------
# Slide 6 — UI/UX + theme
# ---------------------------------------------------------------------------
def slide_theme(prs):
    slide = content_slide(
        prs,
        "05  /  THE SPELLBOOK",
        "Spooky on the surface. Serious underneath.",
        "Halloween is a mental model for risk — not a gimmick that gets in the way of the fix.",
        6,
        accent=PURPLE,
    )

    # Palette.
    text(slide, "CORE PALETTE", 0.74, 1.94, 2.2, 0.18, size=6.2, color=MUTED, bold=True, spc=1.2)
    palette = [
        ("Obsidian", "#0D0F12", OBSIDIAN),
        ("Bone", "#F8FAFC", WHITE),
        ("Pumpkin", "#F97316", ORANGE),
        ("Spectral", "#A855F7", PURPLE),
        ("Ectoplasm", "#22C55E", GREEN),
        ("Blood", "#EF4444", RED),
    ]
    for i, (name, hex_value, color) in enumerate(palette):
        col, row = i % 2, i // 2
        x = 0.74 + col * 2.02
        y = 2.22 + row * 0.62
        chip = rect(slide, x, y, 0.42, 0.42, fill=color, line=RGBColor(63, 70, 84), radius=0.10)
        text(slide, name, x + 0.54, y + 0.02, 1.25, 0.16, size=6.8, color=WHITE, bold=True)
        text(slide, hex_value, x + 0.54, y + 0.22, 1.20, 0.14, size=5.4, color=MUTED, font=FONT_MONO)

    # Type + accessibility.
    text(slide, "TYPE SYSTEM", 0.74, 4.18, 2.2, 0.18, size=6.2, color=MUTED, bold=True, spc=1.2)
    text(slide, "Bahnschrift", 0.74, 4.46, 1.8, 0.22, size=11.0, color=WHITE, bold=True, font=FONT_DISPLAY)
    text(slide, "display / headlines", 2.16, 4.50, 1.6, 0.16, size=5.8, color=MUTED, font=FONT_MONO)
    text(slide, "Segoe UI", 0.74, 4.74, 1.8, 0.20, size=9.2, color=WHITE, font=FONT_BODY)
    text(slide, "body / UI copy", 2.16, 4.77, 1.6, 0.16, size=5.8, color=MUTED, font=FONT_MONO)
    text(slide, "Consolas", 0.74, 5.00, 1.8, 0.20, size=8.4, color=GREEN, font=FONT_MONO)
    text(slide, "evidence / IDs", 2.16, 5.03, 1.6, 0.16, size=5.8, color=MUTED, font=FONT_MONO)

    text(slide, "ACCESSIBILITY", 0.74, 5.42, 2.2, 0.18, size=6.2, color=MUTED, bold=True, spc=1.2)
    bullets(slide, [
        "AA contrast; icon + label + color",
        "Keyboard-first; reduced-motion aware",
        "Spooky copy, precise actions",
    ], 0.74, 5.68, 3.55, 0.90, size=6.5, color=MUTED, bullet_color=PURPLE, space_after=2)

    # Mock dashboard.
    frame = rect(slide, 4.76, 1.94, 7.86, 4.26, fill=RGBColor(10, 12, 16), line=RGBColor(58, 64, 78), radius=0.025)
    add_glow(frame, PURPLE, 24, 12)
    # Sidebar.
    rect(slide, 4.82, 2.00, 1.24, 4.14, fill=RGBColor(13, 15, 20), line=None, radius=0.02)
    # Tiny logo.
    oval(slide, 4.98, 2.14, 0.22, 0.22, fill=ORANGE, line=None)
    text(slide, "GP", 4.98, 2.14, 0.22, 0.22, size=5.4, color=BG, bold=True, align=PP_ALIGN.CENTER,
         valign=MSO_ANCHOR.MIDDLE)
    text(slide, "THREAT\nCRYPT", 4.98, 2.50, 0.80, 0.34, size=5.4, color=WHITE, bold=True,
         font=FONT_DISPLAY, line_spacing=0.9)
    for i, label in enumerate(["Alerts", "NecroScan", "LureLens", "Runbooks", "Evidence"]):
        y = 3.10 + i * 0.34
        if i == 0:
            rect(slide, 4.94, y - 0.06, 1.02, 0.27, fill=RGBColor(38, 25, 16), line=None, radius=0.08)
        text(slide, label, 5.02, y, 0.86, 0.16, size=5.4, color=ORANGE if i == 0 else MUTED,
             bold=i == 0, font=FONT_BODY)
    text(slide, "DEMO\nMODE", 4.98, 5.62, 0.72, 0.30, size=4.8, color=GREEN, bold=True,
         font=FONT_MONO, line_spacing=0.95)

    # Top bar.
    text(slide, "Threat Crypt", 6.24, 2.14, 1.9, 0.22, size=9.2, color=WHITE, bold=True, font=FONT_DISPLAY)
    pill(slide, "●  LIVE", 10.42, 2.12, 0.68, 0.22, fill=RGBColor(18, 32, 25), line=RGBColor(37, 84, 57),
         color=GREEN, size=4.8)
    pill(slide, "4 ACTIVE", 11.20, 2.12, 0.74, 0.22, fill=RGBColor(38, 25, 16), line=RGBColor(99, 53, 20),
         color=ORANGE, size=4.8)
    line(slide, 6.20, 2.44, 12.40, 2.44, color=RGBColor(37, 43, 54), width=0.6)

    # Stat cards.
    stat_data = [("ACTIVE", "4", ORANGE), ("CONTAINED", "0", GREEN), ("PEAK RISK", "96", PURPLE)]
    for i, (label, value, color) in enumerate(stat_data):
        x = 6.22 + i * 1.42
        rect(slide, x, 2.58, 1.28, 0.64, fill=RGBColor(18, 22, 28), line=RGBColor(43, 49, 61), radius=0.05)
        text(slide, label, x + 0.10, 2.64, 1.05, 0.12, size=4.4, color=MUTED, bold=True, font=FONT_MONO)
        text(slide, value, x + 0.10, 2.78, 0.60, 0.30, size=15.0, color=color, bold=True, font=FONT_DISPLAY)
    # Risk sparkline.
    line(slide, 10.64, 3.03, 10.90, 2.88, color=PURPLE, width=0.8)
    line(slide, 10.90, 2.88, 11.18, 2.95, color=PURPLE, width=0.8)
    line(slide, 11.18, 2.95, 11.44, 2.74, color=PURPLE, width=0.8)
    line(slide, 11.44, 2.74, 11.74, 2.84, color=PURPLE, width=0.8)
    line(slide, 11.74, 2.84, 12.12, 2.66, color=PURPLE, width=0.8)

    # Alert list.
    text(slide, "ACTIVE ALERTS", 6.22, 3.42, 1.4, 0.14, size=4.8, color=MUTED, bold=True, font=FONT_MONO)
    alerts = [
        ("SPECTER", "prod-deploy-key is still breathing", "AWS IAM · 2m", ORANGE, "96"),
        ("POLTERGEIST", "MFA reset page is a doppelgänger", "Email · 6m", PURPLE, "88"),
        ("POLTERGEIST", "legacy-admin has no owner", "IAM · 11m", PURPLE, "81"),
    ]
    for i, (sev, title, meta, color, risk) in enumerate(alerts):
        y = 3.62 + i * 0.66
        selected = i == 0
        rect(slide, 6.22, y, 3.02, 0.56, fill=RGBColor(24, 20, 18) if selected else RGBColor(18, 22, 28),
             line=RGBColor(99, 53, 20) if selected else RGBColor(43, 49, 61), radius=0.04)
        if selected:
            line(slide, 6.22, y + 0.06, 6.22, y + 0.50, color=ORANGE, width=2.0)
        text(slide, sev, 6.34, y + 0.08, 0.74, 0.10, size=3.9, color=color, bold=True, font=FONT_MONO)
        text(slide, title, 6.34, y + 0.21, 2.28, 0.14, size=5.2, color=WHITE, bold=True)
        text(slide, meta, 6.34, y + 0.38, 1.85, 0.12, size=4.2, color=MUTED, font=FONT_MONO)
        text(slide, risk, 8.86, y + 0.20, 0.26, 0.16, size=6.0, color=color, bold=True, font=FONT_DISPLAY,
             align=PP_ALIGN.RIGHT)

    # Detail panel.
    rect(slide, 9.42, 3.42, 3.02, 2.55, fill=RGBColor(18, 22, 28), line=RGBColor(43, 49, 61), radius=0.04)
    text(slide, "SELECTED SIGNAL", 9.56, 3.56, 1.5, 0.12, size=4.4, color=MUTED, bold=True, font=FONT_MONO)
    text(slide, "SPECTER  ·  96", 9.56, 3.76, 1.2, 0.14, size=5.4, color=ORANGE, bold=True, font=FONT_MONO)
    text(slide, "prod-deploy-key", 9.56, 3.98, 2.2, 0.18, size=7.4, color=WHITE, bold=True, font=FONT_DISPLAY)
    text(slide, "AWS IAM · AKIA••••7Q2", 9.56, 4.20, 2.2, 0.13, size=4.4, color=MUTED, font=FONT_MONO)
    text(slide, "Blast radius", 9.56, 4.45, 1.0, 0.12, size=4.2, color=MUTED, bold=True, font=FONT_MONO)
    for j, tag in enumerate(["3 repos", "1 role", "3 buckets"]):
        pill(slide, tag, 9.56 + j * 0.66, 4.60, 0.60, 0.18, fill=RGBColor(26, 30, 38),
             line=RGBColor(56, 63, 77), color=RGBColor(203, 213, 225), size=3.7)
    text(slide, "Playbook", 9.56, 4.90, 0.8, 0.12, size=4.2, color=MUTED, bold=True, font=FONT_MONO)
    for j, step in enumerate(["Scope key", "Check usage", "Rotate + deny", "Seal evidence"]):
        yy = 5.06 + j * 0.16
        text(slide, "✓" if j < 2 else "○", 9.56, yy, 0.12, 0.10, size=3.6,
             color=GREEN if j < 2 else DIM, bold=True)
        text(slide, step, 9.72, yy, 1.0, 0.10, size=3.8, color=WHITE if j < 2 else MUTED)
    btn = rect(slide, 9.56, 5.70, 1.34, 0.24, fill=ORANGE, line=None, radius=0.18)
    shape_text(btn, "TRIAGE SECRET  ›", size=4.8, color=BG, bold=True, font=FONT_DISPLAY)

    # Bottom severity taxonomy.
    band = rect(slide, 0.72, 6.34, 11.90, 0.42, fill=RGBColor(18, 22, 28), line=BORDER, radius=0.04)
    text(slide, "SEVERITY TAXONOMY", 0.90, 6.45, 1.55, 0.14, size=5.0, color=MUTED, bold=True, font=FONT_MONO)
    for i, (name, sub, color) in enumerate([
        ("SPECTER", "Critical", ORANGE), ("POLTERGEIST", "High", PURPLE),
        ("APPARITION", "Medium", SKY), ("WHISPER", "Low", DIM),
    ]):
        x = 2.55 + i * 2.50
        oval(slide, x, 6.48, 0.10, 0.10, fill=color, line=None)
        text(slide, f"{name} / {sub}", x + 0.17, 6.43, 1.65, 0.16, size=5.4, color=WHITE, bold=True,
             font=FONT_MONO)

    notes(slide,
          "The theme is not decoration. It gives the team a shared vocabulary for severity: Specter, Poltergeist, "
          "Apparition, Whisper. But the interface still follows accessibility rules: color plus icon plus text, "
          "AA contrast, keyboard-first, and reduced motion. The ghost is a mascot; the audit trail is the product.")


# ---------------------------------------------------------------------------
# Slide 7 — Scale, security, feasibility
# ---------------------------------------------------------------------------
def slide_scale(prs):
    slide = content_slide(
        prs,
        "06  /  THE WARD",
        "Built to scale. Designed to say no.",
        "Serverless economics, least-privilege boundaries, and a deliberately narrow MVP.",
        7,
        accent=GREEN,
    )

    columns = [
        ("◉", "SCALE", ORANGE, [
            "Lambda + SQS absorb scan bursts",
            "DynamoDB on-demand, tenant-partitioned",
            "Scale-to-zero; pay per scan, not per seat",
            "Idempotent jobs, retries, and dead-letter queues",
        ], "Aligned to AWS Well-Architected: reliability + cost."),
        ("◈", "SECURE", PURPLE, [
            "Metadata only; secret values never rendered",
            "KMS at rest, TLS in transit",
            "Cognito auth + tenant RBAC",
            "Signed audit events; approval gates",
            "No secrets in logs or LLM prompts",
        ], "Security is the product — not a slide."),
        ("✓", "FEASIBLE", GREEN, [
            "Hackathon MVP; 3 builders; 5 must-haves",
            "Demo mode included from day one",
            "API limits → cache + backoff",
            "False positives → explainable score + suppression",
            "Live proof before scale",
        ], "Narrow scope. Credible next step."),
    ]

    for i, (glyph, title, color, items, footer) in enumerate(columns):
        x = 0.72 + i * 4.05
        card = rect(slide, x, 1.94, 3.74, 4.02, fill=RGBColor(18, 22, 28), line=BORDER, radius=0.05)
        line(slide, x + 0.18, 1.94, x + 3.56, 1.94, color=color, width=2.0)
        icon_badge(slide, glyph, x + 0.20, 2.14, 0.48, fill=RGBColor(24, 28, 36),
                   line=RGBColor(58, 64, 78), color=color, size=13)
        text(slide, title, x + 0.20, 2.76, 2.8, 0.30, size=15.0, color=WHITE, bold=True,
             font=FONT_DISPLAY, spc=0.8)
        bullets(slide, items, x + 0.20, 3.18, 3.25, 1.02, size=7.1, color=MUTED,
                bullet_color=color, line_spacing=1.12, space_after=5)

        # Small, editable proof visuals keep the lower half of each card useful.
        if i == 0:
            text(slide, "BURST-SAFE THROUGHPUT  /  CONCURRENT SCANS", x + 0.20, 4.26, 3.1, 0.14,
                 size=4.6, color=DIM, bold=True, font=FONT_MONO, spc=0.5)
            line(slide, x + 0.22, 5.14, x + 3.30, 5.14, color=RGBColor(55, 62, 76), width=0.6)
            for j, (height, label) in enumerate([(0.22, "1x"), (0.34, "2x"), (0.48, "4x"), (0.62, "8x"), (0.78, "16x")]):
                bx = x + 0.30 + j * 0.56
                rect(slide, bx, 5.10 - height, 0.34, height, fill=color if j == 4 else RGBColor(92, 49, 24),
                     line=None, radius=0.12)
                text(slide, label, bx - 0.03, 5.19, 0.42, 0.12, size=4.2, color=MUTED, font=FONT_MONO,
                     align=PP_ALIGN.CENTER)

        elif i == 1:
            text(slide, "DEFENSE IN DEPTH", x + 0.20, 4.26, 2.3, 0.14, size=4.8, color=DIM,
                 bold=True, font=FONT_MONO, spc=0.8)
            layers = [("EDGE", "signed webhooks"), ("IDENTITY", "Cognito + RBAC"),
                      ("DATA", "KMS + metadata only"), ("ACTION", "approval gate")]
            for j, (layer, sub) in enumerate(layers):
                ly = 4.48 + j * 0.28
                rect(slide, x + 0.22, ly, 3.28, 0.22, fill=RGBColor(24, 28, 36),
                     line=RGBColor(58, 64, 78), radius=0.25)
                text(slide, layer, x + 0.34, ly + 0.04, 0.70, 0.12, size=4.6, color=color,
                     bold=True, font=FONT_MONO)
                text(slide, sub, x + 1.12, ly + 0.04, 2.18, 0.12, size=4.6, color=MUTED, font=FONT_MONO)
        else:
            text(slide, "BUILD SPLIT  ·  HACKATHON WEEKEND", x + 0.20, 4.26, 2.8, 0.14, size=4.8, color=DIM,
                 bold=True, font=FONT_MONO, spc=0.8)
            split = [("Frontend / demo", 0.40, ORANGE), ("API / analyzers", 0.35, PURPLE), ("Pitch / evidence", 0.25, GREEN)]
            for j, (label, pct, bar_color) in enumerate(split):
                by = 4.50 + j * 0.30
                text(slide, label, x + 0.22, by, 1.30, 0.12, size=4.8, color=WHITE, bold=True)
                rect(slide, x + 1.55, by + 0.02, 1.54, 0.10, fill=RGBColor(35, 40, 50), line=None, radius=0.5)
                rect(slide, x + 1.55, by + 0.02, 1.54 * pct, 0.10, fill=bar_color, line=None, radius=0.5)
                text(slide, f"{int(pct * 100)}%", x + 3.08, by - 0.01, 0.30, 0.12, size=4.6,
                     color=bar_color, bold=True, font=FONT_MONO)

        line(slide, x + 0.20, 5.46, x + 3.52, 5.46, color=RGBColor(43, 49, 61), width=0.6)
        text(slide, footer, x + 0.20, 5.58, 3.20, 0.22, size=5.8, color=color, bold=True, font=FONT_MONO)

    # Scope guardrail.
    band = rect(slide, 0.72, 6.16, 11.90, 0.52, fill=RGBColor(24, 20, 18), line=RGBColor(76, 44, 24), radius=0.04)
    text(slide, "DELIBERATELY OUT OF SCOPE", 0.92, 6.31, 1.95, 0.16, size=5.4, color=ORANGE, bold=True, spc=0.9)
    text(slide, "Full CASB  ·  auto-rotation in production  ·  custom SIEM.  Narrow now, expandable later.",
         2.95, 6.30, 9.3, 0.18, size=6.8, color=MUTED, bold=True)

    notes(slide,
          "Judges should leave believing we can ship this. The MVP is three connectors, a triage queue, a guided "
          "remediation flow, and an audit trail. We deliberately did not build a full CASB or destructive auto-rotation. "
          "The architecture scales with serverless primitives, and the security posture is conservative: metadata only, "
          "least privilege, human approval, and evidence for every action.")


# ---------------------------------------------------------------------------
# Slide 8 — Roadmap + links
# ---------------------------------------------------------------------------
def slide_roadmap(prs):
    slide = content_slide(
        prs,
        "07  /  THE DAWN",
        "The haunting ends here.",
        "Start with one account. Find the first zombie. Prove the fix.",
        8,
        accent=ORANGE,
    )

    # Timeline.
    line(slide, 0.86, 2.70, 12.48, 2.70, color=RGBColor(58, 64, 78), width=1.0)
    roadmap = [
        ("NOW", "Hackathon MVP", ORANGE, [
            "3 connectors + demo mode",
            "Triage queue + risk score",
            "Guided rotate / revoke",
            "Signed audit trail",
        ], "EXIT  ·  demo runs offline"),
        ("30 DAYS", "Design Partner Pilot", PURPLE, [
            "GitHub App + Slack",
            "Real AWS onboarding",
            "PDF evidence packets",
            "5 design partners",
        ], "EXIT  ·  5 labs onboarding"),
        ("90 DAYS", "Team Workflows", GREEN, [
            "Approval-based remediation",
            "Phishing mailbox",
            "SSO + role templates",
            "Usage-based billing",
        ], "EXIT  ·  3 teams paying"),
        ("6 MONTHS", "Small-Team Security", SKY, [
            "Compliance-lite packs",
            "MSP / lab admin mode",
            "Threat-intel enrichment",
            "SOC 2 readiness",
        ], "EXIT  ·  10k scans / month"),
    ]
    for i, (phase, title, color, items, exit_metric) in enumerate(roadmap):
        x = 0.72 + i * 3.03
        # Node on the timeline.
        oval(slide, x + 1.20, 2.60, 0.20, 0.20, fill=BG, line=color, line_width=1.4)
        oval(slide, x + 1.26, 2.66, 0.08, 0.08, fill=color, line=None)
        text(slide, phase, x + 0.04, 2.22, 1.4, 0.18, size=6.0, color=color, bold=True, font=FONT_MONO, spc=0.8)
        card = rect(slide, x, 2.94, 2.74, 1.94, fill=RGBColor(18, 22, 28), line=BORDER, radius=0.05)
        text(slide, title, x + 0.18, 3.10, 2.36, 0.24, size=9.4, color=WHITE, bold=True, font=FONT_DISPLAY)
        bullets(slide, items, x + 0.18, 3.44, 2.34, 1.04, size=6.2, color=MUTED,
                bullet_color=color, line_spacing=1.10, space_after=3)
        text(slide, exit_metric, x + 0.18, 4.50, 2.38, 0.16, size=5.0, color=color, bold=True,
             font=FONT_MONO, spc=0.4)

    # CTA panel.
    cta = rect(slide, 0.72, 5.16, 11.90, 1.42, fill=RGBColor(22, 18, 27), line=RGBColor(74, 48, 92), radius=0.04)
    add_glow(cta, PURPLE, 24, 12)
    text(slide, "READY TO EXORCISE YOUR CLOUD?", 0.98, 5.34, 5.8, 0.24, size=7.0, color=PURPLE,
         bold=True, spc=1.4)
    text(slide, "Give us 60 seconds. We'll find your first zombie.", 0.98, 5.60, 5.8, 0.28,
         size=16.0, color=WHITE, bold=True, font=FONT_DISPLAY)
    if PUBLIC_LINKS:
        text(slide, "Live demo · GitHub · 5-minute setup walkthrough", 0.98, 5.94, 5.2, 0.18,
             size=7.4, color=MUTED)
        link_cards = [
            ("LIVE DEMO", DEMO_URL, ORANGE, "↗"),
            ("GITHUB", GITHUB_URL, PURPLE, "↗"),
        ]
    else:
        text(slide, "Local MVP demo · 5-minute walkthrough · source available on request",
             0.98, 5.94, 5.8, 0.18, size=7.4, color=MUTED)
        link_cards = [
            ("MVP DEMO", "Runs locally · npm run dev", ORANGE, "›"),
            ("SOURCE", "Available on request", PURPLE, "›"),
        ]

    for i, (label, value, color, mark) in enumerate(link_cards):
        x = 7.22 + i * 2.56
        card = rect(slide, x, 5.34, 2.42, 0.88, fill=RGBColor(18, 22, 28), line=color, radius=0.05)
        text(slide, label, x + 0.14, 5.44, 1.3, 0.16, size=5.0, color=color, bold=True, font=FONT_MONO, spc=0.8)
        display_value = value.replace("https://", "").replace("http://", "") if PUBLIC_LINKS else value
        text(slide, display_value, x + 0.14, 5.64, 2.08, 0.34, size=6.0 if not PUBLIC_LINKS else 6.2,
             color=WHITE, bold=True, font=FONT_MONO, line_spacing=1.0)
        text(slide, mark, x + 2.10, 5.42, 0.20, 0.18, size=8.0, color=color, bold=True, align=PP_ALIGN.RIGHT)

    # Contact strip.
    text(slide, f"Contact  ·  {CONTACT}", 0.72, 6.75, 5.2, 0.16, size=5.6, color=DIM, font=FONT_MONO)
    text(slide, "Built at Hack-to-Ween 2026  ·  AWS Student Builder Group, IIT Jodhpur", 6.4, 6.75, 6.2, 0.16,
         size=5.6, color=DIM, font=FONT_MONO, align=PP_ALIGN.RIGHT)

    notes(slide,
          "Close with a concrete ask, not a vague vision. Today: a working triage demo. Next: design partners who "
          "want a 10-minute setup. The roadmap is intentionally staged: connectors, then workflows, then compliance. "
          "We are starting with developers and labs because they feel the pain first and can adopt without a procurement cycle.")


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def build(output: Path) -> Path:
    prs = Presentation()
    prs.slide_width = Inches(SLIDE_W)
    prs.slide_height = Inches(SLIDE_H)

    slide_title(prs)
    slide_problem(prs)
    slide_solution(prs)
    slide_architecture(prs)
    slide_demo(prs)
    slide_theme(prs)
    slide_scale(prs)
    slide_roadmap(prs)

    # Core properties for a polished handoff.
    prs.core_properties.title = "GhostProtocol — Zombie Credential & Phishing Exorcist"
    prs.core_properties.subject = "Hack-to-Ween 2026 pitch deck"
    prs.core_properties.author = TEAM_NAME
    prs.core_properties.keywords = "cloud security, AWS, secrets, phishing, threat triage, hackathon"
    prs.core_properties.comments = "Generated with python-pptx. Edit constants at the top of ghostprotocol_deck.py."

    output = output.resolve()
    prs.save(output)
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate the GhostProtocol Hack-to-Ween 2026 deck.")
    parser.add_argument("--out", default=OUTPUT_FILE, help=f"Output .pptx path (default: {OUTPUT_FILE})")
    args = parser.parse_args()
    out = build(Path(args.out))
    print(f"Created: {out}")
    print(f"Slides: 8  ·  Format: 16:9  ·  Background: #{_hex(BG)}")


if __name__ == "__main__":
    main()
