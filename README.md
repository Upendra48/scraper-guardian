# Scraper Guardian

Scraper Guardian is a system for detecting changes in a website's HTML structure, identifying changes that may break an existing scraper, generating possible repairs, validating those repairs against the updated HTML, and eventually applying validated repairs to scraper source code.

The goal is to move from:

> "The scraper broke. Find out why."

toward:

> "The website changed. Identify what changed, determine whether the scraper is affected, and suggest a validated repair."

---

# Architecture

```text
                    Website
                       │
                       ▼
              HTML Snapshot
                       │
             ┌─────────┴─────────┐
             │                   │
             ▼                   ▼
       Previous HTML       Current HTML
             │                   │
             └─────────┬─────────┘
                       ▼
              Structural Detector
                       │
                       ▼
                ElementSnapshot
                       │
                       ▼
                Element Matcher
                       │
                       ▼
              Matched Elements
                       │
                       ▼
                Change Analyzer
                       │
                       ▼
               Detected Changes
                       │
                       ▼
                Repair Engine
                       │
                       ▼
             Repair Suggestions
                       │
                       ▼
              Repair Validator
                       │
                       ▼
             Validated Repairs
                       │
                       ▼
                Repair Applier
                       │
                       ▼
             Updated Scraper Code
                       │
                       ▼
                Final Validation
```

The system is divided into independent stages so that each stage has a clear responsibility.

---

# Components

## 1. Structural Detector

The Structural Detector converts HTML into a structured representation of individual elements.

Each element is represented by an `ElementSnapshot` containing:

```text
ElementSnapshot(
    tag="a",
    path="/html[1]/body[1]/...",
    attributes={
        "href": "bids.aspx?bidID=287"
    },
    text="HWY Marking Project"
)
```

The detector can identify:

- Elements added to the current HTML
- Elements removed from the current HTML
- Attribute changes
- Text changes

The element collection is stored as a dictionary keyed by element path information, while the matcher operates on the `ElementSnapshot` values.

---

## 2. Element Matcher

The Element Matcher determines whether an element in the previous HTML is probably the same element as an element in the current HTML.

Matching uses evidence such as:

- HTML tag
- Element ID
- `name`
- Visible text
- Matching attributes
- Shared numeric identifiers

The matcher assigns a confidence score to potential matches.

Example:

```text
Tag:   form
Score: 1.00

Previous attributes:
{
    'id': 'cpPopOverForm',
    'name': 'cpPopOverForm',
    'novalidate': ''
}

Current attributes:
{
    'id': 'cpPopOverForm',
    'name': 'cpPopOverForm',
    'novalidate': ''
}
```

The matcher may produce:

```text
Previous elements: 582
Current elements:  582
Matched elements:  398
```

Its responsibility is:

> "Are these probably the same elements?"

The Change Analyzer then answers:

> "If they are the same elements, what changed?"

This separation helps avoid false changes caused by elements being inserted or removed.

---

# 3. Change Analyzer

The Change Analyzer examines matched elements and identifies meaningful differences.

It currently considers changes to:

```text
href
src
id
name
class
action
value
type
data-*
```

It also detects visible text changes.

Changes are classified as:

```text
HIGH
MEDIUM
LOW
```

---

## 3.1 Attribute Changes

The analyzer can detect:

```text
href changed
src changed
id changed
name changed
class changed
action changed
type changed
value changed
data-* changed
```

Example:

```text
Type:       attribute_changed
Tag:        a
Attribute:  href
Severity:   HIGH

Old:
bids.aspx?bidID=287

New:
/procurement/bid/287
```

Each detected change also contains an impact description and evidence.

---

## 3.2 HREF / URL Changes

Changes to link destinations are treated as high-risk because scrapers may directly depend on the URL.

Example:

```text
Old:
/business-office/pdf/bids/Bid%20Instructions%20--%20Flat%20Steel%208-11.pdf

New:
/business-office/pdf/bids-open/Bid%20Instructions%20--%20Flat%20Steel%208-11.pdf
```

Detected result:

```text
Type:       attribute_changed
Tag:        a
Attribute:  href
Severity:   HIGH
```

Impact:

```text
Link destination changed. A scraper using this URL
or URL pattern may need to be updated.
```

---

## 3.3 URL Pattern Detection

The analyzer normalizes dynamic URLs into reusable patterns.

For example:

```text
bids.aspx?bidID=287
bids.aspx?bidID=288
bids.aspx?bidID=289
```

becomes:

```text
bids.aspx?bidID=<id>
```

And:

```text
/procurement/bid/287
/procurement/bid/288
/procurement/bid/289
```

becomes:

```text
/procurement/bid/<id>
```

This allows multiple individual URL changes to be grouped into a scraper-level recommendation.

Example:

```text
Type:     url_pattern_changed
Severity: HIGH
```

---

## 3.4 CSS Class Changes

Changes to `class` are detected.

Example:

```text
Old:
table table-bordered

New:
tableTest table-bordered
```

Result:

```text
Type:       attribute_changed
Tag:        table
Attribute:  class
Severity:   MEDIUM
```

Recommendation:

```text
Type:     selector_class_changed
Severity: MEDIUM
```

This indicates that class-based CSS or XPath selectors may need review.

---

## 3.5 ID Changes

Changes to `id` are classified as high-risk.

Example:

```text
Old:
id="bid-list"

New:
id="open-bid-list"
```

Recommendation:

```text
Type:     selector_id_changed
Severity: HIGH
```

---

## 3.6 NAME Changes

Changes to `name` are detected.

This is useful for:

- Form fields
- Input elements
- Search fields
- Scraper selectors

Example:

```text
Old:
name="bid_id"

New:
name="procurement_id"
```

Recommendation:

```text
Type:     selector_name_changed
Severity: HIGH
```

---

## 3.7 SRC Changes

Changes to `src` resource URLs are detected.

Example:

```text
Old:
src="/documents/bid.pdf"

New:
src="/documents/open-bids/bid.pdf"
```

Recommendation:

```text
Type:     resource_url_changed
Severity: HIGH
```

---

## 3.8 FORM ACTION Changes

Changes to form submission URLs are detected.

Example:

```html
<form action="/search">
```

changed to:

```html
<form action="/procurement/search">
```

Recommendation:

```text
Type:     form_action_changed
Severity: HIGH
```

---

## 3.9 TYPE Changes

Changes to an element's `type` attribute are detected.

Example:

```html
<input type="text">
```

changed to:

```html
<input type="hidden">
```

Recommendation:

```text
Type:     element_type_changed
Severity: MEDIUM
```

---

## 3.10 VALUE Changes

Changes to `value` are detected and normally classified as low severity.

Example:

```text
Old:
value="open"

New:
value="closed"
```

---

## 3.11 DATA-* Changes

Changes to custom `data-*` attributes are detected.

Examples:

```text
data-id
data-bid-id
data-url
data-category
```

These are normally classified as:

```text
Severity: MEDIUM
```

because websites often store scraper-relevant identifiers and URLs in data attributes.

---

# 4. Text Change Detection

The Change Analyzer detects visible element text changes.

Example:

```text
Old:
Marketing Bid 2026

New:
Marketing Bid 2027
```

Result:

```text
Type:       text_changed
Severity:   LOW
```

Text changes on interactive elements such as:

```text
a
button
input
label
```

are treated as more important because scrapers may use text-based selectors.

Such changes receive:

```text
Severity: MEDIUM
```

Large text values are ignored above the configured threshold to avoid reporting the same small change repeatedly on every parent container.

For example, changing one bid can otherwise change the text returned by its:

```text
div
table
thead
tr
```

parents.

---

# 5. Element Change Detector

The Element Change Detector handles structural additions and removals that are not represented by matched elements.

It detects:

```text
element_added
element_removed
```

---

## 5.1 Element Added

An element is added when it exists in the current HTML but has no corresponding previous match.

Example:

```html
<button>Download</button>
```

Result:

```text
Type:     element_added
Tag:      button
Severity: MEDIUM
```

Evidence:

```text
[OK] Element exists in the current HTML
[OK] Element has no corresponding previous match
```

Impact:

```text
A scraper-relevant element was added to the page.
Check whether it contains new data or changes the extraction structure.
```

---

## 5.2 Element Removed

An element is removed when it existed in the previous HTML but has no corresponding current match.

For example:

```html
<td>
    <a href="/business-office/pdf/bids/Bid%20Instructions%20--Marketing%208-11.pdf">
        August 11, 2026, 2:00PM
    </a>
</td>
```

If the date `<td>` and its `<a>` are removed, the detector reports both:

```text
Type:     element_removed
Tag:      td
Severity: HIGH
```

and:

```text
Type:     element_removed
Tag:      a
Severity: HIGH
```

Evidence:

```text
[OK] Element existed in the previous HTML
[OK] Element has no corresponding current match
```

This confirms that the detector can identify both removed parent elements and their removed children.

---

# 6. Structural Changes vs Matched Element Changes

Scraper Guardian separates two kinds of changes.

## Matched Element Changes

These occur when the same logical element exists in both snapshots but something changed.

Examples:

```text
href changed
class changed
id changed
text changed
src changed
```

Flow:

```text
Previous Element
       +
Current Element
       ↓
Element Matcher
       ↓
Matched
       ↓
Change Analyzer
       ↓
Attribute/Text Change
```

## Structural Changes

These occur when an element exists in one snapshot but not the other.

Examples:

```text
element_added
element_removed
```

Flow:

```text
Previous Elements
       +
Current Elements
       ↓
Element Matcher
       ↓
Unmatched Elements
       ↓
Element Change Detector
       ↓
Added / Removed Element
```

---

# 7. Recommendation Generation

The analyzer converts low-level HTML differences into scraper-level recommendations.

For example, several URL changes:

```text
bids.aspx?bidID=286
bids.aspx?bidID=287
bids.aspx?bidID=288
```

changing to:

```text
/procurement/bid/286
/procurement/bid/287
/procurement/bid/288
```

can produce one recommendation:

```text
Type:     url_pattern_changed
Severity: HIGH
```

Other recommendations include:

```text
selector_class_changed
selector_id_changed
selector_name_changed
resource_url_changed
form_action_changed
element_type_changed
text_changed
element_added
element_removed
```

---

# 8. Example: Clinton University Bid Page

A test was performed using a snapshot of the Clinton University business office bid page.

The original snapshot contained:

```text
Previous elements: 267
Current elements:  267
Matched elements:  267
```

Two modifications were introduced:

1. A table class was changed.
2. Bid document URL paths were changed.

The Change Analyzer correctly detected:

```text
Detected changes: 3
```

Recommendations:

```text
[1]
Type:     url_pattern_changed
Severity: HIGH
```

and:

```text
[2]
Type:     selector_class_changed
Severity: MEDIUM
```

Detected changes included:

```text
[CHANGE 1]

Type:       attribute_changed
Tag:        table
Attribute:  class
Severity:   MEDIUM

Old:
table table-bordered

New:
tableTest table-bordered
```

and two high-risk `href` changes.

This demonstrated that the analyzer correctly identifies the specific changed attributes.

---

# 9. Testing Element Removal

A structural test was performed by removing the `<td>` containing a bid date and its corresponding `<a>` element.

The result was:

```text
Previous elements: 267
Current elements: 265
Matched elements: 265
Structural changes: 2
```

The detector reported:

```text
[CHANGE 1]

Type:     element_removed
Tag:      td
Severity: HIGH
```

and:

```text
[CHANGE 2]

Type:     element_removed
Tag:      a
Severity: HIGH
```

This confirms that element removal is detected independently from attribute and text changes.

---

# 10. Testing Element Addition

The detector was also tested by adding a new button to the HTML.

Example:

```html
<button>Download</button>
```

Result:

```text
Structural changes: 1
```

with:

```text
Type:     element_added
Tag:      button
Severity: MEDIUM
```

Evidence:

```text
[OK] Element exists in the current HTML
[OK] Element has no corresponding previous match
```

---

# 11. Detected Change Types

The current Change Analyzer and Element Change Detector can detect:

| Change Type | Detection | Typical Severity |
|---|---:|---:|
| `href` change | ✓ | HIGH |
| URL pattern change | ✓ | HIGH |
| `src` change | ✓ | HIGH |
| `id` change | ✓ | HIGH |
| `name` change | ✓ | HIGH |
| `class` change | ✓ | MEDIUM |
| `action` change | ✓ | HIGH |
| `type` change | ✓ | MEDIUM |
| `value` change | ✓ | LOW |
| `data-*` change | ✓ | MEDIUM |
| Visible text change | ✓ | LOW / MEDIUM |
| Element added | ✓ | MEDIUM |
| Element removed | ✓ | HIGH |

The system therefore supports both attribute-level and structural changes.

---

# 12. Why Element Matching Is Important

HTML pages often contain hundreds of elements.

Position-based comparison is unreliable because inserting or removing one element can shift every element after it.

For example:

```text
Previous:

element 1
element 2
element 3
element 4
```

Current:

```text
element 1
NEW element
element 2
element 3
element 4
```

A position-based system could incorrectly report multiple elements as changed.

Scraper Guardian instead uses multiple pieces of evidence:

```text
Same tag
+
Same ID
+
Same text
+
Same attributes
+
Shared identifier
```

This allows the Change Analyzer to focus on actual changes instead of position shifts.

---

# 13. Change Detection Pipeline

```text
Previous HTML
      +
Current HTML
      │
      ▼
Structural Detector
      │
      ▼
Element Snapshots
      │
      ▼
Element Matcher
      │
      ▼
Matched Elements
      │
      ├──────────────────────┐
      ▼                      ▼
Change Analyzer       Element Change Detector
      │                      │
      ▼                      ▼
Attribute/Text Changes   Added/Removed Elements
      │                      │
      └───────────┬──────────┘
                  ▼
          Recommendations
```

---

# 14. Repair Engine

The Repair Engine converts recommendations into concrete repair suggestions.

Example:

```text
Type:       url_pattern_update
Severity:   HIGH

Old:
bids.aspx?bidID=<id>

New:
/procurement/bid/<id>

Confidence:
0.98
```

The Repair Engine does not directly modify scraper source code.

Its responsibility is:

> "What change should the scraper make?"

---

# 15. Repair Validator

Before a repair can be applied, it is validated against the current HTML.

Example:

```text
Previous elements: 582
Current elements:  582
Matched elements:  398
Detected changes:  3
Recommendations:   1
Repairs:           1
```

Validation result:

```text
Type:       url_pattern_update
Old:        bids.aspx?bidID=<id>
New:        /procurement/bid/<id>

Valid:      True
Confidence: 0.98
```

The validator provides an additional safety layer:

```text
Change detected
      ↓
Repair suggested
      ↓
Repair validated
      ↓
Only then can repair be applied
```

---

# 16. Repair Applier

The Repair Applier is the next stage of the pipeline.

Its purpose is to apply a **validated** repair to scraper source code.

The design separates:

```text
Detection
    ↓
Recommendation
    ↓
Repair generation
    ↓
Validation
    ↓
Application
```

The Applier should support:

```python
apply=False
```

for preview mode.

With:

```python
apply=True
```

the validated repair can be written to the source file.

Potential repair categories include:

```text
url_pattern_update
href_update
attribute_update
id changes
class changes
name changes
src changes
action changes
type/value changes
```

---

# 17. Current Pipeline Status

```text
[✓] HTML snapshot generation
        │
        ▼
[✓] Structural detection
        │
        ▼
[✓] Element matching
        │
        ▼
[✓] Attribute change detection
        │
        ▼
[✓] Text change detection
        │
        ▼
[✓] Element addition detection
        │
        ▼
[✓] Element removal detection
        │
        ▼
[✓] Recommendation generation
        │
        ▼
[✓] Repair generation
        │
        ▼
[✓] Repair validation
        │
        ▼
[→] Repair application
        │
        ▼
[ ] Final scraper validation
```

The change detection and analysis portion has been tested with:

- URL changes
- URL pattern changes
- CSS class changes
- Visible text changes
- Element additions
- Element removals

---

# 18. Current Test Results

For the Coffeyville test case:

```text
Previous elements: 582
Current elements:  582
Matched elements:  398
Detected changes:  3
Recommendations:   1
Repairs:           1
```

Detected changes:

```text
3 HIGH-risk href changes
```

Recommendation:

```text
1 URL pattern change
```

Repair:

```text
1 url_pattern_update
Confidence: 0.98
```

Validation:

```text
Valid: True
Confidence: 0.98
```

Validated repair:

```text
bids.aspx?bidID=<id>
            ↓
/procurement/bid/<id>
```

---

# 19. Design Principle

The system should not assume that every website change is an `href` change.

A website can change:

```text
URL structure
HTML classes
Element IDs
Element names
Form actions
Resource URLs
Element types
Visible text
Data attributes
Element hierarchy
Elements being added
Elements being removed
```

Therefore, the architecture is intentionally divided into:

```text
Detector
Matcher
Analyzer
Recommendation Engine
Repair Engine
Validator
Applier
```

This allows additional change and repair types to be added without redesigning the complete system.

---

# 20. Safety Model

Scraper Guardian should follow a conservative repair strategy.

A repair should not be automatically applied simply because a difference was detected.

Instead:

```text
Change detected
      ↓
Evidence collected
      ↓
Risk classified
      ↓
Recommendation generated
      ↓
Repair proposed
      ↓
Repair validated
      ↓
Repair applied
      ↓
Result verified
```

High-confidence repairs can eventually be automated, while uncertain repairs can be presented for manual review.

---

# 21. Next Development Step

The immediate next task is to complete and test the **Repair Applier**.

The expected flow is:

```text
RepairSuggestion
       +
ValidationResult
       +
Scraper source file
       │
       ▼
   RepairApplier
       │
       ▼
Modified scraper source
```

The Repair Applier should:

1. Refuse to apply an invalid repair.
2. Verify that the source file exists.
3. Support multiple repair types.
4. Preserve dynamic identifiers such as bid IDs.
5. Provide a preview mode.
6. Report the number of replacements.
7. Return a structured result.
8. Avoid modifying the source when no matching pattern is found.
9. Allow the repaired source to be tested afterward.

After that, the next stage will be **post-repair validation**, where the repaired scraper is tested against the current website structure to determine whether the repair actually restores the scraper's expected behavior.

---

# Project Goal

The long-term goal of Scraper Guardian is to provide a structured workflow for maintaining web scrapers when websites change:

```text
Website changes
      ↓
Detect change
      ↓
Understand change
      ↓
Identify scraper impact
      ↓
Suggest repair
      ↓
Validate repair
      ↓
Apply repair
      ↓
Verify scraper
```

The system is therefore intended to evolve from a **change detector** into a **scraper maintenance and repair system**.
