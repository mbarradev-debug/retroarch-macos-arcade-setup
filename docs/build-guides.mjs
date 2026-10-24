// Build every guide in guides/src/*.md into a single-page PDF in guides/.
//
// Each guide is rendered to HTML with a shared stylesheet, then printed by a
// headless Chrome whose page height is set to the measured height of the
// content, so the PDF is one continuous page with no page breaks.
import { readFileSync, readdirSync, mkdirSync } from "node:fs";
import { join, basename, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { Marked } from "marked";
import { chromium } from "playwright-core";

const HERE = dirname(fileURLToPath(import.meta.url));
const SRC = join(HERE, "guides", "src");
const OUT = join(HERE, "guides");
const WIDTH_PX = 860;
// PDF viewers cap page height at about 200 inches (14,400 pt); 96 CSS px per inch.
const MAX_HEIGHT_PX = 200 * 96;
// Links between guides point at the published copies: a PDF printed by Chrome
// cannot keep a relative link to another local file.
const GUIDES_URL = "https://github.com/mbarradev-debug/retroarch-macos-arcade-setup/blob/main/docs/guides/";

const slugify = (text) =>
  text.toLowerCase().replace(/<[^>]+>/g, "").replace(/&[a-z]+;/g, "").replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");

function render(markdown) {
  const headings = [];
  const used = new Set();
  const marked = new Marked({
    gfm: true,
    renderer: {
      heading({ tokens, depth }) {
        const html = this.parser.parseInline(tokens);
        let id = slugify(html);
        for (let n = 2; used.has(id); n++) id = `${slugify(html)}-${n}`;
        used.add(id);
        if (depth === 2 || depth === 3) headings.push({ depth, id, html });
        return `<h${depth} id="${id}">${html}</h${depth}>\n`;
      },
      // GitHub-style alerts: > [!WARNING] ... become highlighted callouts.
      blockquote({ tokens }) {
        const body = this.parser.parse(tokens);
        const m = body.match(/^<p>\[!(NOTE|TIP|WARNING|IMPORTANT|CAUTION)\]\s*/);
        if (!m) return `<blockquote>${body}</blockquote>\n`;
        const kind = m[1].toLowerCase();
        return `<div class="callout ${kind}"><div class="callout-label">${m[1]}</div><p>${body.slice(m[0].length)}</div>\n`;
      },
    },
  });
  let html = marked.parse(markdown);
  // h2 entries are numbered; h3 entries are nested under the h2 before them.
  let toc = "";
  headings.forEach((h, i) => {
    const link = `<a href="#${h.id}">${h.html}</a>`;
    const next = headings[i + 1];
    if (h.depth === 2) toc += `<li>${link}${next?.depth === 3 ? "<ul>" : "</li>"}`;
    else toc += `<li>${link}</li>${next?.depth === 3 ? "" : "</ul></li>"}`;
  });
  html = html.replace(/<p>\[\[toc\]\]<\/p>/, `<nav class="toc"><div class="toc-title">Contents</div><ol>${toc}</ol></nav>`);
  html = html.replace(/<code>([0-9a-f]{32})<\/code>/g, '<code class="md5">$1</code>');
  return html.replace(/href="(\d\d-[a-z0-9-]+\.pdf)"/g, `href="${GUIDES_URL}$1"`);
}

function page(title, body, css) {
  return `<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>${title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:ital,wght@0,400;0,700;1,400&family=JetBrains+Mono:wght@400;600&family=Press+Start+2P&display=block" rel="stylesheet">
<style>${css}</style></head>
<body><main>${body}</main></body></html>`;
}

const css = readFileSync(join(HERE, "guide.css"), "utf8");
mkdirSync(OUT, { recursive: true });
const browser = await chromium.launch({ channel: "chrome", headless: true });
const context = await browser.newContext({ viewport: { width: WIDTH_PX, height: 1200 } });
let failed = false;

for (const file of readdirSync(SRC).filter((f) => f.endsWith(".md")).sort()) {
  const markdown = readFileSync(join(SRC, file), "utf8");
  const title = (markdown.match(/^# (.+)$/m) || [, basename(file, ".md")])[1];
  const html = page(title, render(markdown), css);
  const name = basename(file, ".md");

  const tab = await context.newPage();
  await tab.setContent(html, { waitUntil: "networkidle" });
  await tab.evaluate(() => document.fonts.ready);
  const height = Math.ceil(await tab.evaluate(() => document.documentElement.scrollHeight));
  if (height > MAX_HEIGHT_PX) {
    console.error(`${file}: ${height}px is taller than ${MAX_HEIGHT_PX}px (200 in). Split it into two guides.`);
    failed = true;
    await tab.close();
    continue;
  }
  await tab.pdf({
    path: join(OUT, `${name}.pdf`),
    width: `${WIDTH_PX}px`,
    height: `${height + 2}px`,
    printBackground: true,
    margin: { top: "0", right: "0", bottom: "0", left: "0" },
    pageRanges: "1",
  });
  await tab.close();
  console.log(`${name}.pdf  ${height}px (${(height / 96).toFixed(1)} in)`);
}

await browser.close();
if (failed) process.exit(1);
