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

Each element is represented by an `ElementSnapshot` containing information such as:

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

The detector currently produces:

```text
Previous elements: 582
Current elements:  582
```

The element collection is stored as a dictionary keyed by element/path information, while the matcher operates on the `ElementSnapshot` values.

---

## 2. Element Matcher

The Element Matcher determines whether an element in the previous HTML is probably the same element as an element in the current HTML.

Matching is based on deterministic evidence including:

* HTML tag
* Element ID
* `name`
* Visible text
* Matching attributes
* Shared numeric identifiers

The matcher assigns a confidence score to each potential match.

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

The matcher currently produces:

```text
Previous elements: 582
Current elements:  582
Matched elements:  398
```

The matcher is intentionally separate from change analysis.

Its responsibility is:

> "Are these probably the same elements?"

The Change Analyzer then answers:

> "If they are the same elements, what changed?"

---

## 3. Change Analyzer

The Change Analyzer examines matched elements and identifies meaningful differences.

It is **not limited to `href` changes**.

It currently considers changes to important HTML attributes including:

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

### Attribute changes

Examples:

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

Changes are classified by severity:

```text
HIGH
MEDIUM
LOW
```

For example:

### `href`

```text
HIGH
```

because a changed link destination can directly break URL extraction.

### `id`

```text
HIGH
```

because ID-based selectors may stop working.

### `class`

```text
MEDIUM
```

because CSS/XPath selectors based on classes may be affected.

### Text

Text changes on interactive elements such as links and buttons are treated as more important because scrapers may use visible text as selectors.

---

# Example: Coffeyville Bid URL Change

The current test case uses the City of Coffeyville bid page.

Three bid links changed from:

```text
bids.aspx?bidID=287
bids.aspx?bidID=288
bids.aspx?bidID=286
```

to:

```text
/procurement/bid/287
/procurement/bid/288
/procurement/bid/286
```

The Change Analyzer detected:

```text
Previous elements: 582
Current elements:  582
Matched elements:  398
Detected changes:  3
```

### Detected Change 1

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

Impact:

```text
Link destination changed. A scraper using this URL
or URL pattern may need to be updated.
```

The same change was detected for bid IDs `288` and `286`.

---

# 4. Recommendation Generation

After detecting changes, Scraper Guardian generates a higher-level recommendation.

For the Coffeyville example:

```text
Type:     url_pattern_changed
Severity: HIGH

The URL structure appears to have changed from:

bids.aspx?bidID=

to:

/procurement/bid/

A scraper using the old URL pattern should be reviewed.
```

This is important because individual HTML changes can be grouped into a meaningful scraper-level recommendation.

Instead of reporting only:

```text
href changed
```

the system can explain:

```text
The bid URL structure changed.
```

---

# 5. Repair Engine

The Repair Engine converts recommendations into concrete repair suggestions.

For the Coffeyville example:

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

The repair is represented as a structured `RepairSuggestion`.

The Repair Engine does not directly modify scraper source code.

Its responsibility is to answer:

> "What change should the scraper make?"

---

# 6. Repair Validator

Before a repair can be applied, it is validated against the current HTML.

The validator checks that the proposed repair actually exists in the updated page.

For the Coffeyville example:

```text
======================================================================
REPAIR VALIDATOR TEST
======================================================================

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

Evidence:

```text
✓ Found 3 current href(s) matching the new URL pattern
✓ Old URL pattern is no longer present in the current HTML
✓ Extracted identifiers: 286, 287, 288
✓ New pattern contains the expected procurement bid URL structure
```

The validator therefore provides an additional safety layer:

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

# 7. Repair Applier

The Repair Applier is the next stage of the pipeline.

Its purpose is to apply a **validated** repair to the scraper source code.

The design intentionally separates:

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

The Applier supports a safe preview mode:

```python
apply=False
```

which generates the modified source without changing the actual scraper file.

When:

```python
apply=True
```

the validated change can be written to the source file.

The Applier is being designed as a generic component rather than an `href`-only component.

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

The exact repair type should be determined by the Repair Engine and validated before application.

---

# Current Pipeline Status

The current implementation has reached the following stage:

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
[✓] Change detection
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

---

# Current Test Results

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

The validated repair is:

```text
bids.aspx?bidID=<id>
            ↓
/procurement/bid/<id>
```

---

# Why Element Matching Is Important

HTML pages often contain hundreds of elements.

A simple comparison based on element position is unreliable because an inserted or removed element can shift the positions of every element after it.

For example:

```text
Previous:

element 1
element 2
element 3
element 4


Current:

element 1
NEW element
element 2
element 3
element 4
```

Position-based comparison would incorrectly consider many elements to be changed.

Scraper Guardian instead attempts to identify the same logical element using multiple pieces of evidence.

For example:

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

This allows the Change Analyzer to focus on actual structural changes rather than positional differences.

---

# Design Principle

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

# Safety Model

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

# Next Development Step

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
