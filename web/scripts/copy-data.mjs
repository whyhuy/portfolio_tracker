// Copies the data layer's outputs into web/public/data so the SPA can fetch them
// in dev and in the Vercel build. Runs automatically via predev / prebuild.
import { mkdirSync, copyFileSync, existsSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const here = dirname(fileURLToPath(import.meta.url))
const webRoot = resolve(here, '..')
const dataSrc = resolve(webRoot, '..', 'data')
const dest = resolve(webRoot, 'public', 'data')

mkdirSync(dest, { recursive: true })
for (const f of ['latest.json', 'history.csv']) {
  const from = resolve(dataSrc, f)
  if (existsSync(from)) {
    copyFileSync(from, resolve(dest, f))
    console.log(`[sync:data] copied ${f}`)
  } else {
    console.warn(`[sync:data] missing ${from} (skipped)`)
  }
}
