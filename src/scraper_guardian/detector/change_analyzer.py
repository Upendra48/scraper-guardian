from __future__ import annotations

from dataclasses import dataclass

from .element_matcher import ElementMatch


@dataclass
class AttributeChange:
    """
    Represents a change to a single HTML attribute.
    """

    attribute: str
    old_value: str | None
    new_value: str | None


@dataclass
class ElementChange:
    """
    Represents all detected changes for one matched element.
    """

    previous_path: str
    current_path: str
    tag: str

    text_changed: bool
    old_text: str
    new_text: str

    attribute_changes: list[AttributeChange]

    impact: str


class ChangeAnalyzer:
    """
    Analyze matched HTML elements and determine
    exactly what changed.
    """

    # ==================================================
    # PUBLIC API
    # ==================================================

    def analyze(
        self,
        matches: list[ElementMatch],
    ) -> list[ElementChange]:

        changes: list[ElementChange] = []

        for match in matches:

            change = self._analyze_match(
                match
            )

            # Only keep elements where something
            # actually changed.
            if (
                change.text_changed
                or change.attribute_changes
            ):

                changes.append(
                    change
                )

        return changes

    # ==================================================
    # SINGLE ELEMENT
    # ==================================================

    def _analyze_match(
        self,
        match: ElementMatch,
    ) -> ElementChange:

        previous = match.previous
        current = match.current

        # ------------------------------------------------
        # TEXT
        # ------------------------------------------------

        old_text = (
            previous.text
            .strip()
        )

        new_text = (
            current.text
            .strip()
        )

        text_changed = (
            old_text != new_text
        )

        # ------------------------------------------------
        # ATTRIBUTES
        # ------------------------------------------------

        attribute_changes = []

        all_attributes = (
            set(previous.attributes)
            | set(current.attributes)
        )

        for attribute in sorted(
            all_attributes
        ):

            old_value = previous.attributes.get(
                attribute
            )

            new_value = current.attributes.get(
                attribute
            )

            if old_value != new_value:

                attribute_changes.append(
                    AttributeChange(
                        attribute=attribute,
                        old_value=old_value,
                        new_value=new_value,
                    )
                )

        # ------------------------------------------------
        # IMPACT
        # ------------------------------------------------

        impact = self._determine_impact(
            previous,
            current,
            text_changed,
            attribute_changes,
        )

        return ElementChange(
            previous_path=previous.path,
            current_path=current.path,
            tag=current.tag,
            text_changed=text_changed,
            old_text=old_text,
            new_text=new_text,
            attribute_changes=attribute_changes,
            impact=impact,
        )

    # ==================================================
    # IMPACT
    # ==================================================

    @staticmethod
    def _determine_impact(
        previous,
        current,
        text_changed: bool,
        attribute_changes: list[AttributeChange],
    ) -> str:

        changed_attributes = {
            change.attribute
            for change in attribute_changes
        }

        # ----------------------------------------------
        # HIGH IMPACT
        #
        # Changes that can directly break a scraper.
        # ----------------------------------------------

        if "href" in changed_attributes:

            return "HIGH"

        if "id" in changed_attributes:

            return "HIGH"

        if "name" in changed_attributes:

            return "HIGH"

        # ----------------------------------------------
        # MEDIUM IMPACT
        # ----------------------------------------------

        if "class" in changed_attributes:

            return "MEDIUM"

        if text_changed:

            return "MEDIUM"

        # ----------------------------------------------
        # LOW
        # ----------------------------------------------

        if attribute_changes:

            return "LOW"

        return "NONE"