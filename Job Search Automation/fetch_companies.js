#!/usr/bin/env node
/**
 * Scrapes company data from israelimappedinny.com/database
 * The site is Webflow-rendered, but individual page HTML still contains the data
 * when fetched with a real browser User-Agent.
 *
 * Usage: node fetch_companies.js > .cache/companies.json
 */

const https = require('https');
const http = require('http');

const BASE_URL = 'https://www.israelimappedinny.com/database';
const TOTAL_PAGES = 17;

const HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
};

function fetchPage(url) {
    return new Promise((resolve, reject) => {
        const lib = url.startsWith('https') ? https : http;
        const req = lib.get(url, { headers: HEADERS }, (res) => {
            // Handle redirects
            if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
                return fetchPage(res.headers.location).then(resolve).catch(reject);
            }
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => resolve(data));
        });
        req.on('error', reject);
        req.setTimeout(15000, () => { req.destroy(); reject(new Error('timeout')); });
    });
}

function parseCompanies(html) {
    const companies = [];

    // Extract .w-dyn-item blocks using regex (no DOM parser in base Node)
    // Each item contains company name (fs-list-field="name") and a "Visit Website" link

    // Split into items
    const itemPattern = /<[^>]+class="[^"]*w-dyn-item[^"]*"[^>]*>([\s\S]*?)(?=<[^>]+class="[^"]*w-dyn-item|$)/gi;

    // Simpler approach: extract all occurrences of the pattern
    const blocks = html.split(/class="[^"]*w-dyn-item[^"]*"/);

    for (let i = 1; i < blocks.length; i++) {
        const block = blocks[i].substring(0, 3000); // limit to reasonable size

        // Extract name (fs-list-field="name" attribute)
        const nameMatch = block.match(/fs-list-field="name"[^>]*>([\s\S]*?)<\/div>/);
        if (!nameMatch) continue;
        const name = nameMatch[1].replace(/<[^>]+>/g, '').trim();
        if (!name) continue;

        // Extract website - look for "Visit Website" link
        const visitMatch = block.match(/href="(https?:\/\/[^"]+)"[^>]*>[^<]*Visit Website/i) ||
            block.match(/Visit Website[^<]*<\/a>[\s\S]{0,200}href="(https?:\/\/[^"]+)"/i);

        // Also try pattern: href="URL" ... >Visit Website
        const hrefVisitMatch = block.match(/href="(https?:\/\/(?!www\.israelimappedinny\.com)[^"]+)"(?:[^>]*)>(?:[^<]*<[^>]+>)*[^<]*Visit Website/i);

        let website = null;
        if (visitMatch) website = visitMatch[1];
        else if (hrefVisitMatch) website = hrefVisitMatch[1];

        if (!website || website.includes('israelimappedinny.com')) continue;

        // Extract sector
        const sectorMatch = block.match(/fs-list-field="vertical"[^>]*>([\s\S]*?)<\/div>/);
        const sector = sectorMatch ? sectorMatch[1].replace(/<[^>]+>/g, '').trim() : '';

        // Check hiring status
        const isHiring = /class="[^"]*hiring[^"]*"/.test(block);

        companies.push({ name, website, sector, is_hiring: isHiring });
    }

    return companies;
}

async function main() {
    const allCompanies = [];
    const seen = new Set();

    process.stderr.write(`Fetching ${TOTAL_PAGES} pages...\n`);

    for (let page = 1; page <= TOTAL_PAGES; page++) {
        const url = page === 1 ? BASE_URL : `${BASE_URL}?75ad698b_page=${page}`;

        try {
            const html = await fetchPage(url);
            const companies = parseCompanies(html);

            let added = 0;
            for (const company of companies) {
                const key = company.name.toLowerCase();
                if (!seen.has(key)) {
                    seen.add(key);
                    allCompanies.push(company);
                    added++;
                }
            }

            process.stderr.write(`  Page ${page}: ${added} companies (total: ${allCompanies.length})\n`);
        } catch (err) {
            process.stderr.write(`  Page ${page}: ERROR - ${err.message}\n`);
        }

        // Small delay between requests
        await new Promise(r => setTimeout(r, 300));
    }

    process.stderr.write(`\nTotal: ${allCompanies.length} companies\n`);
    console.log(JSON.stringify(allCompanies, null, 2));
}

main().catch(err => {
    process.stderr.write(`Fatal error: ${err.message}\n`);
    process.exit(1);
});
