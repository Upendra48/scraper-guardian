from scraper_guardian.snapshot.collector import SnapshotCollector


URL = "https://www.coffeyville.com/bids.aspx"


def main():
    collector = SnapshotCollector()

    snapshot_dir = collector.collect(
        url=URL,
        site_name="coffeyville_kansas",
    )

    print("=" * 60)
    print("SNAPSHOT CREATED")
    print("=" * 60)
    print(f"Location: {snapshot_dir}")


if __name__ == "__main__":
    main()