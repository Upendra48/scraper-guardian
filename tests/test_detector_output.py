from pathlib import Path

from bs4 import BeautifulSoup

from scraper_guardian.detector.structural_detector import (
    StructuralDetector,
)


SNAPSHOT = Path(
    "snapshots/coffeyville_kansas/2026-08-10/"
    "20260810_054940/normalized.html"
)


def main():

    html = SNAPSHOT.read_text(
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

    print("=" * 70)
    print("STRUCTURAL DETECTOR OUTPUT")
    print("=" * 70)

    print(
        "Type:",
        type(elements)
    )

    print(
        "Length:",
        len(elements)
    )

    print()

    for index, element in enumerate(
        list(elements.values())[:10],
        start=1,
    ):

        print(
            f"[{index}]"
        )

        print(
            "Type:",
            type(element)
        )

        print(
            "Value:",
            repr(element)
        )

        print(
            "Has tag:",
            hasattr(
                element,
                "tag",
            )
        )

        print(
            "Has path:",
            hasattr(
                element,
                "path",
            )
        )

        print(
            "Has attributes:",
            hasattr(
                element,
                "attributes",
            )
        )

        print()


if __name__ == "__main__":
    main()