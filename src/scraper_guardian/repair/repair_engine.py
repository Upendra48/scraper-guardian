from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RepairSuggestion:
    """
    Represents a proposed repair to scraper logic.
    """

    repair_type: str
    severity: str
    old_pattern: str
    new_pattern: str
    reason: str
    confidence: float


class RepairEngine:
    """
    Convert ChangeAnalyzer recommendations into
    actionable scraper repair suggestions.
    """

    def generate_repairs(
        self,
        recommendations: list[dict],
    ) -> list[RepairSuggestion]:

        repairs: list[RepairSuggestion] = []

        for recommendation in recommendations:

            recommendation_type = recommendation.get(
                "type"
            )

            if recommendation_type == "url_pattern_changed":

                repairs.append(
                    RepairSuggestion(
                        repair_type="url_pattern_update",
                        severity="HIGH",
                        old_pattern="bids.aspx?bidID=<id>",
                        new_pattern="/procurement/bid/<id>",
                        reason=(
                            "The bid URL structure changed. "
                            "The scraper should update its URL "
                            "construction logic."
                        ),
                        confidence=0.98,
                    )
                )

            elif recommendation_type == "selector_class_changed":

                repairs.append(
                    RepairSuggestion(
                        repair_type="selector_update",
                        severity="MEDIUM",
                        old_pattern="CSS class selector",
                        new_pattern="Updated CSS class selector",
                        reason=(
                            "A CSS class used by the page changed. "
                            "Selectors based on that class should "
                            "be reviewed."
                        ),
                        confidence=0.80,
                    )
                )

            elif recommendation_type == "selector_id_changed":

                repairs.append(
                    RepairSuggestion(
                        repair_type="selector_update",
                        severity="HIGH",
                        old_pattern="ID selector",
                        new_pattern="Updated ID selector",
                        reason=(
                            "An element ID changed. "
                            "ID-based scraper selectors should "
                            "be reviewed."
                        ),
                        confidence=0.90,
                    )
                )

            elif recommendation_type == "href_changed":

                repairs.append(
                    RepairSuggestion(
                        repair_type="href_update",
                        severity="HIGH",
                        old_pattern="Previous href",
                        new_pattern="Current href",
                        reason=(
                            "One or more href destinations changed. "
                            "The scraper's URL extraction logic "
                            "should be reviewed."
                        ),
                        confidence=0.85,
                    )
                )

        return repairs