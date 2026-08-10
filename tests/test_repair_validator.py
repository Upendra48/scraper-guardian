from __future__ import annotations

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
from scraper_guardian.repair.repair_engine import (
    RepairEngine,
)
from scraper_guardian.repair.repair_validator import (
    RepairValidator,
)


BASE_DIR = Path(
    "snapshots/coffeyville_kansas/2026-08-10"
)

PREVIOUS = (
    BASE_DIR
    / "20260810_054925"
    / "normalized.html"
)

CURRENT = (
    BASE_DIR
    / "manual_test"
    / "normalized.html"
)


def load_html(path: Path) -> str:

    return path.read_text(
        encoding="utf-8"
    )


def main():

    print("=" * 70)
    print("REPAIR VALIDATOR TEST")
    print("=" * 70)

    previous_html = load_html(
        PREVIOUS
    )

    current_html = load_html(
        CURRENT
    )

    detector = StructuralDetector()

    previous_elements = (
        detector.extract_elements(
            previous_html
        )
    )

    current_elements = (
        detector.extract_elements(
            current_html
        )
    )

    # StructuralDetector returns dictionaries.
    previous_elements = list(
        previous_elements.values()
    )

    current_elements = list(
        current_elements.values()
    )

    print(
        f"Previous elements: {len(previous_elements)}"
    )

    print(
        f"Current elements:  {len(current_elements)}"
    )

    matcher = ElementMatcher()

    matches = matcher.match(
        previous_elements,
        current_elements,
    )

    print(
        f"Matched elements:  {len(matches)}"
    )

    analyzer = ChangeAnalyzer()

    changes = analyzer.analyze(
        matches
    )

    print(
        f"Detected changes:  {len(changes)}"
    )

    recommendations = (
        analyzer.generate_recommendations(
            changes
        )
    )

    print(
        f"Recommendations:   {len(recommendations)}"
    )

    repair_engine = RepairEngine()

    repairs = (
        repair_engine.generate_repairs(
            recommendations
        )
    )

    print(
        f"Repairs:           {len(repairs)}"
    )

    validator = RepairValidator()

    print("\n" + "=" * 70)
    print("VALIDATION RESULTS")
    print("=" * 70)

    for index, repair in enumerate(
        repairs,
        start=1,
    ):

        result = validator.validate(
            repair,
            current_elements,
        )

        print(
            f"\n[REPAIR {index}]"
        )

        print(
            f"Type:       {repair.repair_type}"
        )

        print(
            f"Old:        {repair.old_pattern}"
        )

        print(
            f"New:        {repair.new_pattern}"
        )

        print(
            f"Valid:      {result.valid}"
        )

        print(
            f"Confidence: "
            f"{result.confidence:.2f}"
        )

        print(
            f"Message:    {result.message}"
        )

        if result.evidence:

            print(
                "Evidence:"
            )

            for evidence in result.evidence:

                print(
                    f"  ✓ {evidence}"
                )


if __name__ == "__main__":
    main()