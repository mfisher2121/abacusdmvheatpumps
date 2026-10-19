# Email sequences

Voice: warm, short, plain, like a kind neighbor. Every dollar or date links to its official source with the date we checked it. No "verified," "best," "guaranteed." Every email has a one-click unsubscribe and the footer below. `{{…}}` are merge fields from the lead payload.

**Footer (every email):**
> You're getting this because you asked for it at dmvheatpumps.com on {{consent_record.at}}. [Unsubscribe in one click]({{unsubscribe}}). We never sell your information.
> General information, not legal, tax or financial advice. Programs decide who qualifies and how much. DMV Heat Pumps · {{mailing_address}}

---

## 1. Summary (type `summary`, sent once, right away)

**Subject:** Your heat pump rebate summary ({{answers.where}})
**Preview:** The programs that may fit, with the official links.

Hi there,

Here's what your 2-minute check found. Each program below is in its own words, with a link to the official page so you (or your installer) can check it yourself.

{{#each matched_programs}}
**{{name}}** · {{status_label}}
{{amount}}
{{status_note}}
Official page: {{sources[0].url}} (checked {{checked}})
{{/each}}

**Your plan, in order:** 1) energy audit, 2) air sealing, 3) insulation, 4) a heat pump sized with a Manual J. Fixing the house first often means a smaller, cheaper system.

**Before you sign anything:** here are the 12 questions to ask any installer → {{site}}/before-you-sign/checklist/

**One favor:** if someone on your street heats with gas, oil or propane, forward them this link: {{site}}/check/?ref={{ref}}

Take your time. Compare a few quotes.
Max, for the DMV Heat Pumps community

---

## 2. Checklist (type `checklist`, sent once, right away)

**Subject:** Your Before You Sign checklist
**Preview:** 12 questions to ask any heat pump installer.

Hi,

Here it is: {{site}}/before-you-sign/checklist/ (print it, or save it as a PDF from your browser).

The three questions people tell us matter most:
- **Will you list each incentive on the contract as its own line?**
- **Did you do a room-by-room Manual J? Can I have a copy?**
- **Are you counting on a federal tax credit?** In 2026, the answer should be no. The IRS 25C credit ended for heat pumps placed in service after Dec 31, 2025 ([IRS](https://www.irs.gov/credits-deductions/energy-efficient-home-improvement-credit), checked Oct 16, 2026).

Good installers are glad you asked.
Max

---

## 3. Alerts: confirm + welcome (type `alerts`)

**3a. Confirm (double opt-in, right away)**
**Subject:** One click to confirm your deadline alerts
Please confirm so the alerts reach you: [Yes, send me alerts]({{confirm}}). If you didn't ask for this, ignore this email and you won't hear from us.

**3b. Welcome (after confirm)**
**Subject:** You're on the list. Here's what we're watching.
Thanks for joining. We'll email you before each of these, about 1 to 4 times a month:
- **Oct 26–29:** Maryland PSC hearings on 2027–2029 EmPOWER plans ([PSC schedule](https://webpscxb.pscmaryland.com/DMS/hearing), checked Oct 16, 2026)
- **Nov 30:** Pepco and Delmarva: installs finished for the higher switching amounts ([Pepco](https://homeenergysavings.pepco.com/md/residential/hvac-efficiency-program/participating-distributors), checked Oct 16, 2026)
- **Dec 1:** Washington Gas (MD) applications and papers
- **Dec 31:** Pepco Home Performance reservations; Potomac Edison installs

Haven't run the check yet? {{site}}/check/

---

## 4. Deadline alerts (send to `consent_email_alerts = true`, filter by `where`/`electric_utility`)

Recheck every source the day before sending. If anything changed, say what changed.

**Nov 16 · Subject:** Two weeks until Nov 30 (Pepco & Delmarva)
Switching from gas, oil or propane in Pepco or Delmarva territory? The higher switching amounts need the install **finished** by Nov 30, 2026 ([Pepco](https://homeenergysavings.pepco.com/md/residential/hvac-efficiency-program/participating-distributors), checked {{date}}). If you have a quote, ask your installer in writing: "Will this be finished by Nov 30? What happens to my price if it slips?" Not in Pepco or Delmarva? Your dates are Dec 31. Nothing to do this week.

**Nov 23 · Subject:** One week until Nov 30
Short version: same as last week, seven days closer. If the timing is too tight, that's OK. Dec 31 dates still apply for Home Performance (Pepco) and Potomac Edison. A rushed install is worse than a missed bonus. → {{site}}/check/

**Dec 1 · Subject:** Today: Washington Gas (Maryland) paperwork
If you have an open Washington Gas EmPOWER application, today is the date to have your papers in. The programs end Dec 31, 2026 under House Bill 1532 ([Washington Gas](https://wgsmartsavings.com/programs-rebates/home/md), checked {{date}}).

**Dec 17 · Subject:** Two weeks left in 2026's rebate cycle
Pepco Home Performance: your contractor must reserve your rebates by Dec 31. Potomac Edison: equipment bought and installed by Dec 31. Everything after that depends on the PSC. We'll email you the day 2027 amounts are set.

**PSC decision · Subject:** 2027 Maryland rebate amounts are out
Here's what changed, program by program, with links. [Fill in from the official order the day it posts. Recheck every amount.]

---

## 5. Neighbor Champion (type `champion`)

**On signup · Subject:** Your neighbor link is saved
Your link: {{site}}/check/?ref={{ref}}. When three neighbors use it to get their summary, checklist or alerts, we'll write to you for a mailing address for your Mbraceables sticker pack. It's a thank-you for sharing, never for a review.

**At 3 · Subject:** You helped three neighbors 🎉
Three households on your street checked their rebates because of you. That's the whole point of this. Reply with a mailing address and we'll send your sticker pack. (Adults only; we never collect anything from kids.)

---

## 6. Installer listing (type `installer_apply`)

**Right away · Subject:** We got your listing request
Thanks, {{first_name}}. Next we'll look up license {{license}} on the official {{where}} site, read your public reviews, and send you a draft listing within a week to correct before it goes live. Listings are never for sale, and we never tell homeowners a listing means approval. The badge says exactly what it is: "Listed on DMV Heat Pumps."

**When live · Subject:** You're listed. Here's your badge.
Your listing: {{listing_url}}. Badge code for your site:
`<a href="https://dmvheatpumps.com{{listing_path}}"><img src="https://dmvheatpumps.com/assets/badge-listed.svg" alt="Listed on DMV Heat Pumps" width="180"></a>`
The deadline cheat sheet for your team: {{site}}/installers/#cheatsheet
