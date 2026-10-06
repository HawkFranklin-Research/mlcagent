<!-- Placeholders: observation, allowed, step_id, schema. Response: FactsResponse JSON. -->
Extract facts only from the structured evidence below. Return JSON following {schema}.
Allowed fact keys: {allowed}. Owning step: {step_id}.
Each fact needs key, value, unit (optional), source (exact indexed artifact path), sha256 and step_id.
Use only explicit evidence. Do not infer a number from a figure, assume a missing value or claim
causation. Return an empty list when no justified fact can be cited.
Evidence: {observation}
Each value is one number or a short label (at most 5 words); never prose.
