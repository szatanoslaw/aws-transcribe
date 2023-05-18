import json
from typing import Dict, List

import validators

import constants
from models import Transcription
from event_bridge import EventBridgeHandler
from utils import validate_extension, build_response


def lambda_handler(event, context):
    return TranscriptionCreator().run(
        event["body"], event["requestContext"]["requestId"]
    )


class TranscriptionCreator:
    def run(self, request_body: str, request_id: str):
        request_body = json.loads(request_body)
        print("Request body:", request_body)
        self._validate_url(request_body["audio_url"])
        request_body["sentences"] = self._parse_sentences_to_dicts(
            request_body["sentences"]
        )
        print("Validated successfully")
        transcription = Transcription(request_id, **request_body)
        transcription.save()
        print(f"Transcription #{transcription.request_id} created")
        EventBridgeHandler().run(
            event_type=constants.TranscribeEvents.DOWNLOAD.value,
            body={
                "request_id": transcription.request_id,
                "audio_url": transcription.audio_url,
            },
        )
        return self._prepare_response(transcription)

    @staticmethod
    def _validate_url(audio_url: str):
        validators.url(audio_url)
        validate_extension(audio_url, constants.SUPPORTED_FILE_FORMATS)

    @staticmethod
    def _parse_sentences_to_dicts(sentences: List[str]) -> List[Dict[str, str]]:
        return [{"plain_text": sentence} for sentence in sentences]

    @staticmethod
    def _prepare_response(transcription: Transcription) -> Dict:
        return build_response(
            {
                "request_id": transcription.request_id,
                "message": "Your request was accepted successfully",
            }
        )
