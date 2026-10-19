# Launch plan: Oct 20 – Jan 2027

The next ten weeks have real, sourced dates. That's the closest thing to a viral moment this category gets: a true reason to tell someone *this week*. Every date below is in `data/facts.json` with its source. **Recheck the sources before each push** (next check: Oct 30, after the PSC hearings).

## Week 0 · Oct 20–25 · Get it live

- [ ] Pick the domain setup (see README "Decisions"). Deploy to Vercel.
- [ ] Set `LEAD_WEBHOOK_URL` and build the n8n/Make workflow (README has the steps). Test every form once.
- [ ] Load the emails in `02-email-sequences.md` into your email tool. Turn on double opt-in for alerts.
- [ ] Set up Plausible (or Umami on the Pi) and fill in `PLAUSIBLE_DOMAIN`.
- [ ] Copy `api/lead.js` into the marylandheatpumprebates.com project too. Its forms post to `/api/lead`, and that folder is empty today, so **every lead on that site is currently lost.** Also uncheck its pre-checked "Share my request" box.
- [ ] Send the 10 people you know who heat with gas or oil the link, and ask for brutal feedback.

## Week 1 · Oct 26–Nov 1 · The PSC hearings

The PSC hears the 2027–2029 EmPOWER plans Oct 26–29. Utilities filed with 30% and 45% cuts. It's news, and it's the hook.

- [ ] Mon: post `sq-psc` everywhere. Pitch local press (`05-press-and-partners.md`, pitch A).
- [ ] Email HOAs and civic associations in Montgomery, Prince George's, Howard and Frederick (template in 05).
- [ ] Oct 30: recheck every source. Update `facts.json` if anything changed, rebuild, and send an alert if it did.
- [ ] Ask 3 installers you respect to apply for a listing. Their customers are your next wave.

## Weeks 2–5 · Nov 2–30 · The Nov 30 push (Pepco & Delmarva switching amounts)

- [ ] Weekly: one post from the 30-day calendar per channel per day (see 03).
- [ ] Nov 9: Nextdoor post in every neighborhood you can reach (script in `/neighbors/`).
- [ ] Nov 16: alert email "Two weeks until Nov 30."
- [ ] Nov 20-ish: first Craftsman of the Month feature. Ask them to share it.
- [ ] Nov 23: alert "One week." Post `story-nov30`.
- [ ] Every Friday: look at the share rate. Change one thing about the share ask if it's under 5%.

## Weeks 6–10 · Dec 1–31 · The year-end dates

Dec 1 (Washington Gas MD papers), Dec 31 (Pepco Home Performance reservations, Potomac Edison installs).

- [ ] Dec 1 and Dec 17 alert emails.
- [ ] Shift the story from "deadline" to "the audit first": book it now, decide in January.
- [ ] Porch talks and community nights before the holidays.

## January · The PSC decision

When the PSC sets 2027 amounts, that's the second news moment. Recheck and update `facts.json` the same day, then email everyone on alerts. Update the checker, and repitch press with "what changed."

## Paid (optional, small)

If you spend, spend on the moments: $10–20/day on Meta and Google, aimed at ZIPs in Pepco and Delmarva territory, Oct 26 to Nov 30. Send the traffic to `/maryland/`. Keep ad pixels off until there's a consent banner (brand rule). Use UTM links and cookieless conversion counts.
