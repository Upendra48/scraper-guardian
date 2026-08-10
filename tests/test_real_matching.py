from pathlib import Path

from bs4 import BeautifulSoup

from scraper_guardian.detector.element_matcher import (
    ElementMatcher,
)
from scraper_guardian.detector.structural_detector import (
    ElementSnapshot,
)


PREVIOUS = Path(
    "snapshots/coffeyville_kansas/2026-08-10/"
    "20260810_054925/normalized.html"
)

CURRENT = Path(
    "snapshots/coffeyville_kansas/2026-08-10/"
    "20260810_054940/normalized.html"
)


def build_snapshots(html: str):

    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    elements = []

    for element in soup.find_all(True):

        attributes = {}

        for key, value in element.attrs.items():

            if isinstance(value, list):
                value = " ".join(value)

            attributes[key] = str(value)

        text = element.get_text(
            " ",
            strip=True,
        )

        elements.append(
            ElementSnapshot(
                tag=element.name,
                path=get_element_path(element),
                attributes=attributes,
                text=text,
            )
        )
        
        

    return elements


def get_element_path(element) -> str:
    """
    Generate an XPath-like path for a BeautifulSoup element.
    """

    path_parts = []

    current = element

    while current is not None:

        if not getattr(
            current,
            "name",
            None,
        ):
            break

        parent = current.parent

        if parent is None:
            break

        # Find this element's position among
        # siblings with the same tag.
        index = 1

        for sibling in parent.find_all(
            current.name,
            recursive=False,
        ):

            if sibling is current:
                break

            index += 1

        path_parts.append(
            f"{current.name}[{index}]"
        )

        current = parent

    path_parts.reverse()

    return "/" + "/".join(
        path_parts
    )

def main():

    previous_html = PREVIOUS.read_text(
        encoding="utf-8"
    )

    current_html = CURRENT.read_text(
        encoding="utf-8"
    )

    previous_elements = build_snapshots(
        previous_html
    )

    current_elements = build_snapshots(
        current_html
    )

    print("=" * 70)
    print("REAL HTML ELEMENT MATCHING")
    print("=" * 70)

    print(
        f"Previous elements: {len(previous_elements)}"
    )

    print(
        f"Current elements:  {len(current_elements)}"
    )

    matcher = ElementMatcher(
        minimum_score=0.80
    )

    matches = matcher.match(
        previous_elements,
        current_elements,
    )

    print(
        f"Matched elements:   {len(matches)}"
    )

    print()
    print("## Sample matches")
    print("=" * 70)

    if not matches:
        print("No matches found.")
        return

    for index, match in enumerate(
        matches[:10],
        start=1,
    ):

        print()
        print(f"[MATCH {index}]")
        print("-" * 70)

        print(
            f"Tag:   {match.previous.tag}"
        )

        print(
            f"Score: {match.score:.2f}"
        )

        print()

        print(
            "Previous text:"
        )

        print(
            repr(match.previous.text[:200])
        )

        print()

        print(
            "Current text:"
        )

        print(
            repr(match.current.text[:200])
        )

        print()

        print(
            "Previous attributes:"
        )

        print(
            match.previous.attributes
        )

        print()

        print(
            "Current attributes:"
        )

        print(
            match.current.attributes
        )

        print()

        print(
            "Evidence:"
        )

        for evidence in match.evidence:

            print(
                f"  ✓ {evidence}"
            )

        print("=" * 70)
        
        
        


if __name__ == "__main__":
    main()