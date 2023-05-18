import json
from typing import Tuple, Dict

import boto3

class EventBridgeHandler:
    def __init__(self):
        self.client = boto3.client("events")

    def run(self, event_type: Tuple[str, str], body: Dict):
        detail_type, source = event_type
        response = self.client.put_events(
            Entries=[
                {
                    "DetailType": detail_type,
                    "Source": source,
                    "Detail": json.dumps(body),
                }
            ]
        )
        print("Event bridge events creation response", response)
