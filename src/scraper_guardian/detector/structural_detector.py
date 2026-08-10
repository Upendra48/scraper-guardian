from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from bs4 import BeautifulSoup

@dataclass
class ElementSnapshot:
    tag: str
    path: str
    attributes: dict
    text: str

@dataclass
class StructuralChange:
    change_type: str
    tag: str
    path: str
    details: str
    old_value: str | None = None
    new_value: str | None = None


@dataclass
class StructuralDiff:
    changed: bool
    changes: list[StructuralChange] = field(
        default_factory=list
    )


class StructuralDetector:
    """Compare the DOM structure of two HTML snapshots."""

    def compare(
        self,
        previous_html: str | Path,
        current_html: str | Path,
    ) -> StructuralDiff:

        previous_html = self._read_html(previous_html)
        current_html = self._read_html(current_html)

        previous_soup = BeautifulSoup(
            previous_html,
            "html.parser",
        )

        current_soup = BeautifulSoup(
            current_html,
            "html.parser",
        )

        previous_elements = self._get_elements(
            previous_soup
        )

        current_elements = self._get_elements(
            current_soup
        )

        changes = []

        previous_paths = set(previous_elements)
        current_paths = set(current_elements)

        # Elements that were added.
        for path in current_paths - previous_paths:
            element = current_elements[path]

            changes.append(
                StructuralChange(
                    change_type="element_added",
                    tag=element.tag,
                    path=element.path,
                    details=str(element)[:200],
                )
            )

        # Elements that were removed.
        for key in previous_paths - current_paths:
            element = previous_elements[path]

            changes.append(
                StructuralChange(
                    change_type="element_removed",
                    tag=element.name,
                    path=element.path,
                    details=str(element)[:200],
                )
            )
            
        # Existing elements
        for path in previous_paths & current_paths:

            previous_element = previous_elements[path]
            current_element = current_elements[path]

            self._compare_attributes(
                previous_element,
                current_element,
                changes,
            )
            
            self._compare_text(
                previous_element,
                current_element,
                changes,
            )
        
        return StructuralDiff(
            changed=bool(changes),
            changes=changes,
        )    
        
    
    # HTML Loading    

    @staticmethod
    def _read_html(
        html_or_path: str | Path,
    ) -> str:

        path = Path(html_or_path)

        if path.exists():
            return path.read_text(
                encoding="utf-8"
            )

        return str(html_or_path)
    
    # Element Extraction
    @staticmethod
    def _get_elements(
        soup: BeautifulSoup,
    ) -> dict[str, ElementSnapshot]:

        elements:dict[str, ElementSnapshot] = {}

        for element in soup.find_all(True):

            path = StructuralDetector._get_path(
                element
            )
            
            attributes = {}
            
            for name, value in element.attrs.items():
                
                if isinstance(value, list):
                    value = " ".join(value)
                    
                attributes[name]=  str(value)    
                
            text = element.get_text(
                " ", strip=True,
            )    
            
            snapshot = ElementSnapshot(
                tag=element.name,
                path=path,
                attributes=attributes,
                text=text,
            )
            
            elements[path] = snapshot
            
        return elements


    # Path generation
    @staticmethod
    def _get_path(element) -> str:

        path = []

        current = element

        while current is not None and current.name:
            
            if current.name == "[document]":
                break
            
            if current.parent is None:
                path.append(current.name)
                break

            siblings = [
                sibling
                for sibling in current.parent.find_all(
                    current.name,
                    recursive=False,
                )
            ]

            index = siblings.index(current) + 1

            path.append(
                f"{current.name}[{index}]"
            )

            current = current.parent

        return "/" + "/".join(
            reversed(path)
        )
    
    
    # ======================================================
    # Attribute comparison
    # ======================================================

    @staticmethod
    def _compare_attributes(
        previous: ElementSnapshot,
        current: ElementSnapshot,
        changes: list[StructuralChange],
    ):

        attribute_names = (
            set(previous.attributes)
            | set(current.attributes)
        )

        for attribute in attribute_names:

            old_value = previous.attributes.get(
                attribute
            )

            new_value = current.attributes.get(
                attribute
            )

            if old_value == new_value:
                continue

            changes.append(
                StructuralChange(
                    change_type="attribute_changed",
                    tag=current.tag,
                    path=current.path,
                    details=(
                        f"Attribute '{attribute}' "
                        "changed."
                    ),
                    old_value=old_value,
                    new_value=new_value,
                )
            )

    # ======================================================
    # Text comparison
    # ======================================================

    @staticmethod
    def _compare_text(
        previous: ElementSnapshot,
        current: ElementSnapshot,
        changes: list[StructuralChange],
    ):

        if previous.text == current.text:
            return

        changes.append(
            StructuralChange(
                change_type="text_changed",
                tag=current.tag,
                path=current.path,
                details=(
                    f"Text content of "
                    f"<{current.tag}> changed."
                ),
                old_value=previous.text[:500],
                new_value=current.text[:500],
            )
        )