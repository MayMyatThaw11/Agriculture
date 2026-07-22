from fastapi import APIRouter, UploadFile, status

from app.schemas.disease import DiseaseDetectionResponse

router = APIRouter(tags=["disease-detection"])

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_FILE_SIZE = 8 * 1024 * 1024


@router.post(
    "/disease-detect",
    response_model=DiseaseDetectionResponse,
    status_code=status.HTTP_200_OK,
    summary="Detect plant disease from an image",
)
async def disease_detect(file: UploadFile):
    if file.content_type not in ALLOWED_TYPES:
        return DiseaseDetectionResponse(
            plantName="",
            scientificName="",
            healthStatus="Invalid file type. Please upload JPG, PNG, or WEBP.",
            healthScore=0,
            detectedDisease="",
            confidenceScore=0,
            diseaseSeverity="",
            estimatedAffectedArea="",
            visibleSymptoms=[],
            possibleCauses=[],
            treatmentRecommendations=["Upload a valid image file."],
            preventionRecommendations=[],
        )

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        return DiseaseDetectionResponse(
            plantName="",
            scientificName="",
            healthStatus="File too large. Maximum size is 8 MB.",
            healthScore=0,
            detectedDisease="",
            confidenceScore=0,
            diseaseSeverity="",
            estimatedAffectedArea="",
            visibleSymptoms=[],
            possibleCauses=[],
            treatmentRecommendations=["Choose a smaller image."],
            preventionRecommendations=[],
        )

    result = await _analyze_image(contents, file.content_type)
    return DiseaseDetectionResponse(**result)


async def _analyze_image(image_bytes: bytes, content_type: str) -> dict:
    return {
        "plantName": "Plant specimen",
        "scientificName": "Species identified",
        "healthStatus": "Analysis complete — no disease detection model configured",
        "healthScore": 50,
        "detectedDisease": "Unidentified",
        "confidenceScore": 0,
        "diseaseSeverity": "Unknown",
        "estimatedAffectedArea": "N/A — model not available",
        "visibleSymptoms": ["Upload an image for symptom analysis"],
        "possibleCauses": ["Disease detection requires a trained ML model"],
        "treatmentRecommendations": [
            "Set up a plant disease classification model to enable full diagnosis.",
            "For now, consult a local agricultural extension officer.",
        ],
        "preventionRecommendations": [
            "Practice crop rotation.",
            "Maintain good field hygiene.",
            "Monitor plants regularly for early signs of disease.",
        ],
    }
