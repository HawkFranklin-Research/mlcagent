import json
from mlca.errors import MlcaUserError


def decode(text: str):
    text = text.strip()
    if text.startswith('```'):
        text = text.split('\n',1)[1].rsplit('```',1)[0].strip()
    return json.loads(text)


def complete(client,role,messages,schema,context,categories):
    last = ''
    for attempt in range(2):
        response = client.complete(role,messages,schema=schema,context=context,categories=categories)
        try:
            parsed = schema.model_validate(decode(response.text))
            response.parsed = parsed
            return response
        except (ValueError,TypeError) as exc:
            last = str(exc)[:1500]
            if attempt==0:
                messages = [*messages,{'role':'assistant','content':response.text},
                            {'role':'user','content':f'Correct the JSON to match the supplied schema. Validation: {last}'}]
    raise MlcaUserError('Structured response invalid after one repair: '+last)
