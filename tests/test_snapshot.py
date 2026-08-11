from scraper_guardian.snapshot.collector import SnapshotCollector


URL = "https://www.beaconbid.com/integrations/widget/greenville-spartanburg-airport-district"


def main():
    collector = SnapshotCollector()

    snapshot_dir = collector.collect(
        url=URL,
        site_name="beaconbid",
    )

    print("=" * 60)
    print("SNAPSHOT CREATED")
    print("=" * 60)
    print(f"Location: {snapshot_dir}")


if __name__ == "__main__":
    main()