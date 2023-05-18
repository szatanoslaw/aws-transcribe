from enum import Enum

TRANSCRIPTION_TABLE_NAME = "transcriptions"
TRANSCRIPTION_TABLE_REGION = "eu-central-1"
TRANSCRIPTION_BUCKET_NAME = "szatanoslaw-transcriptions-audio"

SUPPORTED_FILE_FORMATS = ["mp3", "wav"]


class SupportedLanguages(Enum):
    ENGLISH = "en-US"


class TranscriptionStatus(Enum):
    DOWNLOADING = "downloading"
    TRANSCRIBING = "transcribing"
    READY = "ready"
    ERROR = "error"


class TranscribeEvents(Enum):
    DOWNLOAD = ("DownloadTriggerEvent", "transcriptions.start-download")
