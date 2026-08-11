from __future__ import annotations

from pathlib import Path
import tempfile

from scraper_guardian.repair.repair_applier import RepairApplier
from scraper_guardian.repair.repair_engine import RepairSuggestion
from scraper_guardian.repair.repair_validator import ValidationResult


def make_validation(
    valid: bool = True,
    confidence: float = 0.98,
) -> ValidationResult:

    return ValidationResult(
        valid=valid,
        repair_type="url_pattern_update",
        confidence=confidence,
        message="Validation successful.",
        evidence=[
            "Test validation",
        ],
    )


def make_url_repair() -> RepairSuggestion:

    return RepairSuggestion(
        repair_type="url_pattern_update",
        severity="HIGH",
        old_pattern="bids.aspx?bidID=<id>",
        new_pattern="/procurement/bid/<id>",
        confidence=0.98,
        reason=(
            "The bid URL structure changed. "
            "The scraper should update its URL construction logic."
        ),
    )


def make_href_repair() -> RepairSuggestion:

    return RepairSuggestion(
        repair_type="href_update",
        severity="HIGH",
        old_pattern="bids.aspx?bidID=287",
        new_pattern="/procurement/bid/287",
        confidence=0.98,
        reason="Href destination changed.",
    )


def make_attribute_repair() -> RepairSuggestion:

    repair = RepairSuggestion(
        repair_type="attribute_update",
        severity="HIGH",
        old_pattern="bid-row",
        new_pattern="procurement-row",
        confidence=0.95,
        reason="CSS class changed.",
    )

    # The generic attribute repair uses these fields.
    repair.attribute = "class"
    repair.old_value = "bid-row"
    repair.new_value = "procurement-row"

    return repair


def main():

    print("=" * 70)
    print("REPAIR APPLIER TEST")
    print("=" * 70)

    applier = RepairApplier()

    # ==========================================================
    # TEST 1: Validation failure
    # ==========================================================

    print("\n[TEST 1] Validation failure")

    repair = make_url_repair()

    validation = make_validation(
        valid=False,
        confidence=0.0,
    )

    result = applier.apply(
        repair=repair,
        validation=validation,
        source_path="does_not_matter.py",
        apply=False,
    )

    assert result.success is False
    assert result.replacements == 0

    print("PASS")
    print(result.message)

    # ==========================================================
    # TEST 2: Missing source file
    # ==========================================================

    print("\n[TEST 2] Missing source file")

    validation = make_validation()

    result = applier.apply(
        repair=repair,
        validation=validation,
        source_path="missing_scraper.py",
        apply=False,
    )

    assert result.success is False
    assert result.replacements == 0
    assert "does not exist" in result.message

    print("PASS")
    print(result.message)

    # ==========================================================
    # TEST 3: URL pattern update - preview
    # ==========================================================

    print("\n[TEST 3] URL pattern update - preview")

    source = """
BASE_URL = "https://example.com"

bid_id = 287

bid_url = (
    BASE_URL
    + "/bids.aspx?bidID="
    + str(bid_id)
)
"""

    with tempfile.TemporaryDirectory() as temp_dir:

        source_path = (
            Path(temp_dir)
            / "scraper.py"
        )

        source_path.write_text(
            source,
            encoding="utf-8",
        )

        result = applier.apply(
            repair=make_url_repair(),
            validation=make_validation(),
            source_path=source_path,
            apply=False,
        )

        assert result.success is True
        assert result.replacements == 1

        # File must NOT be modified in preview mode.
        original = source_path.read_text(
            encoding="utf-8",
        )

        assert (
            "/bids.aspx?bidID="
            in original
        )

        # Changed source should contain new pattern.
        assert (
            "/procurement/bid/"
            in result.changed_source
        )

        print("PASS")
        print(
            f"Replacements: {result.replacements}"
        )
        print(result.message)

    # ==========================================================
    # TEST 4: URL pattern update - actual apply
    # ==========================================================

    print("\n[TEST 4] URL pattern update - apply")

    source = """
bid_id = 288
bid_url = "bids.aspx?bidID=" + str(bid_id)
"""

    with tempfile.TemporaryDirectory() as temp_dir:

        source_path = (
            Path(temp_dir)
            / "scraper.py"
        )

        source_path.write_text(
            source,
            encoding="utf-8",
        )

        result = applier.apply(
            repair=make_url_repair(),
            validation=make_validation(),
            source_path=source_path,
            apply=True,
        )

        assert result.success is True
        assert result.replacements == 1

        modified = source_path.read_text(
            encoding="utf-8",
        )

        assert (
            "/procurement/bid/"
            in modified
        )

        assert (
            "bids.aspx?bidID="
            not in modified
        )

        print("PASS")
        print(
            f"Replacements: {result.replacements}"
        )
        print(result.message)

    # ==========================================================
    # TEST 5: href_update
    # ==========================================================

    print("\n[TEST 5] Href update")

    source = """
<a href="bids.aspx?bidID=287">
    HWY Marking Project
</a>
"""

    with tempfile.TemporaryDirectory() as temp_dir:

        source_path = (
            Path(temp_dir)
            / "scraper.py"
        )

        source_path.write_text(
            source,
            encoding="utf-8",
        )

        result = applier.apply(
            repair=make_href_repair(),
            validation=make_validation(),
            source_path=source_path,
            apply=False,
        )

        assert result.success is True
        assert result.replacements == 1

        assert (
            'href="/procurement/bid/287"'
            in result.changed_source
        )

        print("PASS")
        print(
            f"Replacements: {result.replacements}"
        )

    # ==========================================================
    # TEST 6: Generic attribute update
    # ==========================================================

    print("\n[TEST 6] Generic attribute update")

    source = """
<div class="bid-row">
    <a href="/bid/287">
        HWY Marking Project
    </a>
</div>
"""

    with tempfile.TemporaryDirectory() as temp_dir:

        source_path = (
            Path(temp_dir)
            / "scraper.py"
        )

        source_path.write_text(
            source,
            encoding="utf-8",
        )

        result = applier.apply(
            repair=make_attribute_repair(),
            validation=make_validation(),
            source_path=source_path,
            apply=False,
        )

        assert result.success is True
        assert result.replacements == 1

        assert (
            'class="procurement-row"'
            in result.changed_source
        )

        assert (
            'class="bid-row"'
            not in result.changed_source
        )

        print("PASS")
        print(
            f"Replacements: {result.replacements}"
        )

    # ==========================================================
    # TEST 7: No matching source
    # ==========================================================

    print("\n[TEST 7] No matching source")

    source = """
bid_url = "/some/other/path"
"""

    with tempfile.TemporaryDirectory() as temp_dir:

        source_path = (
            Path(temp_dir)
            / "scraper.py"
        )

        source_path.write_text(
            source,
            encoding="utf-8",
        )

        result = applier.apply(
            repair=make_url_repair(),
            validation=make_validation(),
            source_path=source_path,
            apply=False,
        )

        assert result.success is False
        assert result.replacements == 0

        print("PASS")
        print(result.message)

    # ==========================================================
    # TEST 8: Generic URL pattern
    # ==========================================================

    print("\n[TEST 8] Generic URL pattern")

    source = """
document_id = 123

url = (
    "/documents/"
    + str(document_id)
    + "/download"
)
"""

    generic_repair = RepairSuggestion(
        repair_type="url_pattern_update",
        severity="HIGH",
        old_pattern="/documents/<id>",
        new_pattern="/procurement/document/<id>",
        confidence=0.95,
        reason="Document URL structure changed.",
    )

    with tempfile.TemporaryDirectory() as temp_dir:

        source_path = (
            Path(temp_dir)
            / "scraper.py"
        )

        source_path.write_text(
            source,
            encoding="utf-8",
        )

        result = applier.apply(
            repair=generic_repair,
            validation=make_validation(),
            source_path=source_path,
            apply=False,
        )

        assert result.success is True
        assert result.replacements == 1

        assert (
            "/procurement/document/"
            in result.changed_source
        )

        print("PASS")
        print(
            f"Replacements: {result.replacements}"
        )

    # ==========================================================
    # SUMMARY
    # ==========================================================

    print("\n" + "=" * 70)
    print("ALL REPAIR APPLIER TESTS PASSED")
    print("=" * 70)


if __name__ == "__main__":
    main()