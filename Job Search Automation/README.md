# Automated Job Search 

An automated job intelligence and opportunity discovery system that identifies relevant open roles across startups and tech companies of interest, operating in NYC.

This project was built to eliminate the repetitive and fragmented workflow of manually checking dozens of startup websites for relevant opportunities. Instead of browsing company-by-company, the system automatically aggregates, filters, ranks, and presents actionable job opportunities in a searchable dashboard.

---

# Problem

Searching for startup opportunities manually is highly inefficient:
- Jobs are scattered across individual company career pages
- Many companies are not indexed well on major job boards
- Relevant opportunities are difficult to track consistently
- Comparing opportunities across companies is time-consuming
- There is no centralized operational workflow for startup-specific job discovery

This creates a fragmented and repetitive process that wastes significant time and leads to missed opportunities.

---

# Solution

Built an automated intelligence pipeline that:

1. Collects Israeli startup company data from a structured NYC startup directory
2. Identifies and crawls company career pages
3. Extracts open job listings
4. Filters and ranks opportunities by relevance
5. Generates a searchable and sortable dashboard for exploration

The system transforms fragmented company websites into a centralized decision-support workflow.

---

# Key Features

## Automated Company Discovery
- Pulls startup/company information from a centralized database
- Processes large company lists automatically

## Career Page Detection
- Identifies careers/job pages across different website structures
- Handles inconsistent navigation patterns

## Job Extraction Pipeline
- Scrapes open roles from company websites
- Parses titles, locations, and metadata

## Relevance Ranking
- Scores jobs based on keyword and relevance matching
- Prioritizes higher-signal opportunities

## Searchable HTML Dashboard
- Interactive report generation
- Sortable/filterable job listings
- Structured presentation layer for fast review

## Concurrent Processing
- Uses multithreading to process companies efficiently
- Significantly reduces runtime for large company sets

## Caching Layer
- Stores processed company data locally
- Avoids unnecessary repeated scraping
- Improves operational efficiency and speed

---

# Workflow Architecture

```text
Company Database
        ↓
Company Website Discovery
        ↓
Career Page Detection
        ↓
Job Scraping & Extraction
        ↓
Relevance Filtering & Ranking
        ↓
Interactive HTML Dashboard
