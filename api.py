import os
import shutil
import tempfile
import time
import uuid
from pathlib import Path
from statistics import mean
from typing import List

from fastapi import FastAPI, File, HTTPException, Query, UploadFile

from file_processors import FileProcessor
from language_detector import LanguageDetector
from ocr_service import OCRModelManager
from schemas import OCRPrediction, OCRResponse, PerformanceMetrics

try:
    import psutil
except ImportError:
    psutil = None


app = FastAPI(title="Multi-language OCR API", version="2.0.0")

DEFAULT_CONFIDENCE_THRESHOLD = 0.75
DEFAULT_TEXT_DET_LIMIT_SIDE_LEN = int(os.getenv("OCR_TEXT_DET_LIMIT_SIDE_LEN", "960"))
DEFAULT_LANGUAGE = os.getenv("OCR_LANGUAGE", "auto").lower()
AUTO_LANGUAGE = "auto"
OCR_DEVICE = os.getenv("OCR_DEVICE", "cpu").lower()

ocr_manager = OCRModelManager(
    device="gpu" if OCR_DEVICE == "gpu" else "cpu",
    text_det_limit_side_len=DEFAULT_TEXT_DET_LIMIT_SIDE_LEN,
)
language_detector = LanguageDetector()


def _save_upload_file(upload_file: UploadFile, destination: Path) -> Path:
    suffix = Path(upload_file.filename).suffix or ".bin"
    dest_path = destination / f"{uuid.uuid4()}{suffix}"
    with dest_path.open("wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    return dest_path


def _combine_text(extracted_text: str, predictions: List[OCRPrediction]) -> str:
    ocr_text = " ".join(pred.text for pred in predictions)
    combined = " ".join(filter(None, [extracted_text or "", ocr_text]))
    return combined.strip()


async def _detect_lang_for_ocr(text: str, fallback: str = DEFAULT_LANGUAGE) -> str:
    if not text:
        return fallback if fallback != AUTO_LANGUAGE else "ar"

    detected = language_detector.detect(text)
    if detected["confidence"] >= 0.40 and detected["language"] != "und":
        return detected["language"]
    return fallback if fallback != AUTO_LANGUAGE else "ar"


async def _process_file(upload_file: UploadFile, confidence_threshold: float, lang: str, include_rows: bool = False) -> OCRResponse:
    start_time = time.perf_counter()
    process = psutil.Process(os.getpid()) if psutil else None
    cpu_start = process.cpu_times() if process else None
    ocr_time = 0.0

    with tempfile.TemporaryDirectory() as temp_dir_name:
        temp_dir = Path(temp_dir_name)
        upload_path = _save_upload_file(upload_file, temp_dir)
        processor = FileProcessor(temp_dir=temp_dir)
        file_data = processor.process_file(upload_path)

        extracted_text = file_data.get("extracted_text")
        image_paths: List[Path] = file_data.get("image_paths", [])
        predictions: List[OCRPrediction] = []
        escalated = False
        model_used = "text-only"
        average_confidence = 0.0
        rows = None
        page_count = file_data.get("page_count", len(image_paths))
        image_count = file_data.get("image_count", len(image_paths))

        if lang == AUTO_LANGUAGE:
            lang = await _detect_lang_for_ocr(
                extracted_text or "",
                fallback="ar" if DEFAULT_LANGUAGE == AUTO_LANGUAGE else DEFAULT_LANGUAGE,
            )
            if lang == AUTO_LANGUAGE and image_paths:
                preview_text = ocr_manager.detect_text(
                    str(image_paths[0]),
                    lang="ar" if DEFAULT_LANGUAGE == AUTO_LANGUAGE else DEFAULT_LANGUAGE,
                )
                lang = await _detect_lang_for_ocr(preview_text, fallback="ar")

        if image_paths:
            model_used = "basic"
            confidences: List[float] = []
            for image_path in image_paths:
                ocr_start = time.perf_counter()
                result = ocr_manager.predict(
                    str(image_path),
                    lang=lang,
                    confidence_threshold=confidence_threshold,
                )
                ocr_time += time.perf_counter() - ocr_start
                if result["escalated"]:
                    escalated = True
                    model_used = result["model_used"]
                for prediction in result["predictions"]:
                    predictions.append(OCRPrediction(**prediction))
                    confidences.append(prediction["confidence"])
            if confidences:
                average_confidence = float(mean(confidences))

            if include_rows and predictions:
                rows = [
                    {"y_start": r["y_start"], "y_end": r["y_end"], "items": [OCRPrediction(**item) for item in r["items"]]}
                    for r in ocr_manager.group_predictions_into_rows([p.dict() for p in predictions])
                ]

        combined_text = _combine_text(extracted_text, predictions)
        language_data = language_detector.detect(combined_text)

        end_time = time.perf_counter()
        cpu_end = process.cpu_times() if process else None

        metrics = PerformanceMetrics(
            total_time_ms=(end_time - start_time) * 1000,
            ocr_time_ms=ocr_time * 1000,
            cpu_user_time=cpu_end.user - cpu_start.user if cpu_start and cpu_end else 0.0,
            cpu_system_time=cpu_end.system - cpu_start.system if cpu_start and cpu_end else 0.0,
            page_count=page_count,
            image_count=image_count,
            recognized_words=len(predictions),
        )

        return OCRResponse(
            filename=upload_file.filename,
            file_type=file_data["file_type"],
            language=language_data["language"],
            language_confidence=language_data["confidence"],
            model_used=model_used,
            escalated=escalated,
            total_predictions=len(predictions),
            average_confidence=average_confidence,
            extracted_text=extracted_text,
            predictions=predictions,
            rows=rows,
            metrics=metrics,
        )


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "Multi-language OCR API", "version": "2.0.0"}


@app.post("/ocr/predict", response_model=OCRResponse)
async def predict_ocr(
    file: UploadFile = File(...),
    confidence_threshold: float = Query(
        DEFAULT_CONFIDENCE_THRESHOLD,
        ge=0.0,
        le=1.0,
        description="Confidence threshold for model escalation",
    ),
    lang: str = Query(
        DEFAULT_LANGUAGE,
        min_length=2,
        max_length=10,
        description="OCR language code, e.g. ar, fa, tr, en. Use 'auto' to detect language from extracted text when available.",
    ),
    include_rows: bool = Query(
        False,
        description="If true, group predictions into rows based on Y-coordinate proximity for structured output",
    ),
):
    try:
        return await _process_file(file, confidence_threshold, lang.lower(), include_rows)
    except ValueError as value_error:
        raise HTTPException(status_code=415, detail=str(value_error))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/ocr/predict-batch", response_model=List[OCRResponse])
async def predict_ocr_batch(
    files: List[UploadFile] = File(...),
    confidence_threshold: float = Query(
        DEFAULT_CONFIDENCE_THRESHOLD,
        ge=0.0,
        le=1.0,
        description="Confidence threshold for model escalation",
    ),
    lang: str = Query(
        DEFAULT_LANGUAGE,
        min_length=2,
        max_length=10,
        description="OCR language code, e.g. ar, fa, tr, en. Use 'auto' to detect language from extracted text when available.",
    ),
    include_rows: bool = Query(
        False,
        description="If true, group predictions into rows based on Y-coordinate proximity for structured output",
    ),
):
    results: List[OCRResponse] = []
    for file in files:
        results.append(await _process_file(file, confidence_threshold, lang.lower(), include_rows))
    return results


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
