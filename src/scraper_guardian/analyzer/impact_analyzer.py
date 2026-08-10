from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class ImpactLevel(str, Enum):
    IGNORE = "IGNORE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class ImpactResult:
    level: ImpactLevel
    reason: str
    recommendation: str


class ImpactAnalyzer:
    """
    Analyze detected HTML changes and determine
    their potential impact on a web scraper.
    """

    # --------------------------------------------------
    # PUBLIC API
    # --------------------------------------------------

    def analyze(
        self,
        change: Any,
    ) -> ImpactResult:

        change_type = getattr(
            change,
            "change_type",
            "",
        )

        tag = (
            getattr(change, "tag", "")
            or ""
        ).lower()

        attribute = (
            getattr(change, "attribute", "")
            or ""
        ).lower()

        old_value = getattr(
            change,
            "old_value",
            "",
        )

        new_value = getattr(
            change,
            "new_value",
            "",
        )

        path = (
            getattr(change, "path", "")
            or ""
        ).lower()

        text = (
            getattr(change, "text", "")
            or ""
        ).lower()

        # --------------------------------------------------
        # Ignore obvious non-scraper changes
        # --------------------------------------------------

        if tag in {
            "script",
            "style",
            "meta",
            "link",
        }:

            return ImpactResult(
                level=ImpactLevel.LOW,
                reason=(
                    f"Change occurred in <{tag}> "
                    "which is usually unrelated to "
                    "bid-data extraction."
                ),
                recommendation=(
                    "Monitor the change but no immediate "
                    "scraper update is normally required."
                ),
            )

        # --------------------------------------------------
        # HREF changes
        # --------------------------------------------------

        if (
            tag == "a"
            and attribute == "href"
        ):

            return ImpactResult(
                level=ImpactLevel.HIGH,
                reason=(
                    "A link destination changed. "
                    "Scrapers commonly depend on href "
                    "values to locate bid-detail pages "
                    "or documents."
                ),
                recommendation=(
                    "Review the scraper's URL construction "
                    "or link extraction logic."
                ),
            )

        # --------------------------------------------------
        # FORM action changes
        # --------------------------------------------------

        if (
            tag == "form"
            and attribute == "action"
        ):

            return ImpactResult(
                level=ImpactLevel.HIGH,
                reason=(
                    "Form submission behavior changed. "
                    "This can affect search, filtering, "
                    "pagination, or bid retrieval."
                ),
                recommendation=(
                    "Review form submission and request "
                    "handling in the scraper."
                ),
            )

        # --------------------------------------------------
        # ID changes
        # --------------------------------------------------

        if attribute == "id":

            return ImpactResult(
                level=ImpactLevel.HIGH,
                reason=(
                    "An element ID changed. "
                    "Scrapers frequently use IDs in "
                    "CSS selectors and XPath expressions."
                ),
                recommendation=(
                    "Search the scraper for the old ID "
                    "and update the selector if required."
                ),
            )

        # --------------------------------------------------
        # NAME changes
        # --------------------------------------------------

        if attribute == "name":

            return ImpactResult(
                level=ImpactLevel.MEDIUM,
                reason=(
                    "An element name attribute changed. "
                    "This may affect form fields or "
                    "data extraction."
                ),
                recommendation=(
                    "Check selectors and form-field "
                    "extraction logic."
                ),
            )

        # --------------------------------------------------
        # CLASS changes
        # --------------------------------------------------

        if attribute == "class":

            return ImpactResult(
                level=ImpactLevel.MEDIUM,
                reason=(
                    "A CSS class changed. "
                    "The scraper may depend on this "
                    "class for locating elements."
                ),
                recommendation=(
                    "Check CSS selectors and XPath "
                    "expressions using the old class."
                ),
            )

        # --------------------------------------------------
        # Bid-related path
        # --------------------------------------------------

        bid_keywords = {
            "bid",
            "bids",
            "procurement",
            "solicitation",
            "rfp",
            "rfq",
            "ifb",
            "proposal",
            "contract",
        }

        if any(
            keyword in path
            for keyword in bid_keywords
        ):

            return ImpactResult(
                level=ImpactLevel.HIGH,
                reason=(
                    "The changed element appears to be "
                    "located inside a bid or procurement "
                    "section."
                ),
                recommendation=(
                    "Review the scraper's bid extraction "
                    "selectors and parsing logic."
                ),
            )

        # --------------------------------------------------
        # Bid-related text
        # --------------------------------------------------

        if any(
            keyword in text
            for keyword in bid_keywords
        ):

            return ImpactResult(
                level=ImpactLevel.HIGH,
                reason=(
                    "The changed element appears to "
                    "contain bid or procurement data."
                ),
                recommendation=(
                    "Review the corresponding bid "
                    "extraction logic."
                ),
            )

        # --------------------------------------------------
        # Element added / removed
        # --------------------------------------------------

        if change_type == "element_removed":

            return ImpactResult(
                level=ImpactLevel.HIGH,
                reason=(
                    "An HTML element was removed. "
                    "Any scraper selector targeting "
                    "that element may now fail."
                ),
                recommendation=(
                    "Check whether the removed element "
                    "was used for bid extraction."
                ),
            )

        if change_type == "element_added":

            return ImpactResult(
                level=ImpactLevel.LOW,
                reason=(
                    "A new HTML element was added."
                ),
                recommendation=(
                    "Monitor the new element to determine "
                    "whether it affects the bid structure."
                ),
            )

        # --------------------------------------------------
        # Table changes
        # --------------------------------------------------

        if tag in {
            "table",
            "thead",
            "tbody",
            "tr",
            "th",
            "td",
        }:

            return ImpactResult(
                level=ImpactLevel.HIGH,
                reason=(
                    "A table-related element changed. "
                    "Bid listings are commonly represented "
                    "using tables."
                ),
                recommendation=(
                    "Review table selectors and column "
                    "extraction logic."
                ),
            )

        # --------------------------------------------------
        # Default
        # --------------------------------------------------

        return ImpactResult(
            level=ImpactLevel.LOW,
            reason=(
                "An HTML change was detected but its "
                "direct scraper impact is uncertain."
            ),
            recommendation=(
                "Review the change if scraper behavior "
                "changes."
            ),
        )