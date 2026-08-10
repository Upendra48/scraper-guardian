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


PREVIOUS = Path(
    "snapshots/coffeyville_kansas/2026-08-10/"
    "20260810_054925/normalized.html"
)

CURRENT = Path(
    "snapshots/coffeyville_kansas/2026-08-10/"
    "20260810_054940/normalized.html"
)


def load_elements(path):

    html = Path(path).read_text(
        encoding="utf-8"
    )

    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    detector = StructuralDetector()

    elements = detector._get_elements(
        soup
    )
    
    return list(elements.values())


def main():

    print("=" * 70)
    print("CHANGE ANALYZER TEST")
    print("=" * 70)

    previous_elements = load_elements(
        PREVIOUS
    )

    current_elements = load_elements(
        CURRENT
    )

    print(
        f"Previous elements: "
        f"{len(previous_elements)}"
    )

    print(
        f"Current elements:  "
        f"{len(current_elements)}"
    )

    # ----------------------------------------------
    # MATCH
    # ----------------------------------------------

    matcher = ElementMatcher(
        minimum_score=0.50
    )

    matches = matcher.match(
        previous_elements,
        current_elements,
    )

    print(
        f"Matched elements:   "
        f"{len(matches)}"
    )

    # ----------------------------------------------
    # ANALYZE
    # ----------------------------------------------

    analyzer = ChangeAnalyzer()

    changes = analyzer.analyze(
        matches
    )

    print(
        f"Changed matched elements: "
        f"{len(changes)}"
    )

    # ----------------------------------------------
    # DISPLAY
    # ----------------------------------------------

    for index, change in enumerate(
        changes,
        start=1,
    ):

        print()
        print("=" * 70)

        print(
            f"CHANGE {index}"
        )

        print("=" * 70)

        print(
            f"Tag:    {change.tag}"
        )

        print(
            f"Impact: {change.impact}"
        )

        print(
            f"Previous path:"
        )

        print(
            f"  {change.previous_path}"
        )

        print(
            f"Current path:"
        )

        print(
            f"  {change.current_path}"
        )

        # ------------------------------------------
        # TEXT
        # ------------------------------------------

        if change.text_changed:

            print()
            print("TEXT CHANGED")

            print(
                f"Old: {change.old_text}"
            )

            print(
                f"New: {change.new_text}"
            )

        # ------------------------------------------
        # ATTRIBUTES
        # ------------------------------------------

        for attribute_change in (
            change.attribute_changes
        ):

            print()

            print(
                f"ATTRIBUTE CHANGED: "
                f"{attribute_change.attribute}"
            )

            print(
                f"Old: "
                f"{attribute_change.old_value}"
            )

            print(
                f"New: "
                f"{attribute_change.new_value}"
            )


if __name__ == "__main__":
    main()