from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher

from .structural_detector import ElementSnapshot


@dataclass
class ElementMatch:
    previous: ElementSnapshot
    current: ElementSnapshot
    score: float
    evidence: list[str]


class ElementMatcher:
    """
    Match elements between two HTML snapshots.

    Matching is based on element identity rather than XPath alone.
    """

    STABLE_ATTRIBUTES = (
        "id",
        "name",
        "data-id",
        "data-key",
        "data-bid-id",
        "data-item-id",
        "href",
        "src",
    )

    NOISY_TAGS = {
        "script",
        "style",
        "meta",
        "link",
        "svg",
        "use",
        "path",
    }

    def match(
        self,
        previous_elements: dict[str, ElementSnapshot],
        current_elements: dict[str, ElementSnapshot],
    ) -> list[ElementMatch]:

        previous = list(previous_elements.values())
        current = list(current_elements.values())

        matches: list[ElementMatch] = []

        used_previous: set[int] = set()
        used_current: set[int] = set()

        # --------------------------------------------------
        # PASS 1: Exact path
        # --------------------------------------------------

        current_by_path = {
            element.path: index
            for index, element in enumerate(current)
        }

        for previous_index, old in enumerate(previous):

            current_index = current_by_path.get(old.path)

            if current_index is None:
                continue

            if current_index in used_current:
                continue

            new = current[current_index]

            matches.append(
                ElementMatch(
                    previous=old,
                    current=new,
                    score=1.0,
                    evidence=[
                        "Exact path match",
                    ],
                )
            )

            used_previous.add(previous_index)
            used_current.add(current_index)

        # --------------------------------------------------
        # PASS 2: Stable attributes
        # --------------------------------------------------

        for previous_index, old in enumerate(previous):

            if previous_index in used_previous:
                continue

            candidates = []

            for current_index, new in enumerate(current):

                if current_index in used_current:
                    continue

                score = self._stable_attribute_score(
                    old,
                    new,
                )

                if score > 0:
                    candidates.append(
                        (
                            score,
                            current_index,
                        )
                    )

            if not candidates:
                continue

            candidates.sort(
                reverse=True
            )

            score, current_index = candidates[0]

            # Don't accept weak attribute matches.
            if score < 0.75:
                continue

            new = current[current_index]

            matches.append(
                ElementMatch(
                    previous=old,
                    current=new,
                    score=score,
                    evidence=[
                        "Matched using stable attributes",
                    ],
                )
            )

            used_previous.add(previous_index)
            used_current.add(current_index)

        # --------------------------------------------------
        # PASS 3: Text + tag
        # --------------------------------------------------

        for previous_index, old in enumerate(previous):

            if previous_index in used_previous:
                continue

            candidates = []

            for current_index, new in enumerate(current):

                if current_index in used_current:
                    continue

                score = self._structural_score(
                    old,
                    new,
                )

                if score >= 0.80:
                    candidates.append(
                        (
                            score,
                            current_index,
                        )
                    )

            if not candidates:
                continue

            candidates.sort(
                reverse=True
            )

            score, current_index = candidates[0]

            new = current[current_index]

            matches.append(
                ElementMatch(
                    previous=old,
                    current=new,
                    score=score,
                    evidence=[
                        "Matched using tag and normalized text",
                    ],
                )
            )

            used_previous.add(previous_index)
            used_current.add(current_index)

        # --------------------------------------------------
        # PASS 4: Structural context
        # --------------------------------------------------

        for previous_index, old in enumerate(previous):

            if previous_index in used_previous:
                continue

            candidates = []

            for current_index, new in enumerate(current):

                if current_index in used_current:
                    continue

                score = self._structural_score(
                    old,
                    new,
                )

                if score >= 0.70:
                    candidates.append(
                        (
                            score,
                            current_index,
                        )
                    )

            if not candidates:
                continue

            candidates.sort(
                reverse=True
            )

            score, current_index = candidates[0]

            new = current[current_index]

            matches.append(
                ElementMatch(
                    previous=old,
                    current=new,
                    score=score,
                    evidence=[
                        "Matched using structural context",
                    ],
                )
            )

            used_previous.add(previous_index)
            used_current.add(current_index)

        return matches

    # ==================================================
    # STABLE ATTRIBUTE MATCHING
    # ==================================================

    def _stable_attribute_score(
        self,
        previous: ElementSnapshot,
        current: ElementSnapshot,
    ) -> float:

        if previous.tag != current.tag:
            return 0.0

        scores = []

        for attribute in self.STABLE_ATTRIBUTES:

            old_value = previous.attributes.get(
                attribute
            )

            new_value = current.attributes.get(
                attribute
            )

            if not old_value or not new_value:
                continue

            if old_value == new_value:

                # ID/name/data-id are extremely strong.
                if attribute in {
                    "id",
                    "name",
                    "data-id",
                    "data-key",
                    "data-bid-id",
                    "data-item-id",
                }:
                    return 1.0

                scores.append(0.90)

        if not scores:
            return 0.0

        return max(scores)

    # ==================================================
    # TEXT MATCHING
    # ==================================================

    def _text_score(
        self,
        previous: ElementSnapshot,
        current: ElementSnapshot,
    ) -> float:

        if previous.tag != current.tag:
            return 0.0

        old_text = self._normalize_text(
            previous.text
        )

        new_text = self._normalize_text(
            current.text
        )

        if not old_text or not new_text:
            return 0.0

        # Avoid matching huge page-level text.
        if len(old_text) > 300:
            return 0.0

        if len(new_text) > 300:
            return 0.0

        return SequenceMatcher(
            None,
            old_text,
            new_text,
        ).ratio()

    # ==================================================
    # STRUCTURAL MATCHING
    # ==================================================

    def _structural_score(
        self,
        previous: ElementSnapshot,
        current: ElementSnapshot,
    ) -> float:

        if previous.tag != current.tag:
            return 0.0

        old_parts = previous.path.split("/")
        new_parts = current.path.split("/")

        if not old_parts or not new_parts:
            return 0.0

        # Compare parent hierarchy without requiring
        # exact XPath equality.
        old_parents = old_parts[:-1]
        new_parents = new_parts[:-1]

        common = 0

        for old_part, new_part in zip(
            reversed(old_parents),
            reversed(new_parents),
        ):
            old_tag = old_part.split("[")[0]
            new_tag = new_part.split("[")[0]

            if old_tag != new_tag:
                break

            common += 1

        if not old_parents or not new_parents:
            return 0.0

        parent_similarity = (
            common
            / max(
                len(old_parents),
                len(new_parents),
            )
        )
        
        if common < 3:
            return 0.0
        
        if parent_similarity < 0.80:
            return 0.0

        return parent_similarity

    # ==================================================
    # NORMALIZATION
    # ==================================================

    @staticmethod
    def _normalize_text(
        text: str | None,
    ) -> str:

        if not text:
            return ""

        return " ".join(
            text.split()
        ).strip()