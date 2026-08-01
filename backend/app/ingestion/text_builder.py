from app.models import ClinicalTrial


class TrialTextBuilder:

    @staticmethod
    def build(trial: ClinicalTrial) -> str:

        sections = []

        if trial.brief_title:
            sections.append(
                f"Brief Title:\n{trial.brief_title}"
            )

        if trial.official_title:
            sections.append(
                f"Official Title:\n{trial.official_title}"
            )

        if trial.study_type:
            sections.append(
                f"Study Type:\n{trial.study_type}"
            )

        if trial.phase:
            sections.append(
                "Phase:\n" + ", ".join(trial.phase)
            )

        if trial.status:
            sections.append(
                f"Recruitment Status:\n{trial.status}"
            )

        if trial.conditions:
            sections.append(
                "Conditions:\n" + "\n".join(trial.conditions)
            )

        if trial.summary:
            sections.append(
                f"Summary:\n{trial.summary}"
            )

        if trial.sponsor:
            sections.append(
                f"Sponsor:\n{trial.sponsor}"
            )

        if trial.enrollment:
            sections.append(
                f"Enrollment:\n{trial.enrollment}"
            )

        if trial.eligibility:
            sections.append(
                f"Eligibility:\n{trial.eligibility}"
            )

        if trial.interventions:

            interventions = []

            for item in trial.interventions:

                if isinstance(item, dict):

                    if item.get("name"):
                        interventions.append(item["name"])

                    elif item.get("type"):
                        interventions.append(item["type"])

                    else:
                        interventions.append(str(item))

                else:
                    interventions.append(str(item))

            sections.append(
                "Interventions:\n" +
                "\n".join(interventions)
            )

        if trial.primary_outcomes:

            outcomes = []

            for item in trial.primary_outcomes:

                if isinstance(item, dict):

                    if item.get("measure"):
                        outcomes.append(item["measure"])
                    else:
                        outcomes.append(str(item))

                else:
                    outcomes.append(str(item))

            sections.append(
                "Primary Outcomes:\n" +
                "\n".join(outcomes)
            )

        if trial.locations:

            sections.append(
                f"Locations: {len(trial.locations)} study locations"
            )

        return "\n\n".join(sections)