from scraper_guardian.detector.change_analyzer import (
    ChangeAnalyzer,
)
from scraper_guardian.repair.repair_engine import (
    RepairEngine,
)


def main():

    analyzer = ChangeAnalyzer()

    changes = [
        {
            "type": "url_pattern_changed",
            "severity": "HIGH",
        }
    ]

    repairs = RepairEngine().generate_repairs(
        changes
    )

    print("=" * 70)
    print("REPAIR ENGINE TEST")
    print("=" * 70)

    print(f"Repairs generated: {len(repairs)}")

    for index, repair in enumerate(
        repairs,
        start=1,
    ):

        print(f"\n[REPAIR {index}]")

        print(
            f"Type:       {repair.repair_type}"
        )

        print(
            f"Severity:   {repair.severity}"
        )

        print(
            f"Old:        {repair.old_pattern}"
        )

        print(
            f"New:        {repair.new_pattern}"
        )

        print(
            f"Confidence: {repair.confidence:.2f}"
        )

        print(
            f"Reason:     {repair.reason}"
        )


if __name__ == "__main__":
    main()