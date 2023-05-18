import string
from typing import List, Dict

from nltk import sent_tokenize, word_tokenize

import constants
from models import Transcription
from transcribe import TranscribeHandler


def lambda_handler(event, context):
    return FinishTranscriptionHandler().run(
        event_detail=event["detail"],
    )


class FinishTranscriptionHandler:
    def run(self, event_detail: Dict[str, str]):
        request_id = event_detail["TranscriptionJobName"]
        transcription_status = event_detail["TranscriptionJobStatus"]
        transcription = Transcription.get(request_id)

        if transcription_status != TranscribeHandler.TRANSCRIPTION_COMPLETED_STATUS:
            error = event_detail.get("FailureReason")
            return self._proces_transcription_failed(
                transcription, transcription_status, error
            )

        transcribe_handler = TranscribeHandler(request_id)
        transcription_text = transcribe_handler.get_transcription_text()
        transcription_text_sentences = self._get_sentences_from_transcription(
            transcription_text
        )
        matched_sentences = self._match_sentences(
            transcription.sentences,
            transcription_text_sentences,
        )
        transcription.update(
            actions=[
                Transcription.status.set(constants.TranscriptionStatus.READY.value),
                Transcription.transcription_url.set(
                    transcribe_handler.get_transcription_url()
                ),
                Transcription.sentences.set(matched_sentences),
            ]
        )

    @staticmethod
    def _proces_transcription_failed(
            transcription: Transcription,
            transcription_status: str,
            transcription_error: str,
    ):
        error_message = f"Transcription ended with '{transcription_status}` status."
        if transcription_error:
            error_message += f" Error message: {transcription_error}"
        transcription.update(
            actions=[
                Transcription.status.set(constants.TranscriptionStatus.ERROR.value),
                Transcription.errors.set(error_message),
            ]
        )

    @staticmethod
    def _get_sentences_from_transcription(transcription: str) -> List[Dict]:
        sentences = sent_tokenize(transcription)
        sentences_with_word_indexes = []
        word_index = 0
        for sentence in sentences:
            words = word_tokenize(sentence)
            end_word_index = (
                    word_index
                    + len([word for word in words if word not in string.punctuation])
                    - 1
            )
            sentences_with_word_indexes.append(
                {
                    "sentence": sentence,
                    "start_word_index": word_index,
                    "end_word_index": end_word_index,
                }
            )
            word_index = end_word_index + 1
        return sentences_with_word_indexes

    @staticmethod
    def _match_sentences(transcription_sentences, transcription_text_sentences):
        for transcription_sentence in transcription_sentences:
            for transcription_text_sentence in transcription_text_sentences:
                if (
                        transcription_text_sentence["sentence"]
                        != transcription_sentence["plain_text"]
                ):
                    continue
                transcription_sentence.was_present = True
                transcription_sentence.start_word_index = transcription_text_sentence[
                    "start_word_index"
                ]
                transcription_sentence.end_word_index = transcription_text_sentence[
                    "end_word_index"
                ]
                break
        return transcription_sentences
