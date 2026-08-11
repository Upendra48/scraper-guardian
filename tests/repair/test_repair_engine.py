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
from scraper_guardian.repair.repair_engine import (
    RepairEngine,
)


PREVIOUS_HTML = (
    "snapshots/beaconbid/2026-08-11/"
    "20260811_042013/normalized.html"
)

CURRENT_HTML = (
    "snapshots/beaconbid/2026-08-11/"
    "test_modified.html"
)


def main():

    print("=" * 70)
    print("REPAIR ENGINE TEST")
    print("=" * 70)

    # --------------------------------------------------
    # 1. Load snapshots
    # --------------------------------------------------

    detector = StructuralDetector()

    previous_elements = detector.extract_elements(
        open(PREVIOUS_HTML, encoding="utf-8").read()
    )

    current_elements = detector.extract_elements(
        open(CURRENT_HTML, encoding="utf-8").read()
    )

    print(
        f"Previous elements: {len(previous_elements)}"
    )

    print(
        f"Current elements:  {len(current_elements)}"
    )

    # --------------------------------------------------
    # 2. Match elements
    # --------------------------------------------------

    matcher = ElementMatcher()

    matches = matcher.match(
        previous_elements,
        current_elements,
    )

    print(
        f"Matched elements:   {len(matches)}"
    )

    # --------------------------------------------------
    # 3. Analyze matched elements
    # --------------------------------------------------

    analyzer = ChangeAnalyzer()

    changes = analyzer.analyze(
        matches
    )

    # --------------------------------------------------
    # 4. Detect added / removed elements
    # --------------------------------------------------

    change_detector = ElementChangeDetector()

    structural_changes = change_detector.detect(
        previous_elements,
        current_elements,
        matches,
    )

    # --------------------------------------------------
    # 5. Generate recommendations
    # --------------------------------------------------

    recommendations = analyzer.generate_recommendations(
        changes
    )

    print(
        f"Detected changes:   {len(changes)}"
    )

    print(
        f"Structural changes: {len(structural_changes)}"
    )

    print(
        f"Recommendations:    {len(recommendations)}"
    )

    # --------------------------------------------------
    # 6. Combine actionable information
    # --------------------------------------------------

    repair_input = []

    for recommendation in recommendations:
        repair_input.append(
            recommendation
        )

    # Structural additions/removals are currently
    # reported but are not automatically converted
    # into scraper repairs unless RepairEngine supports
    # that repair type.

    for structural_change in structural_changes:

        repair_input.append(
            {
                "type": structural_change.change_type,
                "severity": structural_change.severity,
            }
        )

    # --------------------------------------------------
    # 7. Generate repairs
    # --------------------------------------------------

    repairs = RepairEngine().generate_repairs(
        repair_input
    )

    print()

    print("=" * 70)
    print("REPAIRS")
    print("=" * 70)

    print(
        f"Repairs generated: {len(repairs)}"
    )

    for index, repair in enumerate(
        repairs,
        start=1,
    ):

        print(
            f"\n[REPAIR {index}]"
        )

        print(
            f"Type:       {repair.repair_type}"
        )

        print(
            f"Severity:   {repair.severity}"
        )

        print(
            f"Old:        {repair.old_pattern}"
        )

        print(
            f"New:        {repair.new_pattern}"
        )

        print(
            f"Confidence: {repair.confidence:.2f}"
        )

        print(
            f"Reason:     {repair.reason}"
        )


if __name__ == "__main__":
    main()