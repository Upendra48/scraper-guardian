from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from .repair_engine import RepairSuggestion
from .repair_validator import ValidationResult


@dataclass
class AppliedRepair:
    """
    Result of applying a validated repair.
    """

    success: bool
    repair_type: str
    file_path: str
    old_pattern: str
    new_pattern: str
    replacements: int
    changed_source: str
    message: str


class RepairApplier:
    """
    Apply validated RepairEngine suggestions to scraper source code.

    The applier is deliberately safe:

        apply=False
            -> preview only

        apply=True
            -> write the modified source code
    """

    # --------------------------------------------------
    # PUBLIC API
    # --------------------------------------------------

    def apply(
        self,
        repair: RepairSuggestion,
        validation: ValidationResult,
        source_path: str | Path,
        apply: bool = False,
    ) -> AppliedRepair:

        source_path = Path(source_path)

        # ----------------------------------------------
        # Validation must pass first.
        # ----------------------------------------------

        if not validation.valid:

            return AppliedRepair(
                success=False,
                repair_type=repair.repair_type,
                file_path=str(source_path),
                old_pattern=self._get_old_pattern(repair),
                new_pattern=self._get_new_pattern(repair),
                replacements=0,
                changed_source="",
                message=(
                    "Repair was not applied because "
                    "validation failed."
                ),
            )

        # ----------------------------------------------
        # File must exist.
        # ----------------------------------------------

        if not source_path.exists():

            return AppliedRepair(
                success=False,
                repair_type=repair.repair_type,
                file_path=str(source_path),
                old_pattern=self._get_old_pattern(repair),
                new_pattern=self._get_new_pattern(repair),
                replacements=0,
                changed_source="",
                message=(
                    f"Source file does not exist: "
                    f"{source_path}"
                ),
            )

        source = source_path.read_text(
            encoding="utf-8"
        )

        # ----------------------------------------------
        # Dispatch repair type.
        # ----------------------------------------------

        if repair.repair_type == "url_pattern_update":

            changed_source, replacements = (
                self._apply_url_pattern_update(
                    source,
                    repair,
                )
            )

        elif repair.repair_type == "href_update":

            changed_source, replacements = (
                self._apply_href_update(
                    source,
                    repair,
                )
            )

        elif repair.repair_type == "attribute_update":

            changed_source, replacements = (
                self._apply_attribute_update(
                    source,
                    repair,
                )
            )

        else:

            return AppliedRepair(
                success=False,
                repair_type=repair.repair_type,
                file_path=str(source_path),
                old_pattern=self._get_old_pattern(repair),
                new_pattern=self._get_new_pattern(repair),
                replacements=0,
                changed_source="",
                message=(
                    f"Unsupported repair type: "
                    f"{repair.repair_type}"
                ),
            )

        # ----------------------------------------------
        # No source change.
        # ----------------------------------------------

        if replacements == 0:

            return AppliedRepair(
                success=False,
                repair_type=repair.repair_type,
                file_path=str(source_path),
                old_pattern=self._get_old_pattern(repair),
                new_pattern=self._get_new_pattern(repair),
                replacements=0,
                changed_source=source,
                message=(
                    "No matching source pattern or attribute "
                    "value was found in the scraper source."
                ),
            )

        # ----------------------------------------------
        # Preview mode.
        # ----------------------------------------------

        if not apply:

            return AppliedRepair(
                success=True,
                repair_type=repair.repair_type,
                file_path=str(source_path),
                old_pattern=self._get_old_pattern(repair),
                new_pattern=self._get_new_pattern(repair),
                replacements=replacements,
                changed_source=changed_source,
                message=(
                    "Repair preview generated. "
                    "Source file was not modified."
                ),
            )

        # ----------------------------------------------
        # Apply the change.
        # ----------------------------------------------

        source_path.write_text(
            changed_source,
            encoding="utf-8",
        )

        return AppliedRepair(
            success=True,
            repair_type=repair.repair_type,
            file_path=str(source_path),
            old_pattern=self._get_old_pattern(repair),
            new_pattern=self._get_new_pattern(repair),
            replacements=replacements,
            changed_source=changed_source,
            message=(
                "Repair successfully applied "
                "to the scraper source."
            ),
        )

    # --------------------------------------------------
    # URL PATTERN UPDATE
    # --------------------------------------------------

    def _apply_url_pattern_update(
        self,
        source: str,
        repair: RepairSuggestion,
    ) -> tuple[str, int]:

        old_pattern = repair.old_pattern
        new_pattern = repair.new_pattern

        if not old_pattern or not new_pattern:
            return source, 0

        # ----------------------------------------------
        # Coffeyville-style URL:
        #
        # bids.aspx?bidID=<id>
        #
        # becomes:
        #
        # /procurement/bid/<id>
        # ----------------------------------------------

        old_url_regex = self._build_source_url_regex(
            old_pattern
        )

        if old_url_regex is None:
            return source, 0

        # Preserve the numeric ID while changing
        # the surrounding URL structure.
        replacement = self._build_source_replacement(
            new_pattern
        )

        if replacement is None:
            return source, 0

        changed_source, count = re.subn(
            old_url_regex,
            replacement,
            source,
            flags=re.IGNORECASE,
        )

        return changed_source, count

    # --------------------------------------------------
    # HREF UPDATE
    # --------------------------------------------------

    def _apply_href_update(
        self,
        source: str,
        repair: RepairSuggestion,
    ) -> tuple[str, int]:

        old_pattern = repair.old_pattern
        new_pattern = repair.new_pattern

        if not old_pattern or not new_pattern:
            return source, 0

        old_regex = re.escape(
            old_pattern
        )

        new_value = new_pattern

        changed_source, count = re.subn(
            old_regex,
            lambda _: new_value,
            source,
            flags=re.IGNORECASE,
        )

        return changed_source, count

    # --------------------------------------------------
    # GENERIC ATTRIBUTE UPDATE
    # --------------------------------------------------

    def _apply_attribute_update(
        self,
        source: str,
        repair: RepairSuggestion,
    ) -> tuple[str, int]:

        attribute = getattr(
            repair,
            "attribute",
            None,
        )

        old_value = getattr(
            repair,
            "old_value",
            None,
        )

        new_value = getattr(
            repair,
            "new_value",
            None,
        )

        if not attribute or old_value is None or new_value is None:
            return source, 0

        old_value = str(old_value)
        new_value = str(new_value)

        # Replace only the value of the requested HTML attribute.
        # This avoids changing unrelated occurrences of the same text.
        attribute_pattern = (
            r"(?P<prefix>\\b"
            + re.escape(str(attribute))
            + r"\\s*=\\s*[\\\"\\\'])"
            + re.escape(old_value)
            + r"(?P<quote>[\\\"\\\'])"
        )

        changed_source, count = re.subn(
            attribute_pattern,
            lambda match: (
                match.group("prefix")
                + new_value
                + match.group("quote")
            ),
            source,
            flags=re.IGNORECASE,
        )

        return changed_source, count

    # --------------------------------------------------
    # SOURCE URL REGEX
    # --------------------------------------------------

    @staticmethod
    def _build_source_url_regex(
        pattern: str,
    ) -> str | None:

        if not pattern:
            return None

        pattern = pattern.strip()

        # ----------------------------------------------
        # Convert normalized pattern into source regex.
        #
        # bids.aspx?bidID=<id>
        #
        # matches:
        #
        # "bids.aspx?bidID=" + bid_id
        # ----------------------------------------------

        escaped = re.escape(
            pattern
        )

        escaped = escaped.replace(
            r"\<id\>",
            r"(?P<bid_id>\d+)",
        )

        escaped = escaped.replace(
            r"\<bid_id\>",
            r"(?P<bid_id>\d+)",
        )

        escaped = escaped.replace(
            r"\<bidID\>",
            r"(?P<bid_id>\d+)",
        )

        return escaped

    # --------------------------------------------------
    # SOURCE REPLACEMENT
    # --------------------------------------------------

    @staticmethod
    def _build_source_replacement(
        pattern: str,
    ) -> str | None:

        if not pattern:
            return None

        # Convert the normalized repair pattern into a regex
        # replacement while preserving the identifier captured
        # from the old URL.
        #
        # Examples:
        #
        #   /procurement/bid/<id>
        #       -> /procurement/bid/\\g<bid_id>
        #
        #   /documents/<id>/download
        #       -> /documents/\\g<bid_id>/download
        #
        # Do NOT hard-code a particular site's URL structure here.
        replacement = pattern.strip()

        replacement = replacement.replace(
            "<id>",
            r"\\g<bid_id>",
        )

        replacement = replacement.replace(
            "<bid_id>",
            r"\\g<bid_id>",
        )

        replacement = replacement.replace(
            "<bidID>",
            r"\\g<bid_id>",
        )

        return replacement

    # --------------------------------------------------
    # HELPERS
    # --------------------------------------------------

    @staticmethod
    def _get_old_pattern(
        repair: RepairSuggestion,
    ) -> str:

        return getattr(
            repair,
            "old_pattern",
            "",
        ) or ""

    @staticmethod
    def _get_new_pattern(
        repair: RepairSuggestion,
    ) -> str:

        return getattr(
            repair,
            "new_pattern",
            "",
        ) or ""