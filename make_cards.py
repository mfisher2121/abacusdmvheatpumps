#!/usr/bin/env python3
"""Make the social card SVGs in static/og/ (link previews, 1200x630) and
static/social/ (posts: 1080x1080 square, 1080x1920 story). build.py renders
them to PNG with rsvg-convert.
    python3 make_cards.py && python3 build.py
Card text that states a date or amount carries its source line, like the site.
"""
import os
from html import escape as e

from build import FACTS, char_svg, nice

ROOT = os.path.dirname(os.path.abspath(__file__))
BG, INK, MUTED, ACCENT, HEART, WARN, PAPER = "#f7f4ef", "#1a2332", "#5c6b7a", "#0c5c4c", "#d4506f", "#9a5b00", "#ffffff"
MD = nice(FACTS["checked"]["MD"])


def char(key, x, y, size):
    return char_svg(key, size).replace("<svg ", f'<svg x="{x}" y="{y}" ', 1)


def lines(texts, x, y, size, color=INK, weight="700", family="Georgia, serif", lh=1.18, anchor="start"):
    out = []
    for i, t in enumerate(texts):
        out.append(f'<text x="{x}" y="{y + i * size * lh:.0f}" font-family="{family}" font-size="{size}" font-weight="{weight}" fill="{color}" text-anchor="{anchor}">{e(t)}</text>')
    return "".join(out)


def sans(texts, x, y, size, color=MUTED, weight="400", anchor="start", lh=1.4):
    return lines(texts, x, y, size, color, weight, "Helvetica Neue, Helvetica, Arial, sans-serif", lh, anchor)


def frame(w, h, inner, bg=BG):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f'<rect width="{w}" height="{h}" fill="{bg}"/>{inner}</svg>')


def brandmark(x, y, color=INK):
    return sans(["DMV Heat Pumps"], x, y, 30, color, "700") + sans(["Community first. Success follows."], x, y + 38, 24, MUTED)


def og(name, eyebrow, title, sub, chars):
    inner = (f'<rect x="0" y="0" width="1200" height="12" fill="{ACCENT}"/>'
             + sans([eyebrow.upper()], 70, 110, 24, ACCENT, "700")
             + lines(title, 70, 180, 56)
             + sans(sub, 70, 180 + len(title) * 66 + 30, 28)
             + brandmark(70, 540))
    for i, k in enumerate(chars):
        inner += char(k, 935 + (i % 2) * 125, 110 + (i // 2) * 160 + (i % 2) * 60, 125)
    write("og", name, frame(1200, 630, inner))


def write(folder, name, svg):
    d = os.path.join(ROOT, "static", folder)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, name + ".svg"), "w") as f:
        f.write(svg)


def square(name, eyebrow, title, body, src, key, accent=ACCENT, dark=False):
    bg, ink, muted = (INK, "#ffffff", "#c9d3dc") if dark else (BG, INK, MUTED)
    inner = (f'<rect x="60" y="60" width="960" height="960" rx="40" fill="{PAPER if not dark else "#16212c"}"/>'
             + sans([eyebrow.upper()], 120, 170, 30, accent, "700")
             + lines(title, 120, 270, 78, ink)
             + sans(body, 120, 270 + len(title) * 92 + 40, 34, muted)
             + char(key, 760, 700, 220)
             + sans(src, 120, 900, 22, muted)
             + sans(["dmvheatpumps.com"], 120, 960, 30, ink, "700"))
    write("social", name, frame(1080, 1080, inner, bg))


def story(name, eyebrow, title, body, src, key):
    inner = (sans([eyebrow.upper()], 90, 300, 40, ACCENT, "700")
             + lines(title, 90, 420, 104)
             + sans(body, 90, 420 + len(title) * 122 + 50, 44)
             + char(key, 640, 1180, 330)
             + f'<rect x="90" y="1600" width="900" height="130" rx="65" fill="{ACCENT}"/>'
             + sans(["Free 2-minute check · dmvheatpumps.com"], 540, 1680, 40, "#ffffff", "700", "middle")
             + sans(src, 90, 1800, 26))
    write("social", name, frame(1080, 1920, inner))


if __name__ == "__main__":
    # link previews
    og("og-default", "DC · Maryland · Northern Virginia", ["Find the heat pump rebates", "your home can use."], ["Official sources only. Dated. No sales calls."], ["whisper", "sparky", "fluffle", "scout"])
    og("og-check", "2-minute rebate check", ["Which rebates may", "fit your home?"], ["A few quick taps. No email needed to see results."], ["kevin", "whisper"])
    og("og-alerts", "Deadline alerts", ["Hear about the deadline", "before it passes."], ["An email before Nov 30, Dec 31, and the 2027 decision."], ["scout", "sparky"])
    og("og-checklist", "Free checklist", ["Before You Sign:", "12 questions to ask", "your installer."], [], ["kevin", "whisper"])
    og("og-neighbors", "Neighbors helping neighbors", ["Help your street catch", "the rebates in time."], ["Your own link, a flyer, and a porch-talk kit."], ["willie", "petal"])
    og("og-installers", "For installers", ["Homeowners who did", "their homework are", "looking for you."], [], ["sparky", "willie"])
    og("og-buildings", "Property managers · boards · HOAs", ["BEPS and building", "programs, sourced."], ["DC, Maryland and Northern Virginia."], ["hootie", "kevin"])
    og("og-maryland", f"Maryland · checked {MD}", ["Maryland heat pump", "rebates: what's open,", "what's ending."], [], ["sparky", "fluffle"])
    og("og-dc", f"Washington, DC · checked {nice(FACTS['checked']['DC'])}", ["DC heat pump rebates", "for any income."], ["Plus no-cost help if you qualify."], ["petal", "whisper"])
    og("og-virginia", f"Northern Virginia · checked {nice(FACTS['checked']['VA'])}", ["Northern Virginia", "heat pump rebates."], ["Start with the audit."], ["scout", "hootie"])
    og("og-mbraceables", "The Mbraceables", ["Tiny friends.", "Big feelings.", "Brave choices."], [], ["kevin", "whisper", "willie", "fluffle"])

    # campaign posts (square)
    pepco = "Source: Pepco HVAC Efficiency Program, checked " + MD
    square("sq-nov30", "Maryland · Pepco & Delmarva", ["Switching from", "gas, oil or propane?"],
           ["The higher switching amounts need", "the install finished by Nov 30, 2026."], [pepco], "sparky", WARN)
    square("sq-25c", "Myth check", ["The federal 25C", "credit is over."],
           ["It ended for heat pumps placed in", "service after Dec 31, 2025. If a 2026", "quote counts on it, ask why."], ["Source: IRS, Energy Efficient Home Improvement Credit, checked " + MD], "scout", ACCENT)
    square("sq-envelope", "The envelope-first order", ["Fix the house", "before the", "heat pump."],
           ["1 Audit  2 Air sealing  3 Insulation", "4 A heat pump sized with a Manual J"], [""], "fluffle", ACCENT)
    square("sq-psc", "Maryland · Under review", ["2027 rebate amounts", "are being decided."],
           ["PSC hearings Oct 26-29, 2026.", "Utilities filed plans with 30% and 45% cuts."], ["Source: Maryland PSC hearing schedule, Case No. 9890, checked " + MD], "hootie", "#1f4f8a")
    square("sq-community", "Mbrace", ["Community first.", "Success follows."],
           ["We measure how well we help,", "not how much we sell."], [""], "kevin", HEART, dark=True)
    square("sq-questions", "Before you sign", ["Ask for the", "Manual J.", "In writing."],
           ["One of 12 questions in our free", "Before You Sign checklist."], [""], "whisper", ACCENT)

    # stories
    story("story-nov30", "Maryland · Pepco & Delmarva", ["Nov 30 is", "closer than", "it looks."], ["Switching from gas, oil or propane?", "The higher amounts need the", "install finished by then."], [pepco], "sparky")
    story("story-neighbor", "Send this to one neighbor", ["Most people", "hear about it", "too late."], ["A free 2-minute check of the", "heat pump rebates near you."], [""], "willie")
    print("Cards written to static/og/ and static/social/")
