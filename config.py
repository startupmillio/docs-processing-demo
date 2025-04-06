import logging
import os

from dynaconf import Dynaconf
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.httpx import HttpxIntegration


settings = Dynaconf(
    environments=True,
    default_settings_paths=[
        "settings.toml",
        ".secrets.toml",
    ],
    ROOT_PATH_FOR_DYNACONF=os.path.abspath(__file__),
)

log = logging.getLogger(settings.PROJECT_NAME)
log.setLevel(logging.INFO)

log_formatter = logging.Formatter(
    "[%(asctime)s][%(levelname)s] %(filename)s:%(lineno)d | %(message)s"
)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(log_formatter)

log.addHandler(console_handler)

if settings.LOG_TO_SENTRY:
    integrations = [
        FastApiIntegration(),
        HttpxIntegration(),
    ]

    sentry_sdk.init(
        settings.SENTRY_URL,
        environment=settings.current_env,
        integrations=integrations,
        send_default_pii=True,
    )
