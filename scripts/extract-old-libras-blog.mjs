import fs from 'node:fs/promises';
import path from 'node:path';
import puppeteer from 'puppeteer-core';

const SITEMAP_URL = 'https://old.libras.se/blog-posts-sitemap.xml';
const DEFAULT_OUT = 'blog/old-libras-se-blog-export.json';
const CHROME_PATH = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';

const args = new Map();
for (let index = 2; index < process.argv.length; index += 1) {
  const arg = process.argv[index];
  if (!arg.startsWith('--')) continue;
  const [key, inlineValue] = arg.slice(2).split('=');
  const value = inlineValue ?? process.argv[index + 1];
  args.set(key, value);
  if (inlineValue === undefined) index += 1;
}

const limit = Number.parseInt(args.get('limit') ?? '0', 10);
const outputPath = path.resolve(args.get('out') ?? DEFAULT_OUT);

function decodeXml(value = '') {
  return value
    .replaceAll('&amp;', '&')
    .replaceAll('&lt;', '<')
    .replaceAll('&gt;', '>')
    .replaceAll('&quot;', '"')
    .replaceAll('&apos;', "'");
}

function parseSitemap(xml) {
  return [...xml.matchAll(/<url>([\s\S]*?)<\/url>/g)].map((match) => {
    const block = match[1];
    const get = (tag) => decodeXml(block.match(new RegExp(`<${tag}>([\\s\\S]*?)<\\/${tag}>`))?.[1]?.trim() ?? '');
    const images = [...block.matchAll(/<image:image>([\s\S]*?)<\/image:image>/g)].map((imageMatch) => {
      const imageBlock = imageMatch[1];
      const imageLoc = imageBlock.match(/<image:loc>([\s\S]*?)<\/image:loc>/)?.[1]?.trim();
      return decodeXml(imageLoc ?? '');
    }).filter(Boolean);

    return {
      url: get('loc'),
      sitemapLastmod: get('lastmod') || null,
      sitemapImages: [...new Set(images)],
    };
  }).filter((item) => item.url);
}

function slugFromUrl(url) {
  return new URL(url).pathname.split('/').filter(Boolean).at(-1) ?? '';
}

async function fetchText(url) {
  const response = await fetch(url, {
    headers: {
      'user-agent': 'Mozilla/5.0 (compatible; LibrasSeMigrationBot/1.0)',
    },
  });
  if (!response.ok) {
    throw new Error(`Failed to fetch ${url}: ${response.status} ${response.statusText}`);
  }
  return response.text();
}

async function extractPost(page, sitemapItem) {
  await page.goto(sitemapItem.url, { waitUntil: 'networkidle2', timeout: 90_000 });
  await new Promise((resolve) => setTimeout(resolve, 2_500));

  return page.evaluate((item) => {
    const clean = (value = '') => value.replace(/\s+/g, ' ').trim();
    const absoluteUrl = (value) => {
      if (!value) return null;
      try {
        return new URL(value, window.location.href).href;
      } catch {
        return value;
      }
    };
    const uniqueBy = (rows, keyFn) => {
      const seen = new Set();
      return rows.filter((row) => {
        const key = keyFn(row);
        if (!key || seen.has(key)) return false;
        seen.add(key);
        return true;
      });
    };
    const meta = (name) => (
      document.querySelector(`meta[name="${name}"]`)?.getAttribute('content')
      ?? document.querySelector(`meta[property="${name}"]`)?.getAttribute('content')
      ?? null
    );
    const parseJsonLd = () => {
      const scripts = [...document.querySelectorAll('script[type="application/ld+json"]')];
      const parsed = scripts.flatMap((script) => {
        try {
          const data = JSON.parse(script.textContent || '{}');
          return Array.isArray(data) ? data : [data];
        } catch {
          return [];
        }
      });
      return parsed.find((entry) => {
        const type = Array.isArray(entry?.['@type']) ? entry['@type'] : [entry?.['@type']];
        return type.includes('BlogPosting');
      }) ?? null;
    };
    const jsonLd = parseJsonLd();
    const isVisible = (element) => {
      const style = window.getComputedStyle(element);
      const rect = element.getBoundingClientRect();
      return style.display !== 'none' && style.visibility !== 'hidden' && rect.width > 0 && rect.height > 0;
    };
    const selectors = [
      'article',
      '[data-hook="post-page"]',
      '[data-hook="post"]',
      '[data-hook="post-content"]',
      '[data-hook="post-description"]',
      '[data-hook*="post" i]',
      '[class*="post-content" i]',
      '[class*="postpage" i]',
      '[class*="blog" i]',
      'main',
    ];
    const candidates = uniqueBy(
      selectors.flatMap((selector) => [...document.querySelectorAll(selector)]),
      (element) => element
    ).filter(isVisible);
    const scored = candidates.map((element) => {
      const text = clean(element.innerText || element.textContent || '');
      const headings = element.querySelectorAll('h1,h2,h3').length;
      const paragraphs = element.querySelectorAll('p,li,blockquote').length;
      const titleMatch = jsonLd?.headline && text.includes(jsonLd.headline) ? 2_500 : 0;
      const articleBonus = element.tagName.toLowerCase() === 'article' ? 2_000 : 0;
      const sizePenalty = element === document.body ? -10_000 : 0;
      return { element, score: text.length + headings * 120 + paragraphs * 60 + titleMatch + articleBonus + sizePenalty };
    }).sort((a, b) => b.score - a.score);
    const root = scored[0]?.element ?? document.querySelector('main') ?? document.body;

    const denyText = new Set([
      'compartilhar',
      'curtir',
      'comentários',
      'comment',
      'recent posts',
      'posts recentes',
      'ver todos',
      'log in',
      'entrar',
    ]);
    const cleanBlockHtml = (value = '') => value
      .replace(/\s(?:class|style|id|data-[\w-]+|aria-[\w-]+)="[^"]*"/g, '')
      .replace(/\s+/g, ' ')
      .trim();
    const blockElements = [...root.querySelectorAll('h1,h2,h3,h4,h5,h6,p,li,blockquote,figcaption')]
      .filter(isVisible)
      .map((element) => {
        const links = uniqueBy([...element.querySelectorAll('a[href]')].map((link) => ({
          text: clean(link.innerText || link.textContent || ''),
          href: absoluteUrl(link.getAttribute('href')),
        })), (link) => link.href);

        return {
          type: element.tagName.toLowerCase(),
          text: clean(element.innerText || element.textContent || ''),
          html: cleanBlockHtml(element.innerHTML || element.textContent || ''),
          links,
        };
      })
      .filter((block) => block.text.length > 1 && !denyText.has(block.text.toLowerCase()));

    const contentBlocks = uniqueBy(blockElements, (block) => `${block.type}:${block.text}`);
    const imagesFromRoot = [...root.querySelectorAll('img')].filter(isVisible).map((image) => ({
      src: absoluteUrl(image.currentSrc || image.src || image.getAttribute('src')),
      alt: clean(image.alt || image.getAttribute('aria-label') || ''),
      width: image.naturalWidth || image.width || null,
      height: image.naturalHeight || image.height || null,
      source: 'rendered-post',
    }));
    const backgroundImages = [...root.querySelectorAll('*')].flatMap((element) => {
      const value = window.getComputedStyle(element).backgroundImage;
      return [...value.matchAll(/url\(["']?([^"')]+)["']?\)/g)].map((match) => ({
        src: absoluteUrl(match[1]),
        alt: '',
        width: null,
        height: null,
        source: 'rendered-background',
      }));
    });
    const jsonLdImage = typeof jsonLd?.image === 'string'
      ? jsonLd.image
      : jsonLd?.image?.url;
    const sitemapImages = (item.sitemapImages || []).map((src) => ({
      src,
      alt: '',
      width: null,
      height: null,
      source: 'sitemap',
    }));
    const images = uniqueBy([
      ...imagesFromRoot,
      ...backgroundImages,
      ...(jsonLdImage ? [{ src: jsonLdImage, alt: '', width: jsonLd?.image?.width ?? null, height: jsonLd?.image?.height ?? null, source: 'json-ld' }] : []),
      ...sitemapImages,
    ], (image) => image.src);
    const links = uniqueBy([...root.querySelectorAll('a[href]')].filter(isVisible).map((link) => ({
      text: clean(link.innerText || link.textContent || ''),
      href: absoluteUrl(link.getAttribute('href')),
    })).filter((link) => link.href), (link) => link.href);

    const title = clean(jsonLd?.headline || meta('og:title') || document.querySelector('h1')?.innerText || document.title);
    const description = clean(jsonLd?.description || meta('description') || meta('og:description') || '');
    const html = contentBlocks.map((block) => `<${block.type}>${block.html || block.text
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;')}</${block.type}>`).join('\n\n');

    return {
      url: item.url,
      slug: new URL(item.url).pathname.split('/').filter(Boolean).at(-1) ?? '',
      fetchedAt: new Date().toISOString(),
      title,
      description,
      author: jsonLd?.author ?? null,
      dates: {
        published: jsonLd?.datePublished ?? null,
        modified: jsonLd?.dateModified ?? null,
        sitemapLastmod: item.sitemapLastmod ?? null,
      },
      canonical: document.querySelector('link[rel="canonical"]')?.href ?? null,
      meta: {
        documentTitle: document.title,
        ogTitle: meta('og:title'),
        ogDescription: meta('og:description'),
        ogUrl: meta('og:url'),
        ogImage: meta('og:image'),
        twitterCard: meta('twitter:card'),
      },
      featuredImage: images[0] ?? null,
      images,
      links,
      content: {
        text: contentBlocks.map((block) => block.text).join('\n\n'),
        html,
        blocks: contentBlocks,
      },
      extraction: {
        selectedRootTag: root.tagName.toLowerCase(),
        selectedRootId: root.id || null,
        selectedRootClass: root.className || null,
        blockCount: contentBlocks.length,
        imageCount: images.length,
      },
      jsonLd,
    };
  }, sitemapItem);
}

const sitemapXml = await fetchText(SITEMAP_URL);
const sitemapPosts = parseSitemap(sitemapXml);
const postsToFetch = limit > 0 ? sitemapPosts.slice(0, limit) : sitemapPosts;

const browser = await puppeteer.launch({
  executablePath: CHROME_PATH,
  headless: 'new',
  args: ['--disable-gpu', '--no-first-run', '--disable-dev-shm-usage'],
});

const posts = [];
const errors = [];

try {
  const page = await browser.newPage();
  await page.setViewport({ width: 1440, height: 1400, deviceScaleFactor: 1 });
  await page.setUserAgent('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36');

  for (const [index, sitemapItem] of postsToFetch.entries()) {
    const label = `${index + 1}/${postsToFetch.length} ${slugFromUrl(sitemapItem.url)}`;
    process.stdout.write(`Extracting ${label}\n`);
    try {
      posts.push(await extractPost(page, sitemapItem));
    } catch (error) {
      errors.push({
        url: sitemapItem.url,
        slug: slugFromUrl(sitemapItem.url),
        message: error instanceof Error ? error.message : String(error),
      });
    }
  }
} finally {
  await browser.close();
}

const exportData = {
  source: {
    site: 'https://old.libras.se',
    sitemap: SITEMAP_URL,
  },
  generatedAt: new Date().toISOString(),
  totalPostsInSitemap: sitemapPosts.length,
  totalPostsFetched: posts.length,
  totalErrors: errors.length,
  posts,
  errors,
};

await fs.mkdir(path.dirname(outputPath), { recursive: true });
await fs.writeFile(outputPath, `${JSON.stringify(exportData, null, 2)}\n`, 'utf8');
process.stdout.write(`Wrote ${outputPath}\n`);
process.stdout.write(`Fetched ${posts.length}/${sitemapPosts.length} posts with ${errors.length} errors\n`);
