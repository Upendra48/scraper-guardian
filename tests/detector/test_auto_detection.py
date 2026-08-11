from scraper_guardian.detector.hash_detector import (
    HashChangeDetector,
)
from scraper_guardian.snapshot.history import (
    SnapshotHistory,
)


def main():

    site_name = "coffeyville_kansas"

    history = SnapshotHistory()

    previous = history.get_previous(site_name)
    current = history.get_latest(site_name)

    if current is None:
        print("No snapshots found.")
        return

    if previous is None:
        print("Only one snapshot exists.")
        return

    detector = HashChangeDetector()

    result = detector.compare(
        previous_snapshot=previous,
        current_snapshot=current,
    )

    print("=" * 60)
    print("AUTOMATIC CHANGE DETECTION")
    print("=" * 60)

    print(f"Site:           {site_name}")
    print(f"Previous:       {previous}")
    print(f"Current:        {current}")
    print(f"Changed:        {result.changed}")
    print(f"Previous hash:  {result.previous_hash}")
    print(f"Current hash:   {result.current_hash}")
    print(f"Reason:         {result.reason}")


if __name__ == "__main__":
    main()