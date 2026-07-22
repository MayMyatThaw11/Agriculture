from fastapi import APIRouter, status
from fastapi.responses import StreamingResponse

from app.schemas.crop_explanation import CropExplanationRequest
from app.services.llm import stream_crop_explanation

router = APIRouter(tags=["crop-explanation"])


@router.post("/crop-explanation", status_code=status.HTTP_200_OK, summary="Get AI crop explanation")
async def crop_explanation(request: CropExplanationRequest):
    async def event_stream():
        async for chunk in stream_crop_explanation(
            request.soil_pH,
            request.rainfall_mm,
            request.temperature_c,
            request.crop,
            request.language,
        ):
            payload = _escape_json(chunk)
            yield f"data: {{{{ \"content\": \"{payload}\", \"done\": false }}}}\n\n"
        yield "data: {\"content\": \"\", \"done\": true}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


def _escape_json(s: str) -> str:
    for old, new in (("\\", "\\\\"), ('"', '\\"'), ("\n", "\\n"), ("\r", "\\r"), ("\t", "\\t")):
        s = s.replace(old, new)
    return s
