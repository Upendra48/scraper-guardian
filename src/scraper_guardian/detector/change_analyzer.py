from __future__ import annotations

from dataclasses import dataclass, field

from .structural_detector import ElementSnapshot
from .element_matcher import ElementMatch


@dataclass
class ElementChange:
    """
    Represents a change detected between two matched HTML elements.
    """

    change_type: str
    tag: str
    path: str

    old_value: object | None = None
    new_value: object | None = None

    attribute: str | None = None

    severity: str = "LOW"
    impact: str = ""

    evidence: list[str] = field(default_factory=list)


class ChangeAnalyzer:
    """
    Analyze matched HTML elements and identify meaningful changes.

    The ElementMatcher answers:

        "Are these two elements probably the same element?"

    The ChangeAnalyzer answers:

        "If they are the same element, what changed?"
    """

    # Attributes that are especially important for web scrapers.
    IMPORTANT_ATTRIBUTES = {
        "href",
        "src",
        "id",
        "name",
        "class",
        "action",
        "value",
        "type",
    }

    # --------------------------------------------------
    # PUBLIC API
    # --------------------------------------------------

    def analyze(
        self,
        matches: list[ElementMatch],
    ) -> list[ElementChange]:

        changes: list[ElementChange] = []

        for match in matches:

            previous = match.previous
            current = match.current

            # ------------------------------------------
            # Attribute changes
            # ------------------------------------------

            changes.extend(
                self._analyze_attributes(
                    previous,
                    current,
                )
            )

            # ------------------------------------------
            # Text changes
            # ------------------------------------------

            text_change = self._analyze_text(
                previous,
                current,
            )

            if text_change is not None:
                changes.append(text_change)

        return changes

    # --------------------------------------------------
    # ATTRIBUTE ANALYSIS
    # --------------------------------------------------

    def _analyze_attributes(
        self,
        previous: ElementSnapshot,
        current: ElementSnapshot,
    ) -> list[ElementChange]:

        changes: list[ElementChange] = []

        old_attributes = previous.attributes
        new_attributes = current.attributes

        all_attributes = (
            set(old_attributes)
            | set(new_attributes)
        )

        for attribute in sorted(all_attributes):

            old_value = old_attributes.get(attribute)
            new_value = new_attributes.get(attribute)

            # No change.
            if old_value == new_value:
                continue

            severity, impact = self._classify_attribute_change(
                attribute=attribute,
                previous=previous,
                current=current,
                old_value=old_value,
                new_value=new_value,
            )

            change_type = self._get_attribute_change_type(
                attribute=attribute,
                old_value=old_value,
                new_value=new_value,
            )

            changes.append(
                ElementChange(
                    change_type=change_type,
                    tag=current.tag,
                    path=current.path,
                    old_value=old_value,
                    new_value=new_value,
                    attribute=attribute,
                    severity=severity,
                    impact=impact,
                    evidence=[
                        "Element matched by ElementMatcher",
                        f"Attribute '{attribute}' changed",
                    ],
                )
            )

        return changes

    # --------------------------------------------------
    # TEXT ANALYSIS
    # --------------------------------------------------

    def _analyze_text(
        self,
        previous: ElementSnapshot,
        current: ElementSnapshot,
    ) -> ElementChange | None:

        old_text = self._normalize_text(
            previous.text
        )

        new_text = self._normalize_text(
            current.text
        )

        if old_text == new_text:
            return None

        severity = "LOW"
        impact = "Visible element text changed."

        # Text changes on links/buttons can be more important
        # because scrapers often identify elements by visible text.
        if current.tag in {
            "a",
            "button",
            "input",
            "label",
        }:

            severity = "MEDIUM"

            impact = (
                "Visible text changed on an interactive "
                "element. Text-based scraper selectors "
                "may need updating."
            )

        return ElementChange(
            change_type="text_changed",
            tag=current.tag,
            path=current.path,
            old_value=previous.text,
            new_value=current.text,
            severity=severity,
            impact=impact,
            evidence=[
                "Element matched by ElementMatcher",
                "Text content changed",
            ],
        )

    # --------------------------------------------------
    # ATTRIBUTE CHANGE CLASSIFICATION
    # --------------------------------------------------

    def _classify_attribute_change(
        self,
        attribute: str,
        previous: ElementSnapshot,
        current: ElementSnapshot,
        old_value: object,
        new_value: object,
    ) -> tuple[str, str]:

        # ------------------------------------------
        # HREF
        # ------------------------------------------

        if attribute == "href":

            if current.tag == "a":

                return (
                    "HIGH",
                    (
                        "Link destination changed. "
                        "A scraper using this URL or URL "
                        "pattern may need to be updated."
                    ),
                )

            return (
                "MEDIUM",
                "href attribute changed.",
            )

        # ------------------------------------------
        # SRC
        # ------------------------------------------

        if attribute == "src":

            return (
                "HIGH",
                (
                    "Resource URL changed. "
                    "A scraper downloading or parsing "
                    "this resource may be affected."
                ),
            )

        # ------------------------------------------
        # ID
        # ------------------------------------------

        if attribute == "id":

            return (
                "HIGH",
                (
                    "Element ID changed. "
                    "ID-based CSS/XPath selectors may "
                    "no longer work."
                ),
            )

        # ------------------------------------------
        # NAME
        # ------------------------------------------

        if attribute == "name":

            return (
                "HIGH",
                (
                    "Element name changed. "
                    "Name-based selectors may need "
                    "to be updated."
                ),
            )

        # ------------------------------------------
        # CLASS
        # ------------------------------------------

        if attribute == "class":

            return (
                "MEDIUM",
                (
                    "CSS class changed. "
                    "Class-based selectors may be affected."
                ),
            )

        # ------------------------------------------
        # FORM ACTION
        # ------------------------------------------

        if attribute == "action":

            return (
                "HIGH",
                (
                    "Form submission URL changed. "
                    "Form-based scraping logic may be affected."
                ),
            )

        # ------------------------------------------
        # TYPE
        # ------------------------------------------

        if attribute == "type":

            return (
                "MEDIUM",
                (
                    "Element type changed and may affect "
                    "interaction or extraction logic."
                ),
            )

        # ------------------------------------------
        # VALUE
        # ------------------------------------------

        if attribute == "value":

            return (
                "LOW",
                "Element value changed.",
            )

        # ------------------------------------------
        # DATA ATTRIBUTES
        # ------------------------------------------

        if attribute.startswith("data-"):

            return (
                "MEDIUM",
                (
                    f"Data attribute '{attribute}' changed. "
                    "Scraper logic using this attribute "
                    "may be affected."
                ),
            )

        # ------------------------------------------
        # OTHER
        # ------------------------------------------

        return (
            "LOW",
            f"Attribute '{attribute}' changed.",
        )

    # --------------------------------------------------
    # ATTRIBUTE CHANGE TYPE
    # --------------------------------------------------

    @staticmethod
    def _get_attribute_change_type(
        attribute: str,
        old_value: object | None,
        new_value: object | None,
    ) -> str:

        if (
            old_value is None
            and new_value is not None
        ):

            return "attribute_added"

        if (
            old_value is not None
            and new_value is None
        ):

            return "attribute_removed"

        return "attribute_changed"

    # --------------------------------------------------
    # TEXT NORMALIZATION
    # --------------------------------------------------

    @staticmethod
    def _normalize_text(
        text: str | None,
    ) -> str:

        if not text:
            return ""

        return " ".join(
            text.split()
        )