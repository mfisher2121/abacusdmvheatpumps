#!/usr/bin/env python3
"""Build the DMV Heat Pumps funnel into ./public.

Pages live in pages/*.html. Each starts with a header comment:
    <!--
    path: /check/
    title: Page title
    description: Meta description
    theme: ops            (optional: dark installer look)
    og: og-check          (optional: social card name in static/og/)
    -->
Tokens like {{DEADLINES}} are filled from data/facts.json, so every number
on the site has one home. Update facts.json, then run:
    python3 build.py
The build fails if a banned word appears in any page (brand rules).
"""
import datetime as dt
import html
import json
import os
import re
import shutil
import subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "public")

# ---- settings (change here, nowhere else) ----
SITE = "https://dmvheatpumps.com"
BRAND = "DMV Heat Pumps"
EMAIL = "hello@dmvheatpumps.com"
PLAUSIBLE_DOMAIN = ""  # e.g. "dmvheatpumps.com" once Plausible or Umami is set up; empty = no analytics

FACTS = json.load(open(os.path.join(ROOT, "data", "facts.json")))


def e(s):
    return html.escape(str(s), quote=True)


def nice(iso):
    return dt.date.fromisoformat(iso).strftime("%b %-d, %Y")


# ---- character tokens (placeholders until the felted-plush art is dropped in) ----
CHARS = {
    "whisper": ("Whisper", "kitten", "Listens first", "#c99b6d", "pointy"),
    "scout": ("Scout", "raccoon", "Checks the source", "#8d929c", "round-mask"),
    "fluffle": ("Fluffle", "bunny", "Wraps your home in a hug", "#f0c9d4", "long"),
    "sparky": ("Sparky", "dragon", "Courage to switch", "#7cc49c", "horns"),
    "kevin": ("Kevin", "koala", "One step at a time", "#9ea8b3", "fluffy"),
    "willie": ("Willie", "wombat", "Knows every neighbor", "#a77f5f", "round"),
    "petal": ("Petal", "fawn", "Care after the install", "#d8a56f", "pointy"),
    "hootie": ("Hootie", "owl", "The wise listener", "#9c7b5c", "tufts"),
}


def char_svg(key, size=84):
    name, animal, _, color, ears = CHARS[key]
    ear = {
        "pointy": '<path d="M22 30 L28 6 L44 24Z M78 30 L72 6 L56 24Z" fill="{c}"/><path d="M27 24 L30 13 L37 22Z M73 24 L70 13 L63 22Z" fill="#f6c6cf"/>',
        "round": '<circle cx="24" cy="24" r="11" fill="{c}"/><circle cx="76" cy="24" r="11" fill="{c}"/>',
        "round-mask": '<circle cx="24" cy="24" r="11" fill="{c}"/><circle cx="76" cy="24" r="11" fill="{c}"/>',
        "fluffy": '<circle cx="18" cy="30" r="17" fill="{c}"/><circle cx="82" cy="30" r="17" fill="{c}"/><circle cx="18" cy="30" r="9" fill="#e9e2ea"/><circle cx="82" cy="30" r="9" fill="#e9e2ea"/>',
        "long": '<ellipse cx="36" cy="14" rx="8" ry="22" fill="{c}"/><ellipse cx="64" cy="14" rx="8" ry="22" fill="{c}"/><ellipse cx="36" cy="16" rx="4" ry="15" fill="#fff3f6"/><ellipse cx="64" cy="16" rx="4" ry="15" fill="#fff3f6"/>',
        "horns": '<ellipse cx="36" cy="20" rx="5" ry="10" fill="#f6d27a"/><ellipse cx="64" cy="20" rx="5" ry="10" fill="#f6d27a"/><path d="M44 24 Q50 14 56 24Z" fill="#5aa77e"/>',
        "tufts": '<path d="M24 32 L22 12 L40 26Z M76 32 L78 12 L60 26Z" fill="{c}"/>',
    }[ears].format(c=color)
    mask = '<path d="M26 52 Q50 40 74 52 Q66 64 50 58 Q34 64 26 52Z" fill="#3b3f47"/>' if ears == "round-mask" else ""
    return (
        f'<svg viewBox="0 0 100 100" width="{size}" height="{size}" role="img" aria-label="{e(name)} the {e(animal)}">'
        f'{ear}<circle cx="50" cy="56" r="34" fill="{color}"/>{mask}'
        '<circle cx="39" cy="54" r="4.2" fill="#1a2332"/><circle cx="61" cy="54" r="4.2" fill="#1a2332"/>'
        '<circle cx="40.4" cy="52.6" r="1.4" fill="#fff"/><circle cx="62.4" cy="52.6" r="1.4" fill="#fff"/>'
        '<ellipse cx="50" cy="64" rx="4" ry="3" fill="#1a2332" opacity=".75"/>'
        '<circle cx="30" cy="66" r="5" fill="#f19aae" opacity=".55"/><circle cx="70" cy="66" r="5" fill="#f19aae" opacity=".55"/>'
        "</svg>"
    )


def friend(key, line):
    name, animal, *_ = CHARS[key]
    return f'<div class="friend">{char_svg(key, 44)}<span><i>{e(name)} the {e(animal)}:</i> “{e(line)}”</span></div>'


def cast_html():
    return '<div class="cast">' + "".join(
        f'<div class="card token">{char_svg(k)}<b>{e(v[0])}</b><span>{e(v[2])}</span></div>' for k, v in CHARS.items()
    ) + "</div>"


# ---- facts-driven fragments ----
def deadlines_html(juris=None, limit=None):
    today = dt.date.today().isoformat()
    items = [d for d in FACTS["deadlines"] if (d.get("end") or d["date"]) >= today and (not juris or d["juris"] in juris)]
    if limit:
        items = items[:limit]
    rows = []
    for d in items:
        day = dt.date.fromisoformat(d["date"])
        span = f'{day.day}' if not d.get("end") else f'{day.day}–{dt.date.fromisoformat(d["end"]).day}'
        left = "" if d["status"] == "review" else f' <span class="days-left" data-days-until="{d["date"]}"></span>'
        rows.append(
            f'<li class="dl-{d["status"]}"><div class="dl-date"><small>{day.strftime("%b")}</small><span>{span}</span></div>'
            f'<div><h3>{e(d["title"])}{left}</h3><p>{e(d["detail"])}</p>'
            f'<p class="src">Source: <a href="{e(d["source"]["url"])}" target="_blank" rel="noopener" data-official="deadline">{e(d["source"]["label"])}</a>, checked {nice(FACTS["checked"][d["juris"]])}</p></div></li>'
        )
    return '<ul class="deadlines">' + "".join(rows) + "</ul>"


STATUS_LABEL = {"open": "In effect", "ending": "Ending", "review": "Under review", "upcoming": "Not yet live",
                "not-launched": "Not yet live", "closed": "Expired", "ended": "Expired"}
STATUS_ORDER = {"open": 0, "ending": 0, "upcoming": 2, "not-launched": 3, "closed": 4, "ended": 5}


def programs_html(juris):
    items = sorted((p for p in FACTS["programs"] if p["juris"] in (juris, "ALL")), key=lambda p: STATUS_ORDER[p["status"]])
    cards = []
    for p in items:
        src = " · ".join(
            f'<a href="{e(s["url"])}" target="_blank" rel="noopener" data-official="{e(p["id"])}">{e(s["label"])}</a>' for s in p["sources"]
        )
        cards.append(
            f'<article class="card prog-card st-{p["status"]}"><p class="mt0"><span class="badge badge-{p["status"]}">{STATUS_LABEL[p["status"]]}</span></p>'
            f'<h3>{e(p["name"])}</h3><p class="amount">{e(p["amount"])}</p><p class="small">{e(p["status_note"])}</p>'
            f'<p class="small muted">{e(p["note"])}</p><p class="src">Sources: {src}. Checked {nice(FACTS["checked"][juris])}.</p></article>'
        )
    return '<div class="grid">' + "".join(cards) + "</div>"


def facts_js():
    slim = {k: FACTS[k] for k in ("checked", "deadlines", "programs", "utilities")}
    return "window.FACTS=" + json.dumps(slim, separators=(",", ":")) + ";"


# ---- layout ----
NAV = [
    ("/check/", "Check rebates"),
    ("/alerts/", "Deadline alerts"),
    ("/before-you-sign/", "Before you sign"),
    ("/neighbors/", "Neighbors"),
    ("/installers/", "For installers"),
    ("/buildings/", "Buildings"),
]


def layout(meta, body):
    path = meta["path"]
    theme = meta.get("theme", "")
    og = meta.get("og", "og-default")
    nav = "".join(f'<a href="{p}"{" aria-current=page" if p == path else ""}>{e(t)}</a>' for p, t in NAV[1:])
    analytics = (
        f'<script defer data-domain="{e(PLAUSIBLE_DOMAIN)}" src="https://plausible.io/js/script.outbound-links.js"></script>'
        '<script>window.plausible=window.plausible||function(){(window.plausible.q=window.plausible.q||[]).push(arguments)}</script>'
        if PLAUSIBLE_DOMAIN else ""
    )
    noindex = '<meta name="robots" content="noindex">' if meta.get("noindex") else ""
    md = nice(FACTS["checked"]["MD"])
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(meta["title"])}</title>
<meta name="description" content="{e(meta["description"])}">
<link rel="canonical" href="{SITE}{path}">
{noindex}
<meta property="og:type" content="website">
<meta property="og:site_name" content="{BRAND}">
<meta property="og:title" content="{e(meta["title"])}">
<meta property="og:description" content="{e(meta["description"])}">
<meta property="og:url" content="{SITE}{path}">
<meta property="og:image" content="{SITE}/assets/og/{og}.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="{"#0f1720" if theme == "ops" else "#f7f4ef"}">
<link rel="icon" href="/assets/icon.svg" type="image/svg+xml">
<link rel="stylesheet" href="/assets/site.css">
{analytics}
<script>window.MB={{site:"{SITE}",email:"{EMAIL}"}};</script>
</head>
<body class="{"theme-ops" if theme == "ops" else ""}">
<a class="skip" href="#main">Skip to content</a>
<header class="top"><div class="wrap top-row">
<a class="brand" href="/">{char_svg("kevin", 28)}<span>DMV <b>Heat Pumps</b></span></a>
<button class="menu-btn" aria-expanded="false" aria-label="Menu">Menu</button>
<nav>{nav}<a class="btn btn-sm" href="/check/">Check my rebates</a></nav>
</div></header>
<div class="factbar"><div class="wrap">Every rebate fact links to its official source. Maryland facts checked {md}. Next check {nice(FACTS["next_check"])}.</div></div>
<main id="main">
{body}
</main>
<footer><div class="wrap cols">
<div><p><b class="heart">♥</b> <b>Community first. Success follows.</b></p>
<p>DMV Heat Pumps is part of Mbrace. We help neighbors in DC, Maryland and Northern Virginia learn, check the facts, and fix the house before the heat pump.</p>
<p class="tiny">General information, not legal, tax or financial advice. Program administrators decide who qualifies and how much. Programs can change or run out of money. Confirm with the program and your contractor before you sign. We don't run any rebate program. A listing is not an endorsement. Found an error? Email <a href="mailto:{EMAIL}">{EMAIL}</a>. We reply within 2 business days.</p></div>
<div><ul><li><a href="/check/">Rebate checker</a></li><li><a href="/alerts/">Deadline alerts</a></li><li><a href="/before-you-sign/">Before You Sign checklist</a></li><li><a href="/neighbors/">Share with neighbors</a></li><li><a href="/mbraceables/">Meet the Mbraceables</a></li></ul></div>
<div><ul><li><a href="/installers/">For installers</a></li><li><a href="/buildings/">For buildings</a></li><li><a href="/privacy/">Privacy</a></li><li><a href="mailto:{EMAIL}">Contact</a></li></ul></div>
</div></footer>
<script src="/assets/funnel.js" defer></script>
{meta.get("scripts", "")}
</body>
</html>
"""


# ---- brand lint ----
BANNED_WORDS = ["verified", "verify", "certified by us", "best", "approved", "guaranteed", "guarantee",
                "act now", "hurry", "limited time only"]


def load_ai_tells():
    path = os.path.join(ROOT, "data", "forbidden_words.txt")
    words, phrases, mode = [], [], None
    if not os.path.exists(path):
        return words, phrases
    for line in open(path):
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        if s == "[WORDS]":
            mode = words
        elif s == "[PHRASES]":
            mode = phrases
        elif mode is not None:
            mode.append(s.lower())
    return words, phrases


def lint(path, doc):
    text = re.sub(r"<script.*?</script>|<style.*?</style>|<svg.*?</svg>", " ", doc, flags=re.S)
    text = html.unescape(re.sub(r"<[^>]+>", " ", text)).lower()
    words, phrases = load_ai_tells()
    hits = [w for w in BANNED_WORDS + words if re.search(r"\b" + re.escape(w) + r"\b", text)]
    hits += [p for p in phrases if p in text]
    if hits:
        raise SystemExit(f"Brand lint failed on {path}: {sorted(set(hits))}")


# ---- build ----
def parse(src):
    m = re.match(r"\s*<!--(.*?)-->\s*", src, re.S)
    meta = dict(
        (k.strip(), v.strip()) for k, v in (ln.split(":", 1) for ln in m.group(1).strip().splitlines() if ":" in ln)
    )
    return meta, src[m.end():]


def fill(body):
    body = body.replace("{{DEADLINES}}", deadlines_html())
    body = re.sub(r"\{\{DEADLINES:([A-Z ]+)\}\}", lambda m: deadlines_html(m.group(1).split()), body)
    body = re.sub(r"\{\{PROGRAMS:([A-Z]+)\}\}", lambda m: programs_html(m.group(1)), body)
    body = body.replace("{{CAST}}", cast_html())
    body = re.sub(r"\{\{CHAR:(\w+)\}\}", lambda m: char_svg(m.group(1)), body)
    body = re.sub(r'\{\{FRIEND:(\w+):([^}]+)\}\}', lambda m: friend(m.group(1), m.group(2)), body)
    for j in ("MD", "DC", "VA"):
        body = body.replace("{{CHECKED_" + j + "}}", nice(FACTS["checked"][j]))
    body = body.replace("{{NEXT_CHECK}}", nice(FACTS["next_check"]))
    body = body.replace("{{SITE}}", SITE).replace("{{EMAIL}}", EMAIL)
    lic = FACTS["license_lookups"]
    for j in lic:
        body = body.replace("{{LICENSE_" + j + "}}", f'<a href="{e(lic[j]["url"])}" target="_blank" rel="noopener" data-official="license">{e(lic[j]["label"])}</a>')
    return body


def render_og():
    """Render static/og/*.svg and static/social/*.svg to PNG (social platforms need PNG)."""
    if not shutil.which("rsvg-convert"):
        print("rsvg-convert not found: social card PNGs not rebuilt")
        return
    for folder in ("og", "social"):
        src = os.path.join(ROOT, "static", folder)
        if not os.path.isdir(src):
            continue
        for f in os.listdir(src):
            if f.endswith(".svg"):
                png = os.path.join(src, f[:-4] + ".png")
                subprocess.run(["rsvg-convert", "-o", png, os.path.join(src, f)], check=True)


def main():
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    render_og()
    shutil.copytree(os.path.join(ROOT, "static"), os.path.join(OUT, "assets"))
    with open(os.path.join(OUT, "assets", "facts.js"), "w") as f:
        f.write(facts_js())
    with open(os.path.join(OUT, "assets", "icon.svg"), "w") as f:
        f.write(char_svg("kevin", 64))

    urls = []
    pages_dir = os.path.join(ROOT, "pages")
    for name in sorted(os.listdir(pages_dir)):
        if not name.endswith(".html"):
            continue
        meta, body = parse(open(os.path.join(pages_dir, name)).read())
        doc = layout(meta, fill(body))
        lint(name, doc)
        dest = os.path.join(OUT, meta["path"].strip("/"), "index.html") if meta["path"] != "/" else os.path.join(OUT, "index.html")
        if meta["path"] == "/404/":
            dest = os.path.join(OUT, "404.html")
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "w") as f:
            f.write(doc)
        if not meta.get("noindex"):
            urls.append(meta["path"])

    today = dt.date.today().isoformat()
    with open(os.path.join(OUT, "sitemap.xml"), "w") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        for u in urls:
            f.write(f"<url><loc>{SITE}{u}</loc><lastmod>{today}</lastmod></url>\n")
        f.write("</urlset>\n")
    with open(os.path.join(OUT, "robots.txt"), "w") as f:
        f.write(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
    print(f"Built {len(urls)} indexed pages into public/")


if __name__ == "__main__":
    main()
