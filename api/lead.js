// POST /api/lead  (Vercel serverless function, Node 18+)
//
// Validates a form submission, attaches a consent record, and forwards it to
// LEAD_WEBHOOK_URL (n8n, Make, Zapier or an Airtable automation). That workflow
// sends the email the person asked for and adds them to the right list.
//
// Env vars (Vercel > Settings > Environment Variables):
//   LEAD_WEBHOOK_URL     required. Where leads go.
//   LEAD_WEBHOOK_SECRET  optional. Sent as the X-Lead-Secret header so the workflow can reject fakes.
//
// If the webhook is missing or fails, this returns an error so the page shows the
// "email us" fallback. A lead is never silently dropped.

const TYPES = new Set([
  'summary', 'alerts', 'checklist', 'match_interest', 'area_waitlist', 'champion',
  'neighbor_night', 'installer_apply', 'buildings', 'craftsman_nomination', 'newsletter',
  // type values used by the marylandheatpumprebates.com forms
  'homeowner', 'contractor', 'property-manager'
]);

const TEXT_FIELDS = [
  'email', 'first_name', 'last_name', 'zip', 'where', 'electric_utility', 'mobile_phone', 'phone',
  'company', 'website_url', 'license', 'role', 'building_size', 'group_size', 'notes', 'story',
  'nominee_name', 'nominee_company', 'relationship', 'page', 'ref', 'came_from',
  'utm_source', 'utm_medium', 'utm_campaign',
  // marylandheatpumprebates.com fields
  'name', 'utility', 'company_website', 'fuel', 'project', 'units', 'cost', 'referrer'
];
const BOOL_PREFIXES = ['consent_', 'svc_'];
const BOOL_FIELDS = ['adult', 'training_waitlist', 'share', 'participating'];
const ANSWER_FIELDS = ['where', 'utility', 'heat', 'project', 'home', 'timeline'];

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

function clean(v, max) {
  return String(v == null ? '' : v).replace(/[\u0000-\u001f]/g, ' ').trim().slice(0, max || 300);
}

module.exports = async function handler(req, res) {
  if (req.method !== 'POST') {
    res.setHeader('Allow', 'POST');
    return res.status(405).json({ error: 'Method not allowed' });
  }

  let body = req.body;
  if (typeof body === 'string') {
    try { body = JSON.parse(body); } catch (e) { return res.status(400).json({ error: 'Bad JSON' }); }
  }
  body = body || {};

  // Honeypot: real people never fill the hidden "website" field.
  if (body.website) return res.status(200).json({ ok: true });

  const type = clean(body.type, 40);
  if (!TYPES.has(type)) return res.status(400).json({ error: 'Unknown form' });

  const lead = { type };
  for (const k of TEXT_FIELDS) {
    if (body[k] != null && body[k] !== '') lead[k] = clean(body[k], k === 'story' || k === 'notes' ? 1200 : 300);
  }
  for (const k of Object.keys(body)) {
    if (k === 'consent_text') continue; // kept verbatim in consent_record below
    if (BOOL_PREFIXES.some((p) => k.startsWith(p)) || BOOL_FIELDS.includes(k)) lead[k] = [true, 'on', 'yes'].includes(body[k]);
  }
  if (typeof body.answers === 'string') {
    lead.answers_text = clean(body.answers, 2000); // older site sends answers as one string
  } else if (body.answers && typeof body.answers === 'object') {
    lead.answers = {};
    for (const k of ANSWER_FIELDS) if (body.answers[k]) lead.answers[k] = clean(body.answers[k], 40);
    if (Array.isArray(body.answers.matched)) lead.answers.matched = body.answers.matched.slice(0, 30).map((m) => clean(m, 40));
  }

  if (!lead.email || !EMAIL_RE.test(lead.email)) return res.status(400).json({ error: 'Please enter a valid email.' });
  lead.email = lead.email.toLowerCase();
  if (lead.consent_sms && !lead.mobile_phone) return res.status(400).json({ error: 'Add a mobile number for texts.' });
  if (!lead.consent_sms) delete lead.mobile_phone; // no number kept without a text opt-in

  // Consent record: what was agreed to, when, and where.
  lead.consent_record = {
    at: new Date().toISOString(),
    ip: clean((req.headers['x-forwarded-for'] || '').split(',')[0], 64),
    user_agent: clean(req.headers['user-agent'], 300),
    page: lead.page || '',
    text: Array.isArray(body.consent_text) ? body.consent_text.slice(0, 10).map((t) => clean(t, 800)) : []
  };

  const url = process.env.LEAD_WEBHOOK_URL;
  if (!url) {
    console.error('LEAD_WEBHOOK_URL is not set; lead not stored', { type });
    return res.status(503).json({ error: 'Not configured' });
  }
  try {
    const headers = { 'Content-Type': 'application/json' };
    if (process.env.LEAD_WEBHOOK_SECRET) headers['X-Lead-Secret'] = process.env.LEAD_WEBHOOK_SECRET;
    const r = await fetch(url, { method: 'POST', headers, body: JSON.stringify(lead) });
    if (!r.ok) throw new Error('webhook ' + r.status);
  } catch (err) {
    console.error('Lead forward failed', { type, err: String(err) });
    return res.status(502).json({ error: 'Could not save' });
  }
  return res.status(200).json({ ok: true });
};
