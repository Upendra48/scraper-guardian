from scraper_guardian.detector.element_matcher import (
    ElementMatcher,
)
from scraper_guardian.detector.structural_detector import (
    ElementSnapshot,
)


def main():

    previous = ElementSnapshot(
        tag="a",
        path="/html/body/a[1]",
        attributes={
            "href": "bids.aspx?bidID=287",
        },
        text="HWY Marking Project",
    )

    current = ElementSnapshot(
        tag="a",
        path="/html/body/a[1]",
        attributes={
            "href": "/procurement/bid/287",
        },
        text="HWY Marking Project",
    )

    matcher = ElementMatcher()

    matches = matcher.match(
        previous_elements=[previous],
        current_elements=[current],
    )

    print("=" * 60)
    print("ELEMENT MATCH TEST")
    print("=" * 60)

    print(f"Matches: {len(matches)}")

    for match in matches:

        print()
        print("Previous:")
        print(match.previous)

        print()
        print("Current:")
        print(match.current)

        print()
        print(
            f"Score: {match.score:.2f}"
        )
        print()
        
        print("Evidence:")
        for evidence in match.evidence:
            print(f"    ✓ {evidence}")


if __name__ == "__main__":
    main()
    