from __future__ import annotations

import re
from dataclasses import dataclass

from .structural_detector import ElementSnapshot


@dataclass
class ElementMatch:
    """
    Represents a match between an element from the previous
    snapshot and an element from the current snapshot.
    """

    previous: ElementSnapshot
    current: ElementSnapshot
    score: float
    evidence: list[str]


class ElementMatcher:
    """
    Match elements between two HTML snapshots.

    The matcher uses deterministic evidence such as:

    - HTML tag
    - element ID
    - name attribute
    - visible text
    - matching attributes
    - meaningful identifiers
    """

    # ==================================================
    # TAG CATEGORIES
    # ==================================================

    IMPORTANT_TAGS = {
        "a": 0.35,
        "table": 0.40,
        "thead": 0.35,
        "tbody": 0.35,
        "tr": 0.35,
        "th": 0.35,
        "td": 0.35,
        "form": 0.35,
        "input": 0.35,
        "button": 0.35,
    }

    GENERIC_TAGS = {
        "html",
        "head",
        "meta",
        "script",
        "style",
        "link",
        "svg",
    }

    # ==================================================
    # INITIALIZATION
    # ==================================================

    def __init__(
        self,
        minimum_score: float = 0.50,
    ):
        self.minimum_score = minimum_score

    # ==================================================
    # PUBLIC API
    # ==================================================

    def match(
        self,
        previous_elements: list[ElementSnapshot],
        current_elements: list[ElementSnapshot],
    ) -> list[ElementMatch]:

        matches: list[ElementMatch] = []

        # Keep track of current elements that have
        # already been assigned to a previous element.
        used_current: set[int] = set()

        for previous in previous_elements:

            best_index = None
            best_score = 0.0
            best_evidence: list[str] = []

            for index, current in enumerate(
                current_elements
            ):

                # Do not match the same current element
                # to multiple previous elements.
                if index in used_current:
                    continue

                score, evidence = self._score(
                    previous,
                    current,
                )

                if score > best_score:

                    best_score = score
                    best_index = index
                    best_evidence = evidence

            # Only accept the best candidate if it
            # reaches the configured confidence threshold.
            if (
                best_index is not None
                and best_score >= self.minimum_score
            ):

                current = current_elements[
                    best_index
                ]

                matches.append(
                    ElementMatch(
                        previous=previous,
                        current=current,
                        score=best_score,
                        evidence=best_evidence,
                    )
                )

                used_current.add(
                    best_index
                )

        return matches

    # ==================================================
    # SCORING
    # ==================================================

    @staticmethod
    def _score(
        previous: ElementSnapshot,
        current: ElementSnapshot,
    ) -> tuple[float, list[str]]:

        # ------------------------------------------------
        # Different tags cannot represent the same
        # element.
        # ------------------------------------------------

        if previous.tag != current.tag:
            return 0.0, []

        tag = previous.tag.lower()

        # ------------------------------------------------
        # Base score based on tag importance.
        # ------------------------------------------------

        if tag in ElementMatcher.GENERIC_TAGS:

            score = 0.10

        elif tag in ElementMatcher.IMPORTANT_TAGS:

            score = ElementMatcher.IMPORTANT_TAGS[
                tag
            ]

        else:

            score = 0.20

        evidence = [
            "Same HTML tag"
        ]

        # ------------------------------------------------
        # ID
        # ------------------------------------------------

        previous_id = previous.attributes.get(
            "id"
        )

        current_id = current.attributes.get(
            "id"
        )

        if (
            previous_id
            and current_id
            and previous_id == current_id
        ):

            score += 0.30

            evidence.append(
                "Same element ID"
            )

        # ------------------------------------------------
        # NAME
        # ------------------------------------------------

        previous_name = previous.attributes.get(
            "name"
        )

        current_name = current.attributes.get(
            "name"
        )

        if (
            previous_name
            and current_name
            and previous_name == current_name
        ):

            score += 0.20

            evidence.append(
                "Same name attribute"
            )

        # ------------------------------------------------
        # TEXT
        # ------------------------------------------------

        previous_text = (
            previous.text
            .strip()
            .lower()
        )

        current_text = (
            current.text
            .strip()
            .lower()
        )

        if (
            previous_text
            and current_text
            and previous_text == current_text
        ):

            score += 0.20

            evidence.append(
                "Same text content"
            )

        # ------------------------------------------------
        # ATTRIBUTE SIMILARITY
        # ------------------------------------------------

        previous_attributes = set(
            previous.attributes
        )

        current_attributes = set(
            current.attributes
        )

        common_attributes = (
            previous_attributes
            & current_attributes
        )

        if common_attributes:

            matching_attributes = sum(
                1
                for attribute in common_attributes
                if (
                    previous.attributes[
                        attribute
                    ]
                    == current.attributes[
                        attribute
                    ]
                )
            )

            similarity = (
                matching_attributes
                / len(common_attributes)
            )

            if similarity > 0:

                score += (
                    0.20 * similarity
                )

                evidence.append(
                    "Matching attributes"
                )

        # ------------------------------------------------
        # MEANINGFUL IDENTIFIER SIMILARITY
        # ------------------------------------------------

        previous_identifiers = (
            ElementMatcher._extract_identifiers(
                previous.attributes
            )
        )

        current_identifiers = (
            ElementMatcher._extract_identifiers(
                current.attributes
            )
        )

        shared_identifiers = (
            previous_identifiers
            & current_identifiers
        )

        if shared_identifiers:

            score += 0.30

            evidence.append(
                "Shared identifier: "
                + ", ".join(
                    sorted(
                        shared_identifiers
                    )
                )
            )

        # ------------------------------------------------
        # LIMIT SCORE TO 1.0
        # ------------------------------------------------

        score = min(
            score,
            1.0,
        )

        return (
            score,
            evidence,
        )

    # ==================================================
    # IDENTIFIER EXTRACTION
    # ==================================================

    @staticmethod
    def _extract_identifiers(
        attributes: dict[str, str],
    ) -> set[str]:

        """
        Extract meaningful entity identifiers from
        selected HTML attributes.

        Examples:

            bids.aspx?bidID=287
                -> 287

            /procurement/bid/287
                -> 287

            data-bid-id="287"
                -> 287

            data-item-id="123"
                -> 123

        We intentionally do NOT extract arbitrary numbers
        from things such as:

            /739942322.js

        because those numbers are usually asset/build IDs,
        not business entity identifiers.
        """

        identifiers: set[str] = set()

        important_attributes = {
            "id",
            "name",
            "href",
            "data-id",
            "data-bid-id",
            "data-item-id",
            "data-record-id",
        }

        for attribute, value in attributes.items():

            if attribute not in important_attributes:
                continue

            if not value:
                continue

            value = str(value)

            # --------------------------------------------
            # bidID=287
            # bid-id=287
            # bid_id=287
            # --------------------------------------------

            matches = re.findall(
                r"(?:bidID|bid-id|bid_id)"
                r"[=/\-_]?"
                r"(\d+)",
                value,
                re.IGNORECASE,
            )

            identifiers.update(
                matches
            )

            # --------------------------------------------
            # /bid/287
            # /item/287
            # /record/287
            # --------------------------------------------

            matches = re.findall(
                r"(?:bid|item|record)"
                r"[=/\-_]"
                r"(\d+)",
                value,
                re.IGNORECASE,
            )

            identifiers.update(
                matches
            )

            # --------------------------------------------
            # data-bid-id="287"
            # data-item-id="287"
            # data-record-id="287"
            #
            # For id/name attributes, also allow:
            #
            # bid287
            # item287
            # record287
            # --------------------------------------------

            if attribute in {
                "id",
                "name",
                "data-id",
                "data-bid-id",
                "data-item-id",
                "data-record-id",
            }:

                matches = re.findall(
                    r"(?:bid|item|record)"
                    r"[-_]?(\d+)",
                    value,
                    re.IGNORECASE,
                )

                identifiers.update(
                    matches
                )

        return identifiers