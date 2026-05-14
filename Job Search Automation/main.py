"""
Orchestrates the full pipeline: scrape companies → find careers pages → scrape jobs → filter → output HTML report.

Usage:
    python main.py                         # Run full pipeline (all companies)
    python main.py --max-companies 20      # Test with first N companies
    python main.py --no-cache              # Skip cached company list
"""

import argparse
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

from scrapers.company_db import scrape_companies
from scrapers.careers_finder import find_careers_page
from scrapers.job_scraper import scrape_jobs_from_careers_page
from filters import filter_jobs
from output_generator import generate_html_report
from config import MAX_WORKERS

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(SCRIPT_DIR, ".cache")
COMPANIES_CACHE = os.path.join(CACHE_DIR, "companies.json")
OUTPUT_PATH = os.path.join(SCRIPT_DIR, "output", "results.html")


def main():
    parser = argparse.ArgumentParser(description="Israeli NYC Startup Job Scraper")
    parser.add_argument("--max-companies", type=int, default=None, help="Limit number of companies (for testing)")
    parser.add_argument("--no-cache", action="store_true", help="Re-scrape company list even if cached")
    args = parser.parse_args()

    print("=" * 60)
    print("🚀 Israeli NYC Startup Job Scraper")
    print(f"   Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # ── Step 1: Get company list ──────────────────────────────────
    print("\n📋 Step 1: Fetching company list...")
    companies = _load_or_scrape_companies(force_refresh=args.no_cache)

    if args.max_companies:
        companies = companies[:args.max_companies]
        print(f"   ℹ️  Limited to first {args.max_companies} companies (--max-companies flag)")

    print(f"   ✅ Processing {len(companies)} companies\n")

    # ── Step 2: Find careers pages and scrape jobs (parallel) ─────
    print("🔍 Step 2: Finding careers pages and scraping jobs...")
    all_jobs = []
    errors = []
    success_count = 0
    no_careers_count = 0

    def process_company(company):
        try:
            careers_page = find_careers_page(company.website)
            if not careers_page:
                return [], "no_careers"
            jobs = scrape_jobs_from_careers_page(careers_page, company.name)
            return jobs, "ok"
        except Exception as e:
            return [], f"error: {e}"

    print(f"   🚀 Submitting {len(companies)} tasks to ThreadPoolExecutor...")
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(process_company, c): c for c in companies}
        done = 0
        print(f"   🔍 Waiting for tasks to complete...")
        try:
            for future in as_completed(futures):
                company = futures[future]
                done += 1
                try:
                    jobs, status = future.result()
                    if status == "ok":
                        all_jobs.extend(jobs)
                        success_count += 1
                        print(f"  [{done}/{len(companies)}] ✅ {company.name}: {len(jobs)} jobs found")
                    elif status == "no_careers":
                        no_careers_count += 1
                        print(f"  [{done}/{len(companies)}] ⚠️  {company.name}: no careers page found")
                    else:
                        errors.append(company.name)
                        print(f"  [{done}/{len(companies)}] ❌ {company.name}: {status}")
                except BaseException as e:
                    errors.append(company.name)
                    print(f"  [{done}/{len(companies)}] 🧨 Fatal task error for {company.name}: {e}")
        except BaseException as e:
            print(f"   🔥 FATAL: Loop interrupted: {e}")
        finally:
            print(f"   🏁 Loop finished at {done}/{len(companies)}")

    print(f"\n   📊 Summary: {success_count} companies scraped, {no_careers_count} no careers page, {len(errors)} errors")
    print(f"   📦 Total raw jobs collected: {len(all_jobs)}")

    # ── Step 3: Filter ───────────────────────────────────────────
    print("\n🎯 Step 3: Filtering jobs by location + keywords + seniority...")
    matched_jobs = filter_jobs(all_jobs)
    print(f"   ✅ {len(matched_jobs)} matching jobs after filtering")

    # ── Step 4: Generate HTML report ─────────────────────────────
    print("\n📄 Step 4: Generating HTML report...")
    generate_html_report(matched_jobs, OUTPUT_PATH)

    print("\n" + "=" * 60)
    print(f"✨ Done! Found {len(matched_jobs)} matching positions.")
    print(f"   Open: file://{os.path.abspath(OUTPUT_PATH)}")
    print("=" * 60)


def _load_or_scrape_companies(force_refresh: bool = False):
    """Load companies from cache or scrape fresh."""
    os.makedirs(CACHE_DIR, exist_ok=True)

    if not force_refresh and os.path.exists(COMPANIES_CACHE):
        try:
            with open(COMPANIES_CACHE, "r") as f:
                data = json.load(f)
            print(f"   ♻️  Loaded {len(data)} companies from cache (use --no-cache to refresh)")
            # Re-create Company objects
            from scrapers.company_db import Company
            return [Company(**c) for c in data]
        except Exception:
            pass

    from scrapers.company_db import scrape_companies as _scrape
    companies = _scrape()

    # Save to cache
    try:
        with open(COMPANIES_CACHE, "w") as f:
            import dataclasses
            json.dump([dataclasses.asdict(c) for c in companies], f, indent=2)
        print(f"   💾 Company list cached to {COMPANIES_CACHE}")
    except Exception:
        pass

    return companies


if __name__ == "__main__":
    main()
