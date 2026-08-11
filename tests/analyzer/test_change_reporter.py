from pathlib import Path

from scraper_guardian.detector.structural_detector import (
    StructuralDetector,
)

from scraper_guardian.detector.element_matcher import (
    ElementMatcher,
)

from scraper_guardian.detector.change_analyzer import (
    ChangeAnalyzer,
)

from scraper_guardian.reporter.change_reporter import (
    ChangeReporter,
)


BASE_DIR = Path(__file__).resolve().parents[1]


PREVIOUS = (
    BASE_DIR
    / "snapshots"
    / "coffeyville_kansas"
    / "2026-08-10"
    / "20260810_054925"
    / "normalized.html"
)


CURRENT = (
    BASE_DIR
    / "snapshots"
    / "coffeyville_kansas"
    / "2026-08-10"
    / "manual_test"
    / "normalized.html"
)


def load_html(path: Path) -> str:

    if not path.exists():
        raise FileNotFoundError(
            f"Snapshot not found:\n{path}"
        )

    return path.read_text(
        encoding="utf-8"
    )


def main():

    print("=" * 70)
    print("CHANGE REPORTER TEST")
    print("=" * 70)

    previous_html = load_html(
        PREVIOUS
    )

    current_html = load_html(
        CURRENT
    )

    detector = StructuralDetector()

    previous_elements = (
        detector.extract_elements(
            previous_html
        )
    )

    current_elements = (
        detector.extract_elements(
            current_html
        )
    )

    # StructuralDetector currently returns
    # dictionaries of ElementSnapshot objects.
    previous_elements = list(
        previous_elements.values()
    )

    current_elements = list(
        current_elements.values()
    )

    print(
        f"Previous elements: {len(previous_elements)}"
    )

    print(
        f"Current elements:  {len(current_elements)}"
    )

    matcher = ElementMatcher(
        minimum_score=0.50
    )

    matches = matcher.match(
        previous_elements,
        current_elements,
    )

    print(
        f"Matched elements:   {len(matches)}"
    )

    analyzer = ChangeAnalyzer()

    changes = analyzer.analyze(
        matches
    )

    print(
        f"Detected changes:   {len(changes)}"
    )

    reporter = ChangeReporter()

    report = reporter.generate(
        changes
    )

    print()

    print(
        reporter.format_text(report)
    )


if __name__ == "__main__":
    main()
