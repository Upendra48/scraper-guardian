from scraper_guardian.detector.structural_detector import (
    StructuralDetector,
)


PREVIOUS = (
    "snapshots/coffeyville_kansas/"
    "2026-08-10/20260810_054940/normalized.html"
)

CURRENT = (
    "snapshots/coffeyville_kansas/"
    "2026-08-10/TEST_BID_LINK_CHANGED/normalized.html"
)


def main():

    detector = StructuralDetector()

    result = detector.compare(
        previous_html=PREVIOUS,
        current_html=CURRENT,
    )

    print("=" * 70)
    print("STRUCTURAL HTML DIFF")
    print("=" * 70)

    print(f"Changed: {result.changed}")
    print(f"Changes: {len(result.changes)}")
    print()

    for change in result.changes:
        print(
            f"[{change.change_type}] "
            f"{change.tag}"
        )

        print(f"Path:    {change.path}")
        print(f"Details: {change.details}")
        
        if change.old_value is not None:
            print(f"Old:     {change.old_value}")
            
        if change.new_value is not None:
            print(f"New:     {change.new_value}")    
            
        print("-" * 70)


if __name__ == "__main__":
    main()