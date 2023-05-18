from models import Transcription
from utils import build_response


def lambda_handler(event, context):
    record_id = event["pathParameters"]["transcription_id"]

    try:
        transcription = Transcription.get(record_id)
    except Transcription.DoesNotExist:
        return build_response(body={}, status_code=404)
    data = transcription.attribute_values
    data["sentences"] = [
        sentence.attribute_values for sentence in transcription.sentences
    ]
    return build_response(body=data)
