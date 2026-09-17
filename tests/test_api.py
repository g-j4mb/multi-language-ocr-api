import io

import fitz
import pytest
from docx import Document
from fastapi.testclient import TestClient
from PIL import Image

import api
from file_processors import FileProcessor
from language_detector import LanguageDetector
from ocr_service import OCRModelManager
from schemas import OCRPrediction, OCRResponse


def test_language_detector_detects_english():
    detector = LanguageDetector()
    result = detector.detect("Hello world")

    assert result["language"] == "en"
    assert result["confidence"] > 0.5


def test_file_processor_process_image(tmp_path):
    image_path = tmp_path / "test.png"
    Image.new("RGB", (10, 10), color="white").save(image_path)

    processor = FileProcessor(temp_dir=tmp_path)
    result = processor.process_file(image_path)

    assert result["file_type"] == "image"
    assert result["extracted_text"] is None
    assert len(result["image_paths"]) == 1
    assert result["image_paths"][0].exists()


def test_file_processor_process_docx_text_only(tmp_path):
    docx_path = tmp_path / "test.docx"
    document = Document()
    document.add_paragraph("Hello from Word")
    document.save(docx_path)

    processor = FileProcessor(temp_dir=tmp_path)
    result = processor.process_file(docx_path)

    assert result["file_type"] == "docx"
    assert result["extracted_text"] == "Hello from Word"
    assert isinstance(result["image_paths"], list)
    assert len(result["image_paths"]) == 0


def test_file_processor_process_pdf(tmp_path):
    pdf_path = tmp_path / "test.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "PDF page text")
    doc.save(pdf_path)
    doc.close()

    processor = FileProcessor(temp_dir=tmp_path)
    result = processor.process_file(pdf_path)

    assert result["file_type"] == "pdf"
    assert result["extracted_text"] is None
    assert len(result["image_paths"]) == 1
    assert result["image_paths"][0].suffix == ".png"


def test_file_processor_unsupported_extension(tmp_path):
    data_path = tmp_path / "test.txt"
    data_path.write_text("unsupported")

    processor = FileProcessor(temp_dir=tmp_path)
    with pytest.raises(ValueError, match="Unsupported file type"):
        processor.process_file(data_path)


def test_ocr_service_escalates(monkeypatch):
    class DummyModel:
        def predict(self, *args, **kwargs):
            return []

    monkeypatch.setattr(
        OCRModelManager, "_build_basic_model", lambda self, lang: DummyModel()
    )
    monkeypatch.setattr(
        OCRModelManager, "_build_escalated_model", lambda self, lang: DummyModel()
    )

    manager = OCRModelManager(device="cpu", text_det_limit_side_len=640)
    call_count = {"count": 0}

    def fake_run_model(model, path):
        call_count["count"] += 1
        if call_count["count"] == 1:
            return [{"rec_texts": ["مرحبا"], "rec_scores": [0.2]}]
        return [{"rec_texts": ["مرحبا"], "rec_scores": [0.95]}]

    monkeypatch.setattr(manager, "_run_model", fake_run_model)

    result = manager.predict("/tmp/dummy.png", confidence_threshold=0.5)

    assert result["escalated"] is True
    assert result["model_used"] == "escalated"
    assert result["recognized_words"] == 1
    assert result["average_confidence"] == pytest.approx(0.95, rel=1e-3)


def test_api_health():
    client = TestClient(api.app)
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["service"] == "Multi-language OCR API"


def test_api_predict_endpoint(monkeypatch):
    async def fake_process_file(file, confidence_threshold, lang, include_rows):
        return OCRResponse(
            filename=file.filename,
            file_type="image",
            language="ar",
            language_confidence=0.98,
            model_used="basic",
            escalated=False,
            total_predictions=1,
            average_confidence=0.98,
            extracted_text=None,
            predictions=[OCRPrediction(text="مرحبا", confidence=0.98)],
            rows=None,
        )

    monkeypatch.setattr(api, "_process_file", fake_process_file)
    client = TestClient(api.app)

    image_bytes = io.BytesIO()
    Image.new("RGB", (10, 10), color="white").save(image_bytes, format="PNG")
    image_bytes.seek(0)

    response = client.post(
        "/ocr/predict",
        files={"file": ("test.png", image_bytes, "image/png")},
        params={"confidence_threshold": 0.8, "lang": "auto"},
    )

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["filename"] == "test.png"
    assert json_data["language"] == "ar"
    assert json_data["escalated"] is False
    assert json_data["total_predictions"] == 1


def test_api_predict_batch_endpoint(monkeypatch):
    async def fake_process_file(file, confidence_threshold, lang, include_rows):
        return OCRResponse(
            filename=file.filename,
            file_type="image",
            language="ar",
            language_confidence=0.98,
            model_used="basic",
            escalated=False,
            total_predictions=1,
            average_confidence=0.98,
            extracted_text=None,
            predictions=[OCRPrediction(text="مرحبا", confidence=0.98)],
            rows=None,
        )

    monkeypatch.setattr(api, "_process_file", fake_process_file)
    client = TestClient(api.app)

    img1 = io.BytesIO()
    Image.new("RGB", (10, 10), color="white").save(img1, format="PNG")
    img1.seek(0)

    img2 = io.BytesIO()
    Image.new("RGB", (10, 10), color="white").save(img2, format="PNG")
    img2.seek(0)

    response = client.post(
        "/ocr/predict-batch",
        files=[
            ("files", ("test1.png", img1, "image/png")),
            ("files", ("test2.png", img2, "image/png")),
        ],
        params={"confidence_threshold": 0.8, "lang": "auto"},
    )

    assert response.status_code == 200
    json_data = response.json()
    assert isinstance(json_data, list)
    assert len(json_data) == 2
    assert json_data[0]["filename"] == "test1.png"
    assert json_data[1]["filename"] == "test2.png"
