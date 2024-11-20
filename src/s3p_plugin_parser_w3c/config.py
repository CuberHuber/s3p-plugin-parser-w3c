import datetime

from s3p_sdk.plugin.config import (
    PluginConfig,
    CoreConfig,
    TaskConfig,
    trigger,
    MiddlewareConfig,
    modules,
    payload
)
from s3p_sdk.plugin.types import SOURCE
from s3p_sdk.module import (
    WebDriver,
)

config = PluginConfig(
    plugin=CoreConfig(
        reference='w3c',
        type=SOURCE,
        files=['w3c.py', ],
        is_localstorage=False
    ),
    task=TaskConfig(
        trigger=trigger.TriggerConfig(
            type=trigger.SCHEDULE,
            interval=datetime.timedelta(days=1),
        )
    ),
    middleware=MiddlewareConfig(
        modules=[
            modules.TimezoneSafeControlConfig(order=1, is_critical=True),
            modules.FilterOnlyNewDocumentWithDB(order=2, is_critical=True),
            modules.SaveDocument(order=3, is_critical=True),
        ],
        bus=None,
    ),
    payload=payload.PayloadConfig(
        file='w3c.py',
        classname='W3C',
        entry=payload.entry.EntryConfig(
            method='content',
            params=[
                payload.entry.ModuleParamConfig(key='driver', module_name=WebDriver, bus=True),
                payload.entry.ConstParamConfig(key='max_count_documents', value=50),
            ]
        )
    )
)

__all__ = ['config']
