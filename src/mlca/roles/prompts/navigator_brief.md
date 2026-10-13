<!-- Placeholders: summary, template, schema. Response: BriefDraft JSON. -->
Draft a study brief for a {template} study from this table summary (no data rows). Return JSON matching {schema}.
{summary}
aim: one sentence naming what is predicted. target (or duration and event_column for survival): exact column names only.
unit: what one row represents, e.g. "one patient", "one visit" or "one sample". repeated: "Yes", "No" or "Not sure yet".
Leave a field empty when unsure.
