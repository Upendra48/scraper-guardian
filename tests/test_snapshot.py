from scraper_guardian.snapshot.collector import SnapshotCollector


URL = "https://www.clinton.edu/business-office/bids.php"


def main():
    collector = SnapshotCollector()

    snapshot_dir = collector.collect(
        url=URL,
        site_name="Clinton Edu",
    )

    print("=" * 60)
    print("SNAPSHOT CREATED")
    print("=" * 60)
    print(f"Location: {snapshot_dir}")


if __name__ == "__main__":
    main()