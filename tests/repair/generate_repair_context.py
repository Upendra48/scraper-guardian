from __future__ import annotations

import json
from pathlib import Path

from scraper_guardian.detector.structural_detector import (
    StructuralDetector,
)
from scraper_guardian.detector.element_matcher import (
    ElementMatcher,
)
from scraper_guardian.detector.change_analyzer import (
    ChangeAnalyzer,
)
from scraper_guardian.detector.element_change_detector import (
    ElementChangeDetector,
)

from pathlib import Path

AGENCY= "clinton"
DATE = "2026-08-13"


BASE = Path(
    "snapshots/clinton/2026-08-13"
)

PREVIOUS = (
    BASE
    / "20260813_034553"
    / "normalized.html"
)

CURRENT = (
    BASE
    / "test_modified.html"
)


OUTPUT_FILE = (
    BASE
    / "repair_context.json"
)


def element_change_to_dict(change):
    """Convert StructuralChange into JSON-safe data."""

    return {
        "change_type": change.change_type,
        "tag": change.tag,
        "path": change.path,
        "severity": getattr(change, "severity", None),
        "impact": getattr(change, "impact", ""),
        "details": getattr(change, "details", ""),
        "old_value": getattr(change, "old_value", None),
        "new_value": getattr(change, "new_value", None),
        "attribute": getattr(change, "attribute", None),
        "evidence": getattr(change, "evidence", []),
    }


def analyzer_change_to_dict(change):
    """Convert ElementChange into JSON-safe data."""

    return {
        "change_type": change.change_type,
        "tag": change.tag,
        "path": change.path,
        "attribute": change.attribute,
        "severity": change.severity,
        "impact": change.impact,
        "old_value": change.old_value,
        "new_value": change.new_value,
        "evidence": change.evidence,
    }


def main():

    print("=" * 70)
    print("REPAIR CONTEXT GENERATOR")
    print("=" * 70)

    # ==========================================================
    # 1. Load HTML snapshots
    # ==========================================================

    previous_html = PREVIOUS.read_text(
    encoding="utf-8"
)

    current_html = CURRENT.read_text(
    encoding="utf-8"
)

    # ==========================================================
    # 2. Extract elements
    # ==========================================================

    detector = StructuralDetector()

    previous_elements = detector.extract_elements(
        previous_html
    )

    current_elements = detector.extract_elements(
        current_html
    )

    print(
        f"Previous elements: {len(previous_elements)}"
    )

    print(
        f"Current elements:  {len(current_elements)}"
    )

    # ==========================================================
    # 3. Match elements
    # ==========================================================

    matcher = ElementMatcher()

    matches = matcher.match(
        previous_elements,
        current_elements,
    )

    print(
        f"Matched elements:   {len(matches)}"
    )

    # ==========================================================
    # 4. Change Analyzer
    # ==========================================================

    analyzer = ChangeAnalyzer()

    detected_changes = analyzer.analyze(
        matches
    )

    recommendations = (
        analyzer.generate_recommendations(
            detected_changes
        )
    )

    print(
        f"Detected changes:   {len(detected_changes)}"
    )

    print(
        f"Recommendations:    {len(recommendations)}"
    )

    # ==========================================================
    # 5. Element Change Detector
    # ==========================================================

    change_detector = ElementChangeDetector()

    structural_changes = change_detector.detect(
        previous_elements,
        current_elements,
        matches,
    )

    print(
        f"Structural changes: {len(structural_changes)}"
    )

    # ==========================================================
    # 6. Build Repair Context
    # ==========================================================

    repair_context = {

        "project": "Scraper Guardian",

        "source": {
            "previous_html": str(PREVIOUS),
            "current_html": str(CURRENT),
        },

        "summary": {
            "previous_elements": len(
                previous_elements
            ),
            "current_elements": len(
                current_elements
            ),
            "matched_elements": len(
                matches
            ),
            "detected_changes": len(
                detected_changes
            ),
            "structural_changes": len(
                structural_changes
            ),
            "recommendations": len(
                recommendations
            ),
        },

        "detected_changes": [
            analyzer_change_to_dict(
                change
            )
            for change in detected_changes
        ],

        "structural_changes": [
            element_change_to_dict(
                change
            )
            for change in structural_changes
        ],

        "recommendations": recommendations,

    }

    # ==========================================================
    # 7. Create output directory
    # ==========================================================

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # ==========================================================
    # 8. Save JSON
    # ==========================================================

    OUTPUT_FILE.write_text(
        json.dumps(
            repair_context,
            indent=4,
            ensure_ascii=False,
            default=str,
        ),
        encoding="utf-8",
    )

    # ==========================================================
    # 9. Display result
    # ==========================================================

    print()
    print("=" * 70)
    print("REPAIR CONTEXT CREATED")
    print("=" * 70)

    print(
        f"Location: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()