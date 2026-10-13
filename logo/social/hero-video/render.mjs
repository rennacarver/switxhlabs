// Renders hero-video.html to a 1080×1080, 30fps MP4 for LinkedIn.
// Usage: node render.mjs <node_modules dir with puppeteer-core + ffmpeg-static> <output.mp4>
import { createRequire } from 'node:module'
import { mkdtempSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join, dirname, resolve } from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'
import { execFileSync } from 'node:child_process'

const [modulesDir, outFile] = process.argv.slice(2)
const require = createRequire(join(resolve(modulesDir), 'noop.js'))
const puppeteer = require('puppeteer-core')
const ffmpeg = require('ffmpeg-static')

const FPS = 30
const here = dirname(fileURLToPath(import.meta.url))
const frames = mkdtempSync(join(tmpdir(), 'hero-frames-'))

const browser = await puppeteer.launch({
  executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  args: ['--allow-file-access-from-files', '--hide-scrollbars'],
})
const page = await browser.newPage()
await page.setViewport({ width: 1080, height: 1080, deviceScaleFactor: 1 })
await page.goto(pathToFileURL(join(here, 'hero-video.html')).href, { waitUntil: 'networkidle0' })
await page.evaluate(() => document.fonts.ready)

const total = await page.evaluate(() => window.TOTAL)
const count = Math.round((total / 1000) * FPS)
for (let i = 0; i < count; i++) {
  await page.evaluate((ms) => window.render(ms), (i * 1000) / FPS)
  await page.screenshot({ path: join(frames, `f${String(i).padStart(5, '0')}.png`) })
}
await browser.close()

execFileSync(ffmpeg, [
  '-y', '-loglevel', 'error',
  '-framerate', String(FPS),
  '-i', join(frames, 'f%05d.png'),
  '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '16', '-preset', 'slow',
  '-movflags', '+faststart',
  resolve(outFile),
])
rmSync(frames, { recursive: true, force: true })
console.log(`${count} frames, ${(total / 1000).toFixed(2)}s -> ${outFile}`)
