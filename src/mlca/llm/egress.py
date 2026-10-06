import hashlib
from mlca.paths import canonical
from mlca.errors import MlcaUserError

CATEGORIES = {'template_spec','facts','inventory_summary','script','traceback','figure_image','sample_rows','user_text'}


def classify(payload: dict, categories: list[str], allow_sample_rows: bool) -> dict:
    if not set(categories)<=CATEGORIES:
        raise MlcaUserError('Unknown model payload category')
    if 'sample_rows' in categories and not allow_sample_rows:
        raise MlcaUserError('Raw sample rows are disabled by privacy configuration')
    raw = canonical(payload).encode()
    return {'bytes_sent':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'categories':sorted(set(categories))}
