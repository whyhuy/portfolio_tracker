// Vercel Routing (Edge) Middleware — password-gates the WHOLE site before anything is served,
// including the static data file (data/latest.json). This is the only free way to keep the
// dashboard's contents private; a client-side lock screen would leave the JSON publicly fetchable.
//
// Setup: in the Vercel project, add an Environment Variable  SITE_PASSWORD = <your password>.
// Access: visiting the site shows a browser login prompt — any username, that password.
// Fail-closed: if SITE_PASSWORD is unset, the site serves nothing (so it can never leak).
// Local dev (`npm run dev`) does NOT run this — it only executes on Vercel.
import { next } from '@vercel/edge'

export default function middleware(request) {
  const expected = process.env.SITE_PASSWORD || ''

  if (!expected) {
    return new Response('Access is not configured. Set SITE_PASSWORD in the Vercel project.', {
      status: 503,
    })
  }

  const header = request.headers.get('authorization') || ''
  const encoded = header.startsWith('Basic ') ? header.slice(6) : ''
  if (encoded) {
    // "user:pass" — we ignore the username and check the password only.
    const supplied = atob(encoded).split(':').slice(1).join(':')
    if (supplied === expected) return next()
  }

  return new Response('Authentication required.', {
    status: 401,
    headers: { 'WWW-Authenticate': 'Basic realm="Portfolio", charset="UTF-8"' },
  })
}
