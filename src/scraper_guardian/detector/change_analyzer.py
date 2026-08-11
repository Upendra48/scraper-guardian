
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

    # ==================================================
    # PUBLIC API
    # ==================================================

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

    # ==================================================
    # RECOMMENDATIONS
    # ==================================================

    def generate_recommendations(
        self,
        changes: list[ElementChange],
    ) -> list[dict[str, str]]:
        """
        Generate actionable recommendations from detected changes.

        Recommendations are derived from the detected changes and are
        independent of any specific website.
        """

        recommendations: list[dict[str, str]] = []

        # ------------------------------------------
        # HREF / URL changes
        # ------------------------------------------

        href_changes = [
            change
            for change in changes
            if (
                change.attribute == "href"
                and change.change_type
                in {
                    "attribute_changed",
                    "attribute_added",
                    "attribute_removed",
                }
            )
        ]

        if href_changes:

            old_patterns: set[str] = set()
            new_patterns: set[str] = set()

            for change in href_changes:

                old_value = str(
                    change.old_value or ""
                )

                new_value = str(
                    change.new_value or ""
                )

                old_pattern = (
                    self._normalize_url_pattern(
                        old_value
                    )
                )

                new_pattern = (
                    self._normalize_url_pattern(
                        new_value
                    )
                )

                if old_pattern:
                    old_patterns.add(
                        old_pattern
                    )

                if new_pattern:
                    new_patterns.add(
                        new_pattern
                    )

            # --------------------------------------
            # URL pattern changed
            # --------------------------------------

            if (
                old_patterns
                and new_patterns
                and old_patterns != new_patterns
            ):

                old_pattern_text = ", ".join(
                    sorted(old_patterns)
                )

                new_pattern_text = ", ".join(
                    sorted(new_patterns)
                )

                recommendations.append(
                    {
                        "type": "url_pattern_changed",
                        "severity": "HIGH",
                        "message": (
                            "The URL structure appears to have changed "
                            "from:\n\n"
                            f"{old_pattern_text}\n\n"
                            "to:\n\n"
                            f"{new_pattern_text}\n\n"
                            "A scraper using the old URL pattern should "
                            "be reviewed."
                        ),
                    }
                )

            # --------------------------------------
            # HREF changed but no clear pattern
            # --------------------------------------

            else:

                recommendations.append(
                    {
                        "type": "href_changed",
                        "severity": "HIGH",
                        "message": (
                            "One or more link destinations changed. "
                            "Review the scraper's URL extraction logic."
                        ),
                    }
                )

        # ==================================================
        # CLASS CHANGES
        # ==================================================

        class_changes = [
            change
            for change in changes
            if (
                change.attribute == "class"
                and change.change_type
                in {
                    "attribute_changed",
                    "attribute_added",
                    "attribute_removed",
                }
            )
        ]

        if class_changes:

            recommendations.append(
                {
                    "type": "selector_class_changed",
                    "severity": "MEDIUM",
                    "message": (
                        "CSS class attributes changed. "
                        "Review scrapers using class-based "
                        "CSS or XPath selectors."
                    ),
                }
            )

        # ==================================================
        # ID CHANGES
        # ==================================================

        id_changes = [
            change
            for change in changes
            if (
                change.attribute == "id"
                and change.change_type
                in {
                    "attribute_changed",
                    "attribute_added",
                    "attribute_removed",
                }
            )
        ]

        if id_changes:

            recommendations.append(
                {
                    "type": "selector_id_changed",
                    "severity": "HIGH",
                    "message": (
                        "Element IDs changed. "
                        "Review scrapers using ID-based "
                        "CSS or XPath selectors."
                    ),
                }
            )

        # ==================================================
        # NAME CHANGES
        # ==================================================

        name_changes = [
            change
            for change in changes
            if (
                change.attribute == "name"
                and change.change_type
                in {
                    "attribute_changed",
                    "attribute_added",
                    "attribute_removed",
                }
            )
        ]

        if name_changes:

            recommendations.append(
                {
                    "type": "selector_name_changed",
                    "severity": "HIGH",
                    "message": (
                        "Element name attributes changed. "
                        "Review scrapers using name-based "
                        "selectors or form fields."
                    ),
                }
            )

        # ==================================================
        # SRC CHANGES
        # ==================================================

        src_changes = [
            change
            for change in changes
            if (
                change.attribute == "src"
                and change.change_type
                in {
                    "attribute_changed",
                    "attribute_added",
                    "attribute_removed",
                }
            )
        ]

        if src_changes:

            recommendations.append(
                {
                    "type": "resource_url_changed",
                    "severity": "HIGH",
                    "message": (
                        "One or more resource URLs changed. "
                        "Review scrapers that download or "
                        "parse linked resources."
                    ),
                }
            )

        # ==================================================
        # FORM ACTION CHANGES
        # ==================================================

        action_changes = [
            change
            for change in changes
            if (
                change.attribute == "action"
                and change.change_type
                in {
                    "attribute_changed",
                    "attribute_added",
                    "attribute_removed",
                }
            )
        ]

        if action_changes:

            recommendations.append(
                {
                    "type": "form_action_changed",
                    "severity": "HIGH",
                    "message": (
                        "A form submission URL changed. "
                        "Review form-based scraping or "
                        "request logic."
                    ),
                }
            )

        # ==================================================
        # TYPE CHANGES
        # ==================================================

        type_changes = [
            change
            for change in changes
            if (
                change.attribute == "type"
                and change.change_type
                in {
                    "attribute_changed",
                    "attribute_added",
                    "attribute_removed",
                }
            )
        ]

        if type_changes:

            recommendations.append(
                {
                    "type": "element_type_changed",
                    "severity": "MEDIUM",
                    "message": (
                        "An element's type attribute changed. "
                        "Review interaction or extraction logic."
                    ),
                }
            )

        # ==================================================
        # TEXT CHANGES
        # ==================================================

        text_changes = [
            change
            for change in changes
            if change.change_type == "text_changed"
        ]

        if text_changes:

            recommendations.append(
                {
                    "type": "text_changed",
                    "severity": "MEDIUM",
                    "message": (
                        "Visible element text changed. "
                        "Review scrapers that identify elements "
                        "using exact text or text-based selectors."
                    ),
                }
            )

        # ==================================================
        # ELEMENT REMOVALS
        # ==================================================

        removed_elements = [
            change
            for change in changes
            if change.change_type == "element_removed"
        ]

        if removed_elements:

            recommendations.append(
                {
                    "type": "element_removed",
                    "severity": "HIGH",
                    "message": (
                        "Elements used by the previous page "
                        "structure were removed. Review selectors "
                        "and extraction logic."
                    ),
                }
            )

        # ==================================================
        # ELEMENT ADDITIONS
        # ==================================================

        added_elements = [
            change
            for change in changes
            if change.change_type == "element_added"
        ]

        if added_elements:

            recommendations.append(
                {
                    "type": "element_added",
                    "severity": "LOW",
                    "message": (
                        "New elements were added to the page. "
                        "Check whether they contain new data or "
                        "affect the scraper's element hierarchy."
                    ),
                }
            )

        return recommendations

    # ==================================================
    # URL PATTERN NORMALIZATION
    # ==================================================

    @staticmethod
    def _normalize_url_pattern(
        url: str,
    ) -> str:
        """
        Convert a concrete URL into a reusable URL pattern.

        Examples:

            bids.aspx?bidID=287
                ->
            bids.aspx?bidID=<id>

            /procurement/bid/287
                ->
            /procurement/bid/<id>
        """

        if not url:
            return ""

        value = url.strip()

        # ------------------------------------------
        # bidID query parameter
        # ------------------------------------------

        value = __import__("re").sub(
            r"([?&]bidID=)\d+",
            r"\1<id>",
            value,
            flags=__import__("re").IGNORECASE,
        )

        # ------------------------------------------
        # Generic numeric path component
        # ------------------------------------------

        value = __import__("re").sub(
            r"/\d+(?=/?$)",
            "/<id>",
            value,
        )

        return value

    # ==================================================
    # ATTRIBUTE ANALYSIS
    # ==================================================

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

            old_value = old_attributes.get(
                attribute
            )

            new_value = new_attributes.get(
                attribute
            )

            # No change.
            if old_value == new_value:
                continue

            severity, impact = (
                self._classify_attribute_change(
                    attribute=attribute,
                    previous=previous,
                    current=current,
                    old_value=old_value,
                    new_value=new_value,
                )
            )

            change_type = (
                self._get_attribute_change_type(
                    attribute=attribute,
                    old_value=old_value,
                    new_value=new_value,
                )
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

    # ==================================================
    # TEXT ANALYSIS
    # ==================================================

    def _analyze_text(
        self,
        previous: ElementSnapshot,
        current: ElementSnapshot,
    ) -> ElementChange | None:
        
        if current.tag in {"html", "body"}:
            return None

        old_text = self._normalize_text(
            previous.text
        )

        new_text = self._normalize_text(
            current.text
        )

        if old_text == new_text:
            return None
        
        if len(old_text) >300 or len(new_text) >300:
            return None

        severity = "LOW"

        impact = (
            "Visible element text changed."
        )

        # Text changes on interactive elements
        # can affect text-based selectors.
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

    # ==================================================
    # ATTRIBUTE CHANGE CLASSIFICATION
    # ==================================================

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

    # ==================================================
    # ATTRIBUTE CHANGE TYPE
    # ==================================================

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

    # ==================================================
    # TEXT NORMALIZATION
    # ==================================================

    @staticmethod
    def _normalize_text(
        text: str | None,
    ) -> str:

        if not text:
            return ""

        return " ".join(
            text.split()
        )

