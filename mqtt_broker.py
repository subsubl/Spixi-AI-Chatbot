#!/usr/bin/env python3
"""Lightweight MQTT broker for local testing using hbmqtt.
Run this inside the project's venv.
"""
import asyncio
from hbmqtt.broker import Broker

config = {
    'listeners': {
        'default': {
            'type': 'tcp',
            'bind': '0.0.0.0:1883'
        }
    },
    'sys_interval': 10,
    'topic-check': {
        'enabled': False
    }
}

async def start_broker():
    broker = Broker(config)
    await broker.start()
    # keep running
    await asyncio.Event().wait()

if __name__ == '__main__':
    try:
        asyncio.run(start_broker())
    except KeyboardInterrupt:
        pass
