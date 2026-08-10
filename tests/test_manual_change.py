from scraper_guardian.detector.hash_detector import (
    HashChangeDetector,
)


PREVIOUS = (
    "snapshots/coffeyville_kansas/"
    "2026-08-10/20260810_054940"
)

CURRENT = (
    "snapshots/coffeyville_kansas/"
    "2026-08-10/TEST_CHANGED"
)


def main():

    detector = HashChangeDetector()

    result = detector.compare(
        previous_snapshot=PREVIOUS,
        current_snapshot=CURRENT,
    )

    print("=" * 60)
    print("MANUAL CHANGE TEST")
    print("=" * 60)

    print(f"Changed:        {result.changed}")
    print(f"Previous hash:  {result.previous_hash}")
    print(f"Current hash:   {result.current_hash}")
    print(f"Reason:         {result.reason}")


if __name__ == "__main__":
    main()