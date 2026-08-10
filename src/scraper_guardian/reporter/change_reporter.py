
from __future__ import annotations

from dataclasses import dataclass, field

from ..detector.change_analyzer import ElementChange


@dataclass
class ChangeReport:
    """
    Human-readable summary of detected scraper-impacting changes.
    """

    total_changes: int
    high_risk: int
    medium_risk: int
    low_risk: int

    changes: list[ElementChange] = field(default_factory=list)

    recommendations: list[str] = field(
        default_factory=list
    )


class ChangeReporter:
    """
    Convert ElementChange objects into a scraper impact report.

    The ChangeAnalyzer detects what changed.
    The ChangeReporter explains what those changes mean
    for a scraper.
    """

    # ==================================================
    # PUBLIC API
    # ==================================================

    def generate(
        self,
        changes: list[ElementChange],
    ) -> ChangeReport:

        high_risk = [
            change
            for change in changes
            if change.severity == "HIGH"
        ]

        medium_risk = [
            change
            for change in changes
            if change.severity == "MEDIUM"
        ]

        low_risk = [
            change
            for change in changes
            if change.severity == "LOW"
        ]

        recommendations = (
            self._generate_recommendations(changes)
        )

        return ChangeReport(
            total_changes=len(changes),
            high_risk=len(high_risk),
            medium_risk=len(medium_risk),
            low_risk=len(low_risk),
            changes=changes,
            recommendations=recommendations,
        )

    # ==================================================
    # RECOMMENDATIONS
    # ==================================================

    def _generate_recommendations(
        self,
        changes: list[ElementChange],
    ) -> list[str]:

        recommendations: list[str] = []

        href_changes = [
            change
            for change in changes
            if change.attribute == "href"
            and change.tag == "a"
        ]

        if href_changes:
            recommendations.append(
                self._href_recommendation(
                    href_changes
                )
            )

        id_changes = [
            change
            for change in changes
            if change.attribute == "id"
        ]

        if id_changes:
            recommendations.append(
                "Element IDs changed. "
                "Review CSS/XPath selectors that "
                "depend on the affected IDs."
            )

        class_changes = [
            change
            for change in changes
            if change.attribute == "class"
        ]

        if class_changes:
            recommendations.append(
                "CSS classes changed. "
                "Review class-based selectors "
                "used by the scraper."
            )

        src_changes = [
            change
            for change in changes
            if change.attribute == "src"
        ]

        if src_changes:
            recommendations.append(
                "Resource URLs changed. "
                "Review document, image, JavaScript, "
                "or other resource extraction logic."
            )

        action_changes = [
            change
            for change in changes
            if change.attribute == "action"
        ]

        if action_changes:
            recommendations.append(
                "Form submission URLs changed. "
                "Review scraper form-submission logic."
            )

        text_changes = [
            change
            for change in changes
            if change.change_type == "text_changed"
        ]

        if text_changes:
            recommendations.append(
                "Visible text changed. "
                "Review text-based selectors and "
                "element identification logic."
            )

        return recommendations

    # ==================================================
    # HREF ANALYSIS
    # ==================================================

    @staticmethod
    def _href_recommendation(
        changes: list[ElementChange],
    ) -> str:

        old_values = [
            str(change.old_value)
            for change in changes
            if change.old_value
        ]

        new_values = [
            str(change.new_value)
            for change in changes
            if change.new_value
        ]

        # Detect the common bid URL migration.
        old_bid_pattern = any(
            "bidID=" in value
            for value in old_values
        )

        new_bid_pattern = any(
            "/procurement/bid/" in value
            for value in new_values
        )

        if old_bid_pattern and new_bid_pattern:
            return (
                "The bid URL structure appears to have "
                "changed from:\n\n"
                "    bids.aspx?bidID=<id>\n\n"
                "to:\n\n"
                "    /procurement/bid/<id>\n\n"
                "A scraper using the old bid URL pattern "
                "should be reviewed."
            )

        return (
            "Link destinations changed. "
            "Review URL extraction and navigation "
            "logic used by the scraper."
        )

    # ==================================================
    # TEXT OUTPUT
    # ==================================================

    def format_text(
        self,
        report: ChangeReport,
    ) -> str:

        lines: list[str] = []

        lines.append(
            "=" * 70
        )
        lines.append(
            "SCRAPER IMPACT REPORT"
        )
        lines.append(
            "=" * 70
        )

        lines.append(
            f"Total changes: {report.total_changes}"
        )

        lines.append(
            f"High risk:     {report.high_risk}"
        )

        lines.append(
            f"Medium risk:   {report.medium_risk}"
        )

        lines.append(
            f"Low risk:      {report.low_risk}"
        )

        lines.append("")

        # --------------------------------------------------
        # Changes
        # --------------------------------------------------

        if report.changes:

            lines.append(
                "DETECTED CHANGES"
            )

            lines.append(
                "-" * 70
            )

            for index, change in enumerate(
                report.changes,
                start=1,
            ):

                lines.append(
                    f"\n[{index}]"
                )

                lines.append(
                    f"Type:       {change.change_type}"
                )

                lines.append(
                    f"Tag:        {change.tag}"
                )

                lines.append(
                    f"Path:       {change.path}"
                )

                if change.attribute:
                    lines.append(
                        f"Attribute:  {change.attribute}"
                    )

                lines.append(
                    f"Severity:   {change.severity}"
                )

                if change.old_value is not None:
                    lines.append(
                        f"Old:        {change.old_value}"
                    )

                if change.new_value is not None:
                    lines.append(
                        f"New:        {change.new_value}"
                    )

                if change.impact:
                    lines.append(
                        f"Impact:     {change.impact}"
                    )

                if change.evidence:
                    lines.append(
                        "Evidence:"
                    )

                    for evidence in change.evidence:
                        lines.append(
                            f"    ✓ {evidence}"
                        )

        else:

            lines.append(
                "NO SCRAPER-IMPACTING CHANGES DETECTED"
            )

        # --------------------------------------------------
        # Recommendations
        # --------------------------------------------------

        if report.recommendations:

            lines.append("")
            lines.append(
                "RECOMMENDATIONS"
            )

            lines.append(
                "-" * 70
            )

            for index, recommendation in enumerate(
                report.recommendations,
                start=1,
            ):

                lines.append(
                    f"\n[{index}]"
                )

                lines.append(
                    recommendation
                )

        lines.append("")
        lines.append(
            "=" * 70
        )

        return "\n".join(lines)

