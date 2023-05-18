import os.path
from urllib.error import HTTPError

import boto3
from smart_open import open
from urllib.parse import urlparse

import constants
from models import Transcription
from transcribe import TranscribeHandler

s3_client = boto3.client("s3")


def lambda_handler(event, context):
    request_id = event["detail"]["request_id"]
    audio_url = event["detail"]["audio_url"]
    DownloadAudioFileHandler().run(request_id, audio_url)


class DownloadAudioFileHandler:
    def __init__(self):
        self.client = boto3.client("s3")

    def run(
        self,
        request_id: str,
        audio_url: str,
    ):
        s3_file_path = self._get_s3_file_path(request_id, audio_url)
        print(f"Downloading {audio_url} to {s3_file_path}")
        try:
            self._download_file_to_s3_bucket(audio_url, s3_file_path)
        except HTTPError as err:
            print(f"Unable to download file: {err}")
            Transcription.get(request_id).update(
                actions=[
                    Transcription.status.set(constants.TranscriptionStatus.ERROR.value),
                    Transcription.errors.set(err),
                ]
            )
        else:
            print("File downloaded successfully, updating record")
            Transcription.get(request_id).update(
                actions=[
                    Transcription.status.set(
                        constants.TranscriptionStatus.TRANSCRIBING.value
                    ),
                    Transcription.audio_url.set(s3_file_path),
                ]
            )
            print("Starting transcription job")
            TranscribeHandler(request_id).run(s3_file_path)

    @staticmethod
    def _get_s3_file_path(request_id: str, audio_url: str) -> str:
        audio_file_path = urlparse(audio_url).path
        audio_file_name = os.path.basename(audio_file_path)
        return (
            f"s3://{constants.TRANSCRIPTION_BUCKET_NAME}/{request_id}/{audio_file_name}"
        )

    def _download_file_to_s3_bucket(self, audio_url: str, s3_file_path: str):
        with open(
            s3_file_path, "wb", transport_params={"client": s3_client}
        ) as file_out:
            for line in open(audio_url, "rb"):
                file_out.write(line)
