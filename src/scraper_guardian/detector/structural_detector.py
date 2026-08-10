from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from bs4 import BeautifulSoup

@dataclass
class ElementSnaoshot:
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

        previous_keys = set(previous_elements)
        current_keys = set(current_elements)

        # Elements that were added.
        for key in current_keys - previous_keys:
            element = current_elements[key]

            changes.append(
                StructuralChange(
                    change_type="element_added",
                    tag=element.name,
                    path=key,
                    details=str(element)[:200],
                )
            )

        # Elements that were removed.
        for key in previous_keys - current_keys:
            element = previous_elements[key]

            changes.append(
                StructuralChange(
                    change_type="element_removed",
                    tag=element.name,
                    path=key,
                    details=str(element)[:200],
                )
            )
            

        for key in previous_keys & current_keys:

            previous_element = previous_elements[key]
            current_element = current_elements[key]

            previous_attributes = dict(
                previous_element.attrs
            )

            current_attributes = dict(
                current_element.attrs
            )

            attribute_names = (
                set(previous_attributes)
                | set(current_attributes)
            )

            
            # Attributes that changed.
            for attribute in attribute_names:

                old_value = previous_attributes.get(
                    attribute
                )

                new_value = current_attributes.get(
                    attribute
                )

                if old_value == new_value:
                    continue

                changes.append(
                    StructuralChange(
                        change_type="attribute_changed",
                        tag=current_element.name,
                        path=key,
                        details=(
                            f"Attribute '{attribute}' "
                            f"changed."
                        ),
                        old_value=str(old_value),
                        new_value=str(new_value),
                    )
                )    
        
        return StructuralDiff(
            changed=bool(changes),
            changes=changes,
        )

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

    @staticmethod
    def _get_elements(
        soup: BeautifulSoup,
    ) -> dict[str, object]:

        elements = {}

        for element in soup.find_all(True):

            path = StructuralDetector._get_path(
                element
            )
            identity = StructuralDetector._get_identity(
                element
            )
            
            key = f"{path}|{identity}"

            elements[key] = element

        return elements

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
    
    
    @staticmethod
    def _get_identity(element) -> str:
        """
        Generate a stable identity for an HTML element.
        """
        
        #Strongest identifier: id
        element_id = element.get("id")
        if element_id:
            return f"{element.name}#{element['id']}"
        
        
        # Second: name
        name = element.get("name")
        if name:
            return(
                f"{element.name}"
                f"[name={element.get("name")}]"
            )

        classes = element.get("class")

        if classes:
            if isinstance(classes, list):
                classes = ".".join(classes)

            return f"{element.name}.{classes}"
        
        # Useful attributes for links
        href = element.get("href")
        if href:
            return(
                f"{element.name}"
                f"[href='{href}']"
            )    
            
        # Useful attribues for inputs
        input_type = element.get("type")
        if input_type:
            return(
                f"{element.name}"
                f"[type='{input_type}']"
            )    

        # if element.get("name"):
        #     return (
        #     f"{element.name}"
        #     f"[name='{element['name']}']"
        # )

        return element.name