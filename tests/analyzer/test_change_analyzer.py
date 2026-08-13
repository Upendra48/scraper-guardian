from pathlib import Path

from bs4 import BeautifulSoup

from scraper_guardian.detector.structural_detector import (
    StructuralDetector,
)

from scraper_guardian.detector.element_matcher import (
    ElementMatcher,
)

from scraper_guardian.detector.change_analyzer import (
    ChangeAnalyzer,
)


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


def load_html(path: Path) -> str:

    return path.read_text(
        encoding="utf-8"
    )


def main():

    print("=" * 70)
    print("CHANGE ANALYZER TEST")
    print("=" * 70)

    previous_html = load_html(
        PREVIOUS
    )

    current_html = load_html(
        CURRENT
    )

    detector = StructuralDetector()

    previous_elements = detector.extract_elements(
        previous_html
    )

    current_elements = detector.extract_elements(
        current_html
    )
    
    # previous_elements = list(previous_elements.values())
    # current_elements = list(current_elements.values())

    print(
        f"Previous elements: "
        f"{len(previous_elements)}"
    )

    print(
        f"Current elements:  "
        f"{len(current_elements)}"
    )

    # Convert dictionaries to lists.
    # previous_list = list(
    #     previous_elements.values()
    # )

    # current_list = list(
    #     current_elements.values()
    # )

    matcher = ElementMatcher(
    )

    matches = matcher.match(
        previous_elements,
        current_elements,
    )

    print(
        f"Matched elements:   "
        f"{len(matches)}"
    )

    analyzer = ChangeAnalyzer()

    changes = analyzer.analyze(
        matches
    )
    
    recommendations = analyzer.generate_recommendations(changes)

    print("\n" + "=" * 70)
    print("RECOMMENDATIONS")
    print("=" * 70)

    for index, recommendation in enumerate(
        recommendations,
        start=1,
    ):
        print(f"\n[{index}]")
        print(f"Type:     {recommendation['type']}")
        print(f"Severity: {recommendation['severity']}")
        print(f"Message:  {recommendation['message']}")

    print(
        f"Detected changes:   "
        f"{len(changes)}"
    )

    print()

    print("=" * 70)
    print("DETECTED CHANGES")
    print("=" * 70)

    for index, change in enumerate(
        changes,
        start=1,
    ):

        print()
        print(
            f"[CHANGE {index}]"
        )

        print(
            f"Type:       "
            f"{change.change_type}"
        )

        print(
            f"Tag:        "
            f"{change.tag}"
        )

        print(
            f"Path:       "
            f"{change.path}"
        )

        if change.attribute:

            print(
                f"Attribute:  "
                f"{change.attribute}"
            )

        print(
            f"Severity:   "
            f"{change.severity}"
        )

        print(
            f"Old:        "
            f"{change.old_value}"
        )

        print(
            f"New:        "
            f"{change.new_value}"
        )

        print(
            f"Impact:     "
            f"{change.impact}"
        )

        if change.evidence:

            print("Evidence:")

            for evidence in change.evidence:

                print(
                    f" [OK]  {evidence}"
                )

        print("-" * 70)


if __name__ == "__main__":
    main()