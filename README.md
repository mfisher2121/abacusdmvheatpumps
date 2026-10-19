# DMV Heat Pumps: funnel, landing pages and launch assets

Everything needed to turn dmvheatpumps.com into a working, consent-first funnel for the Nov 30 / Dec 31, 2026 rebate dates and beyond.

## What's here

| Folder | What |
|---|---|
| `pages/` | 15 pages: home, 2-minute checker, MD/DC/VA landing pages, alerts, Before You Sign (+ printable checklist), neighbors share kit, installers, buildings, Mbraceables + Craftsman nominations, thanks, privacy, 404 |
| `data/facts.json` | **Every number on the site**, each with its official source and checked date. Change facts here only. |
| `static/` | CSS, `funnel.js` (forms, referral links, share buttons, events), `check.js` (checker), `neighbors.js` (QR flyer), social cards, installer badge |
| `api/lead.js` | Vercel function behind every form. Validates, records consent, forwards to your automation. |
| `marketing/` | Funnel map, 10-week launch plan, email sequences, 30-day social calendar, video scripts, press/partner/installer outreach |
| `build.py` | Builds `public/` from the above. Fails if a banned word gets in ("verified," "best," "guaranteed"… and the AI-tells list). |
| `make_cards.py` | Regenerates the social card images from the same facts. |

## Build

```bash
python3 make_cards.py   # only when card text or facts change
python3 build.py        # writes public/
```

Needs Python 3.9+. `rsvg-convert` (installed) renders the PNG cards.

## Deploy (Vercel)

1. `vercel` in this folder (or connect it as a new Vercel project). `vercel.json` already sets the build.
2. Vercel → Settings → Environment Variables:
   - `LEAD_WEBHOOK_URL`: your n8n / Make / Zapier webhook (below)
   - `LEAD_WEBHOOK_SECRET`: any long random string; check it in the workflow
3. Point the domain at it.

**Until `LEAD_WEBHOOK_URL` is set, every form shows the "email us" fallback.** Leads are never silently dropped.

## The lead workflow (n8n on the Pi, or Make)

Webhook → check `X-Lead-Secret` → branch on `type`:

| `type` | Do this |
|---|---|
| `summary` | Send email 1 (02-email-sequences.md) with the programs in `answers.matched`. If `consent_email_alerts`, add to Alerts. If `consent_newsletter`, add to Newsletter. |
| `checklist` | Send email 2. Same optional list adds. |
| `alerts` | Add to Alerts with double opt-in (email 3a). If `consent_sms`, add to SMS with a "Reply YES" confirmation. |
| `champion` | Save `ref` + email. Each new lead whose `came_from` matches that `ref` adds one. At 3, send email 5b. |
| `match_interest` | Email the person installer names. Share nothing until they consent to those named installers. |
| `installer_apply`, `buildings`, `neighbor_night`, `craftsman_nomination`, `newsletter`, `area_waitlist` | Save to Airtable and send the matching email. |

Always save the whole payload, including `consent_record` (time, IP, page, exact consent text), to an Airtable "Consent log" table.

## Decisions only you can make

1. **Domain setup.** This is built for dmvheatpumps.com. The marylandheatpumprebates.com site could 301 to `/maryland/`, or stay as its own SEO page that links here. One constant in `build.py`.
2. **Sticker pack.** The Neighbor Champion thank-you is a promise. Keep it only if you'll mail them. Otherwise edit `/neighbors/` and `/thanks/`.
3. **Installer pricing.** Pages say "founding pricing, ask for rates." Set the numbers when ready.
4. **Hootie vs. Whisper for the audit.** Following the brand plan, Whisper guides the audit; Hootie appears on the buildings page.
5. **Mailing address** for the email footer (required by CAN-SPAM).

## Before launch: please check

- **Privacy notice** (`pages/privacy.html`) is a plain-language draft written to match what the code actually does. Have counsel review it for MODPA, TCPA / Maryland Stop the Spam Calls Act (SMS), and DC/VA.
- **Recheck every source** in `facts.json` after the PSC hearings (Oct 30), then weekly through Dec 31. Update the `checked` dates only after re-opening each URL.
- **Character art.** The round character faces are placeholders. Replace `char_svg()` in `build.py` with the felted-plush art when it's ready; the whole site and every card update.

## Found in the existing marylandheatpumprebates.com project (Desktop/DMVHEATPUMPS@@)

- **Its `api/` folder is empty, so every form on that site posts to an endpoint that doesn't exist.** Copy `api/lead.js` from here into it. It accepts that site's field names too (`homeowner`, `contractor`, `property-manager`, `alerts`).
- **Its installer-share box is pre-checked** ("Share my request with up to three installers near me", `build.py` line ~511). That breaks the unchecked-box rule, and the lead spec requires naming the installers first. Remove `checked`.
- Its `programs.json` uses the key `"verified"` and `build.py` prints "verified" dates. Rename the label to "Last checked" per the brand rule.
