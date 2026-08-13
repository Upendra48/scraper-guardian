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
    

def build_repair_context(
    detected_changes,
    structural_changes,
    recommendations,
):
    """
    Convert detected changes into repair-oriented context
    that can be passed to an LLM.
    """

    repair_context = {
        "high_risk_changes": [],
        "selector_changes": [],
        "url_changes": [],
        "removed_elements": [],
        "added_elements": [],
        "text_changes": [],
        "other_changes": [],
    }

    # --------------------------------------------------
    # Analyzer changes
    # --------------------------------------------------

    for change in detected_changes:

        attribute = change.attribute
        change_type = change.change_type

        item = {
            "change_type": change_type,
            "tag": change.tag,
            "path": change.path,
            "attribute": attribute,
            "old_value": change.old_value,
            "new_value": change.new_value,
            "severity": change.severity,
            "impact": change.impact,
            "evidence": change.evidence,
        }

        # URL changes
        if attribute in {"href", "src", "action"}:

            repair_context["url_changes"].append(item)

            if change.severity == "HIGH":
                repair_context["high_risk_changes"].append({
                    "category": "url_change",
                    "tag": change.tag,
                    "path": change.path,
                    "attribute": attribute,
                    "old_value": change.old_value,
                    "new_value": change.new_value,
                    "impact": change.impact,
                })

        # Selector-related changes
        elif attribute in {
            "id",
            "class",
            "name",
        }:

            repair_context["selector_changes"].append(item)

            if change.severity == "HIGH":
                repair_context["high_risk_changes"].append({
                    "category": "selector_change",
                    "tag": change.tag,
                    "path": change.path,
                    "attribute": attribute,
                    "old_value": change.old_value,
                    "new_value": change.new_value,
                    "impact": change.impact,
                })

        # Text changes
        elif change_type == "text_changed":

            repair_context["text_changes"].append(item)

        # Everything else
        else:

            repair_context["other_changes"].append(item)

            if change.severity == "HIGH":
                repair_context["high_risk_changes"].append({
                    "category": "attribute_change",
                    "tag": change.tag,
                    "path": change.path,
                    "attribute": attribute,
                    "old_value": change.old_value,
                    "new_value": change.new_value,
                    "impact": change.impact,
                })

    # --------------------------------------------------
    # Structural changes
    # --------------------------------------------------

    for change in structural_changes:

        item = {
            "change_type": change.change_type,
            "tag": change.tag,
            "path": change.path,
            "severity": getattr(
                change,
                "severity",
                "HIGH",
            ),
            "impact": getattr(
                change,
                "impact",
                "",
            ),
            "details": getattr(
                change,
                "details",
                "",
            ),
            "evidence": getattr(
                change,
                "evidence",
                [],
            ),
        }

        if change.change_type == "element_removed":

            repair_context["removed_elements"].append(item)

            repair_context["high_risk_changes"].append({
                "category": "element_removed",
                "tag": change.tag,
                "path": change.path,
                "impact": getattr(
                    change,
                    "impact",
                    "Element was removed from the page.",
                ),
            })

        elif change.change_type == "element_added":

            repair_context["added_elements"].append(item)

        elif change.change_type == "text_changed":

            repair_context["text_changes"].append(item)

    # --------------------------------------------------
    # Overall repair guidance
    # --------------------------------------------------

    repair_context["repair_guidance"] = {
        "total_high_risk_changes": len(
            repair_context["high_risk_changes"]
        ),

        "instructions": [
            "Inspect the scraper source for logic affected by the detected changes.",
            "Prefer evidence from the current HTML when determining replacement selectors or URLs.",
            "Do not modify scraper code solely because a low-risk change was detected.",
            "Preserve dynamic identifiers and variable parts of URLs.",
            "Validate proposed repairs against the current HTML before applying them.",
        ],
    }

    return repair_context    


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
    
        # ==========================================================
    # 6. Build LLM-oriented repair context
    # ==========================================================

    llm_repair_context = build_repair_context(
        detected_changes=detected_changes,
        structural_changes=structural_changes,
        recommendations=recommendations,
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
        
        "repair-context": llm_repair_context,

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