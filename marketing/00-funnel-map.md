# The DMV Heat Pumps funnel

One idea runs the whole thing: **give away the most useful, most honest thing first, and make it easy for people to hand it to a neighbor.** The brand rules (sourced facts, no fake urgency, consent-only) are not a drag on growth here. They're the reason people will forward it. Nobody forwards a sales pitch to their neighbor. People do forward "this checks the official pages and the deadline is Nov 30."

## The map

```
 HOW PEOPLE ARRIVE              WHAT THEY GET FREE               WHAT WE ASK FOR            WHAT HAPPENS NEXT
 ─────────────────              ─────────────────                ───────────────            ─────────────────
 Google: "md heat pump rebates" → /maryland/, /dc/, /virginia/ ─┐
 Nextdoor / FB groups / texts  → /check/ (via a neighbor's link) │
 Local press (PSC, Nov 30)     → /maryland/                      ├→ 2-minute check ──→ Email my summary ──→ Summary email
 Installer's "Listed" badge    → /                               │   (anonymous)        Checklist           → Alerts (if yes)
 Flyers + porch talks (QR)     → /check/?ref=…                   │                      Alerts              → Newsletter (if yes)
 Google Business Profile posts → /                              ─┘                      Installer names     → Installer names → consent → match
                                                                                                │
                                         ┌──────────────────────────────────────────────────────┘
                                         ▼
                              /thanks/ "send this to one neighbor"  →  their personal ?ref link  →  next household
                              Neighbor Champion (3 neighbors → sticker pack thank-you)
                              Craftsman of the Month nominations → installers share their feature
```

## The three loops that make it spread

1. **Neighbor loop (homeowners).** Every results page and thank-you page asks for one share, with ready-made text. Each share carries a random `?ref=` code. When three people use your link, you get a thank-you. This is the main growth engine. It works hardest in the weeks before Nov 30 and Dec 31, because then there's a real, sourced reason to tell someone *now*.
2. **Craftsman loop (trades).** Nominations come from customers and peers. When we feature someone, they share it with their whole customer list and crew. The "Listed on DMV Heat Pumps" badge on installer sites sends their visitors back here.
3. **Community loop (in person).** Porch talks, HOA emails, church and library talks. A QR flyer turns one room into twenty checks. That's slow to start, but it builds the trust that makes everything else work.

## What we measure (community numbers first)

| Metric | Why | Where it comes from |
|---|---|---|
| **Official apply-link clicks** (North Star) | Someone went to the real program. That's the job. | `official_apply_click` event |
| Neighbors helped | Checks completed + summaries sent | `check_complete`, `summary` leads |
| Share rate | % of completed checks that tap a share button | `share_click` / `check_complete` |
| Arrivals by share | People who came from a neighbor's link | `arrived_by_share` event, `came_from` on leads |
| K-factor (rough) | arrivals by share ÷ people who shared | the two above |
| Installer applications | Supply side | `installer_apply` leads |

A K-factor over 1 means each person brings in more than one more, and it grows on its own. Most campaigns land well under 1; the realistic goal is to push the share rate up, so every paid or press visit brings extra people with it. Check these numbers weekly; anything under ~5% share rate means the share ask needs work.

## Events (no personal data in any event)

`check_start`, `check_complete {where, project}`, `share_click {channel, where}`, `arrived_by_share {channel}`, `lead_submit {type}`, `official_apply_click {program}`. Set `PLAUSIBLE_DOMAIN` in `build.py` to turn them on. Plausible is cookieless, so no banner is needed.
