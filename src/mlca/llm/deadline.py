"""Kill a trusted transport subprocess at a wall deadline; credentials use pipes only."""

import json
import os
import subprocess

from mlca.errors import MlcaUserError


def exchange(command, body, seconds):
    environment = {
        k: v
        for k, v in os.environ.items()
        if k
        in {"PATH", "SYSTEMROOT", "SSL_CERT_FILE", "SSL_CERT_DIR", "HTTPS_PROXY", "HTTP_PROXY", "NO_PROXY"}
    }
    process = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=environment,
    )
    try:
        stdout, _ = process.communicate(json.dumps(body), timeout=seconds)
    except subprocess.TimeoutExpired:
        process.kill()
        process.communicate()
        raise MlcaUserError(
            "Model call exceeded its wall-clock deadline; provider usage is unavailable",
            category="provider_error",
        ) from None
    except BaseException:
        process.kill()
        process.communicate()
        raise
    if process.returncode:
        raise MlcaUserError("Model transport subprocess failed", category="provider_error")
    try:
        return json.loads(stdout)
    except ValueError:
        raise MlcaUserError("Invalid model transport response", category="provider_error") from None
