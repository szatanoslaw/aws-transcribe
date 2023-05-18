from pynamodb import models, attributes

import constants


class Sentence(attributes.DynamicMapAttribute):
    plain_text = attributes.UnicodeAttribute()
    was_present = attributes.BooleanAttribute(default=False)
    start_word_index = attributes.NumberAttribute(null=True, default=None)
    end_word_index = attributes.NumberAttribute(null=True, default=None)


class Transcription(models.Model):
    class Meta:
        table_name = constants.TRANSCRIPTION_TABLE_NAME
        region = constants.TRANSCRIPTION_TABLE_REGION

    request_id = attributes.UnicodeAttribute(hash_key=True)
    audio_url = attributes.UnicodeAttribute()
    transcription_url = attributes.UnicodeAttribute(null=True)
    sentences = attributes.ListAttribute(of=Sentence)

    status = attributes.UnicodeAttribute(
        default=constants.TranscriptionStatus.DOWNLOADING.value
    )
    errors = attributes.UnicodeAttribute(null=True)
