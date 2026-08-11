from __future__ import annotations

from pathlib import Path

from scraper_guardian.detector.structural_detector import (
    StructuralDetector,
)
from scraper_guardian.detector.element_matcher import (
    ElementMatcher,
)
from scraper_guardian.detector.element_change_detector import (
    ElementChangeDetector,
)


BASE_DIR = Path(
    "snapshots/beaconbid/2026-08-11"
)

PREVIOUS = (
    BASE_DIR
    / "20260811_042013"
    / "normalized.html"
)

CURRENT = (
    BASE_DIR
    / "test_modified.html"
)


def load_html(path: Path) -> str:
    return path.read_text(
        encoding="utf-8"
    )


def main():

    print("=" * 70)
    print("ELEMENT CHANGE DETECTOR TEST")
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

    print(
        f"Previous elements: {len(previous_elements)}"
    )

    print(
        f"Current elements:  {len(current_elements)}"
    )

    matcher = ElementMatcher(
    )

    matches = matcher.match(
        previous_elements,
        current_elements,
    )

    print(
        f"Matched elements:   {len(matches)}"
    )

    change_detector = ElementChangeDetector()

    structural_changes = (
        change_detector.detect(
            previous_elements,
            current_elements,
            matches,
        )
    )

    print(
        f"Structural changes: {len(structural_changes)}"
    )

    print()
    print("=" * 70)
    print("STRUCTURAL CHANGES")
    print("=" * 70)

    for index, change in enumerate(
        structural_changes[:30],
        start=1,
    ):

        print()
        print(
            f"[CHANGE {index}]"
        )

        print(
            f"Type:     {change.change_type}"
        )

        print(
            f"Tag:      {change.tag}"
        )

        print(
            f"Path:     {change.path}"
        )

        print(
            f"Severity: {change.severity}"
        )

        print(
            f"Impact:   {change.impact}"
        )

        print("Evidence:")

        for evidence in change.evidence:
            print(
                f" [OK] {evidence}"
            )


if __name__ == "__main__":
    main()