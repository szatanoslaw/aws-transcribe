import json
from typing import Dict, Optional

from smart_open import open
import boto3

import constants
from utils import get_extension, parse_url_to_s3_uri


class TranscribeHandler:
    TRANSCRIPTION_COMPLETED_STATUS = "COMPLETED"
    TRANSCRIPTION_FAILED_STATUS = "FAILED"

    def __init__(self, request_id: str):
        self.client = boto3.client("transcribe")
        self.request_id = request_id
        self._transcription_job = None

    def run(
        self,
        file_uri: str,
        file_format: str = None,
        language_code: str = constants.SupportedLanguages.ENGLISH.value,
    ):
        if file_format is None:
            file_format = get_extension(file_uri)
        response = self.client.start_transcription_job(
            TranscriptionJobName=self.request_id,
            Media={"MediaFileUri": file_uri},
            MediaFormat=file_format,
            LanguageCode=language_code,
            OutputBucketName=constants.TRANSCRIPTION_BUCKET_NAME,
            OutputKey=f"{self.request_id}/transcript.json",
        )
        return response

    def get_transcription_text(self) -> str:
        transcription_uri = parse_url_to_s3_uri(self.get_transcription_url())
        s3_client = boto3.client("s3")
        with open(
            transcription_uri, transport_params={"client": s3_client}
        ) as transcription_file:
            transcribe_output = json.load(transcription_file)
        return transcribe_output["results"]["transcripts"][0]["transcript"]

    def get_transcription_url(self) -> Optional[str]:
        job = self.transcription_job
        if not self._is_transcription_completed(job):
            return None
        return job["TranscriptionJob"]["Transcript"]["TranscriptFileUri"]

    @classmethod
    def _is_transcription_completed(cls, job: Dict) -> bool:
        job_status = job["TranscriptionJob"]["TranscriptionJobStatus"]
        return job_status == cls.TRANSCRIPTION_COMPLETED_STATUS

    @property
    def transcription_job(self, force_fetch: bool = False) -> Dict:
        if self._transcription_job is not None or force_fetch:
            return self._transcription_job
        return self._get_transcription_job()

    def _get_transcription_job(self):
        return self.client.get_transcription_job(TranscriptionJobName=self.request_id)
