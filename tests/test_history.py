from scraper_guardian.snapshot.history import SnapshotHistory


def main():
    history = SnapshotHistory()

    snapshots = history.get_site_snapshots(
        "coffeyville_kansas"
    )

    print("=" * 60)
    print("SNAPSHOT HISTORY")
    print("=" * 60)

    print(f"Total snapshots: {len(snapshots)}")

    for snapshot in snapshots:
        print(f"- {snapshot}")

    print()

    latest = history.get_latest(
        "coffeyville_kansas"
    )

    previous = history.get_previous(
        "coffeyville_kansas"
    )

    print(f"Latest:   {latest}")
    print(f"Previous: {previous}")


if __name__ == "__main__":
    main()