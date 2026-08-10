Scraper Guardian
================

AI-powered monitoring and maintenance system for web scrapers.

The goal of this project is to automatically detect changes in websites
that affect web scraping, identify the cause of scraper failures, and
eventually generate and validate code changes required to repair scrapers.

Project goals
-------------

1. Monitor websites used by scrapers.
2. Store HTML and DOM snapshots.
3. Detect meaningful structural changes.
4. Validate scraper extraction.
5. Identify affected fields.
6. Use AI to analyze scraper failures.
7. Generate repair suggestions.
8. Test proposed scraper changes.
9. Notify developers about important changes.
10. Eventually automate safe scraper repairs.

Architecture
------------

Website
    |
    v
Scraper
    |
    v
Snapshot
    |
    v
Change Detector
    |
    v
Scraper Validator
    |
    v
AI Analyzer
    |
    v
Repair Agent
    |
    v
Validation
    |
    v
Human Approval