
from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import urlparse

from ..detector.structural_detector import ElementSnapshot
from .repair_engine import RepairSuggestion


@dataclass
class ValidationResult:
    """
    Result of validating a proposed scraper repair.
    """

    valid: bool
    repair_type: str
    confidence: float
    message: str
    evidence: list[str]


class RepairValidator:
    """
    Validate RepairEngine suggestions against the current HTML.

    The validator does NOT modify scraper code.

    It only answers:

        "Does this proposed repair appear to be valid
         against the current page?"
    """

    # --------------------------------------------------
    # PUBLIC API
    # --------------------------------------------------

    def validate(
        self,
        repair: RepairSuggestion,
        current_elements: list[ElementSnapshot],
    ) -> ValidationResult:

        if repair.repair_type == "url_pattern_update":
            return self._validate_url_pattern(
                repair,
                current_elements,
            )

        if repair.repair_type == "href_update":
            return self._validate_href_update(
                repair,
                current_elements,
            )

        return ValidationResult(
            valid=False,
            repair_type=repair.repair_type,
            confidence=0.0,
            message=(
                f"Unsupported repair type: "
                f"{repair.repair_type}"
            ),
            evidence=[],
        )

    # --------------------------------------------------
    # URL PATTERN VALIDATION
    # --------------------------------------------------

    def _validate_url_pattern(
        self,
        repair: RepairSuggestion,
        current_elements: list[ElementSnapshot],
    ) -> ValidationResult:

        old_pattern = repair.old_pattern
        new_pattern = repair.new_pattern

        evidence: list[str] = []

        # ----------------------------------------------
        # Validate pattern format
        # ----------------------------------------------

        old_regex = self._pattern_to_regex(
            old_pattern
        )

        new_regex = self._pattern_to_regex(
            new_pattern
        )

        if old_regex is None or new_regex is None:

            return ValidationResult(
                valid=False,
                repair_type=repair.repair_type,
                confidence=0.0,
                message=(
                    "Unable to interpret URL patterns."
                ),
                evidence=[
                    "Invalid URL pattern format",
                ],
            )

        # ----------------------------------------------
        # Collect href values
        # ----------------------------------------------

        hrefs: list[str] = []

        for element in current_elements:

            if element.tag != "a":
                continue

            href = element.attributes.get("href")

            if not href:
                continue

            hrefs.append(
                href.strip()
            )

        # ----------------------------------------------
        # Find old/new pattern matches
        # ----------------------------------------------

        old_matches = [
            href
            for href in hrefs
            if re.fullmatch(
                old_regex,
                href,
                re.IGNORECASE,
            )
        ]

        new_matches = [
            href
            for href in hrefs
            if re.fullmatch(
                new_regex,
                href,
                re.IGNORECASE,
            )
        ]

        # ----------------------------------------------
        # New pattern must exist
        # ----------------------------------------------

        if not new_matches:

            return ValidationResult(
                valid=False,
                repair_type=repair.repair_type,
                confidence=0.0,
                message=(
                    "The proposed new URL pattern "
                    "was not found in the current HTML."
                ),
                evidence=[
                    "No current href matched the new pattern",
                    (
                        f"Expected pattern: "
                        f"{new_pattern}"
                    ),
                    (
                        f"Checked {len(hrefs)} "
                        f"current href(s)"
                    ),
                ],
            )

        evidence.append(
            f"Found {len(new_matches)} current href(s) "
            "matching the new URL pattern"
        )

        # ----------------------------------------------
        # Old pattern should normally be absent
        # ----------------------------------------------

        if not old_matches:

            evidence.append(
                "Old URL pattern is no longer present "
                "in the current HTML"
            )

        else:

            evidence.append(
                f"Old URL pattern still appears in "
                f"{len(old_matches)} current href(s)"
            )

        # ----------------------------------------------
        # Validate identifiers
        # ----------------------------------------------

        new_identifiers: set[str] = set()

        for href in new_matches:

            identifiers = self._extract_numeric_ids(
                href
            )

            new_identifiers.update(
                identifiers
            )

        if not new_identifiers:

            return ValidationResult(
                valid=False,
                repair_type=repair.repair_type,
                confidence=0.30,
                message=(
                    "The new URL pattern exists, but "
                    "no numeric bid identifiers could "
                    "be extracted."
                ),
                evidence=evidence,
            )

        evidence.append(
            "Extracted identifiers: "
            + ", ".join(
                sorted(
                    new_identifiers,
                    key=lambda value: int(value),
                )
            )
        )

        # ----------------------------------------------
        # Validate that the pattern is actually
        # representing bid URLs.
        # ----------------------------------------------

        if "/procurement/bid/" in new_pattern.lower():

            evidence.append(
                "New pattern contains the expected "
                "procurement bid URL structure"
            )

        # ----------------------------------------------
        # Calculate confidence
        # ----------------------------------------------

        confidence = 0.90

        if old_matches:
            confidence -= 0.10

        if len(new_matches) >= 3:
            confidence += 0.08

        elif len(new_matches) >= 2:
            confidence += 0.05

        elif len(new_matches) >= 1:
            confidence += 0.02

        confidence = min(
            confidence,
            0.99,
        )

        return ValidationResult(
            valid=True,
            repair_type=repair.repair_type,
            confidence=confidence,
            message=(
                "The proposed URL pattern is valid "
                "against the current HTML."
            ),
            evidence=evidence,
        )

    # --------------------------------------------------
    # HREF VALIDATION
    # --------------------------------------------------

    def _validate_href_update(
        self,
        repair: RepairSuggestion,
        current_elements: list[ElementSnapshot],
    ) -> ValidationResult:

        new_pattern = repair.new_pattern

        if not new_pattern:

            return ValidationResult(
                valid=False,
                repair_type=repair.repair_type,
                confidence=0.0,
                message=(
                    "The proposed href pattern is empty."
                ),
                evidence=[],
            )

        # Convert the proposed href to a regex so
        # <id> works as a placeholder here too.
        new_regex = self._pattern_to_regex(
            new_pattern
        )

        if new_regex is None:

            return ValidationResult(
                valid=False,
                repair_type=repair.repair_type,
                confidence=0.0,
                message=(
                    "Unable to interpret the proposed "
                    "href pattern."
                ),
                evidence=[
                    "Invalid href pattern format",
                ],
            )

        matching_elements: list[
            ElementSnapshot
        ] = []

        matching_hrefs: list[str] = []

        for element in current_elements:

            href = element.attributes.get(
                "href"
            )

            if not href:
                continue

            href = href.strip()

            if re.fullmatch(
                new_regex,
                href,
                re.IGNORECASE,
            ):

                matching_elements.append(
                    element
                )

                matching_hrefs.append(
                    href
                )

        # ----------------------------------------------
        # No matches
        # ----------------------------------------------

        if not matching_elements:

            return ValidationResult(
                valid=False,
                repair_type=repair.repair_type,
                confidence=0.0,
                message=(
                    "The proposed href update "
                    "could not be found in the "
                    "current HTML."
                ),
                evidence=[
                    (
                        "No current href matched "
                        "the proposed pattern"
                    ),
                    (
                        f"Expected pattern: "
                        f"{new_pattern}"
                    ),
                ],
            )

        # ----------------------------------------------
        # Extract identifiers
        # ----------------------------------------------

        identifiers: set[str] = set()

        for href in matching_hrefs:

            identifiers.update(
                self._extract_numeric_ids(
                    href
                )
            )

        evidence = [
            (
                f"Found {len(matching_elements)} "
                "matching href element(s)"
            )
        ]

        if identifiers:

            evidence.append(
                "Extracted identifiers: "
                + ", ".join(
                    sorted(
                        identifiers,
                        key=lambda value: int(value),
                    )
                )
            )

        return ValidationResult(
            valid=True,
            repair_type=repair.repair_type,
            confidence=0.95,
            message=(
                "The proposed href update exists "
                "in the current HTML."
            ),
            evidence=evidence,
        )

    # --------------------------------------------------
    # PATTERN CONVERSION
    # --------------------------------------------------


    @staticmethod
    def _pattern_to_regex(
    pattern: str | None,
) -> str | None:

        if not pattern:
            return None

        pattern = pattern.strip()

        if not pattern:
            return None

    # --------------------------------------------------
    # Convert placeholders BEFORE escaping the pattern.
    #
    # This is important because re.escape() behavior
    # can differ between Python versions for characters
    # such as < and >.
    # --------------------------------------------------

        placeholders: dict[str, str] = {
        "<id>": "__NUMERIC_ID__",
        "<bid_id>": "__NUMERIC_BID_ID__",
        "<bidID>": "__NUMERIC_BID_ID_CAMEL__",
    }

        normalized = pattern

        for placeholder, token in placeholders.items():
            normalized = normalized.replace(
            placeholder,
            token,
        )

    # --------------------------------------------------
    # Escape the literal parts of the URL.
    # --------------------------------------------------

        escaped = re.escape(
        normalized
    )

    # --------------------------------------------------
    # Replace our temporary tokens with regex patterns.
    # --------------------------------------------------

        escaped = escaped.replace(
        "__NUMERIC_ID__",
        r"\d+",
    )

        escaped = escaped.replace(
        "__NUMERIC_BID_ID__",
        r"\d+",
    )

        escaped = escaped.replace(
        "__NUMERIC_BID_ID_CAMEL__",
        r"\d+",
    )

    # --------------------------------------------------
    # Anchor the complete URL pattern.
    # --------------------------------------------------

        return (
        r"^"
        + escaped
        + r"$"
        )



    # --------------------------------------------------
    # IDENTIFIER EXTRACTION
    # --------------------------------------------------

    @staticmethod
    def _extract_numeric_ids(
        href: str,
    ) -> set[str]:

        identifiers: set[str] = set()

        if not href:
            return identifiers

        parsed = urlparse(
            href
        )

        # ----------------------------------------------
        # Query parameters
        # ----------------------------------------------

        query = parsed.query

        matches = re.findall(
            r"(?:bidID|bid_id|bid-id|id|item|record)"
            r"=(\d+)",
            query,
            re.IGNORECASE,
        )

        identifiers.update(
            matches
        )

        # ----------------------------------------------
        # Path identifiers
        # ----------------------------------------------

        path_matches = re.findall(
            r"/(?:bid|item|record)/(\d+)",
            parsed.path,
            re.IGNORECASE,
        )

        identifiers.update(
            path_matches
        )

        return identifiers

