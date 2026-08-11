from __future__ import annotations

from dataclasses import dataclass, field

from .structural_detector import ElementSnapshot
from .element_matcher import ElementMatch

IGNORED_STRUCTURAL_TAGS = {
    "script",
    "style",
    "meta",
    "link",
    "svg",
    "use",
    "path",
}

@dataclass
class ElementStructuralChange:
    """
    Represents an element that was added to or removed from
    the current HTML structure.
    """

    change_type: str
    tag: str
    path: str

    element: ElementSnapshot

    severity: str = "LOW"
    impact: str = ""

    evidence: list[str] = field(default_factory=list)


class ElementChangeDetector:
    """
    Detect elements that could not be matched between the
    previous and current HTML snapshots.

    ElementMatcher handles elements that exist in both
    snapshots.

    This class handles elements that exist only on one side.
    """

    def detect(
        self,
        previous_elements: dict[str, ElementSnapshot],
        current_elements: dict[str, ElementSnapshot],
        matches: list[ElementMatch],
    ) -> list[ElementStructuralChange]:

        changes: list[ElementStructuralChange] = []
        
        previous = list(previous_elements.values())
        current = list(current_elements.values())

        matched_previous = {
            id(match.previous)
            for match in matches
        }

        matched_current = {
            id(match.current)
            for match in matches
        }

        # --------------------------------------------------
        # Removed elements
        # --------------------------------------------------

        for element in previous:

            if id(element) in matched_previous:
                continue
            
            if element.tag in IGNORED_STRUCTURAL_TAGS:
                continue

            changes.append(
                self._create_removed_change(
                    element
                )
            )

        # --------------------------------------------------
        # Added elements
        # --------------------------------------------------
        
        

        for element in current:

            if id(element) in matched_current:
                continue
            
            if element.tag in IGNORED_STRUCTURAL_TAGS:
                continue

            changes.append(
                self._create_added_change(
                    element
                )
            )

        return changes

    # --------------------------------------------------
    # REMOVED ELEMENT
    # --------------------------------------------------

    @staticmethod
    def _create_removed_change(
        element: ElementSnapshot,
    ) -> ElementStructuralChange:

        severity = "LOW"
        impact = (
            "An element from the previous page structure "
            "is no longer present."
        )

        # Elements commonly used directly by scrapers
        # deserve higher priority.
        if element.tag in {
            "a",
            "form",
            "table",
            "tr",
            "td",
            "button",
            "input",
        }:
            severity = "HIGH"

            impact = (
                "A scraper-relevant element was removed "
                "from the page structure. Selectors or "
                "extraction logic may no longer work."
            )


        return ElementStructuralChange(
            change_type="element_removed",
            tag=element.tag,
            path=element.path,
            element=element,
            severity=severity,
            impact=impact,
            evidence=[
                "Element existed in the previous HTML",
                "Element has no corresponding current match",
            ],
        )

    # --------------------------------------------------
    # ADDED ELEMENT
    # --------------------------------------------------

    @staticmethod
    def _create_added_change(
        element: ElementSnapshot,
    ) -> ElementStructuralChange:

        severity = "LOW"
        impact = (
            "A new element was added to the current "
            "page structure."
        )

        if element.tag in {
            "a",
            "form",
            "table",
            "tr",
            "td",
            "button",
            "input",
        }:
            severity = "MEDIUM"

            impact = (
                "A scraper-relevant element was added "
                "to the page. Check whether it contains "
                "new data or changes the extraction structure."
            )

        return ElementStructuralChange(
            change_type="element_added",
            tag=element.tag,
            path=element.path,
            element=element,
            severity=severity,
            impact=impact,
            evidence=[
                "Element exists in the current HTML",
                "Element has no corresponding previous match",
            ],
        )