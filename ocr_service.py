from statistics import mean
from typing import Dict, List, Optional

from paddleocr import PaddleOCR


class OCRModelManager:
    SUPPORTED_LANGUAGES = {
        "ar",
        "en",
        "ch",
        "japan",
        "korean",
        "french",
        "german",
        "spanish",
        "russian",
        "it",
        "pt",
        "nl",
        "vi",
        "th",
        # Add other supported PaddleOCR language codes here.
    }

    RECOGNITION_MODEL_OVERRIDES = {
        "ar": "arabic_PP-OCRv5_mobile_rec",
    }

    def __init__(
        self,
        device: str = "cpu",
        text_det_limit_side_len: int = 960,
    ):
        self.device = device
        self.text_det_limit_side_len = text_det_limit_side_len
        self.basic_models: Dict[str, PaddleOCR] = {}
        self.escalated_models: Dict[str, PaddleOCR] = {}

    def get_basic_model(self, lang: str) -> PaddleOCR:
        lang = lang.lower()
        if lang not in self.basic_models:
            self.basic_models[lang] = self._build_basic_model(lang)
        return self.basic_models[lang]

    def get_escalated_model(self, lang: str) -> PaddleOCR:
        lang = lang.lower()
        if lang not in self.escalated_models:
            self.escalated_models[lang] = self._build_escalated_model(lang)
        return self.escalated_models[lang]

    def _build_basic_model(self, lang: str) -> PaddleOCR:
        kwargs = {
            "text_detection_model_name": "PP-OCRv5_mobile_det",
            "use_doc_orientation_classify": False,
            "use_doc_unwarping": False,
            "use_textline_orientation": False,
            "device": self.device,
        }

        if lang in self.RECOGNITION_MODEL_OVERRIDES:
            kwargs["text_recognition_model_name"] = self.RECOGNITION_MODEL_OVERRIDES[lang]
        else:
            kwargs["lang"] = lang

        return PaddleOCR(**kwargs)

    def _build_escalated_model(self, lang: str) -> PaddleOCR:
        kwargs = {
            "use_doc_orientation_classify": False,
            "use_doc_unwarping": False,
            "use_textline_orientation": False,
            "device": self.device,
        }

        if lang in self.RECOGNITION_MODEL_OVERRIDES:
            kwargs["text_recognition_model_name"] = self.RECOGNITION_MODEL_OVERRIDES[lang]
        else:
            kwargs["ocr_version"] = "PP-OCRv5"
            kwargs["lang"] = lang

        return PaddleOCR(**kwargs)

    def predict(
        self,
        image_path: str,
        lang: str = "ar",
        confidence_threshold: float = 0.75,
    ) -> Dict[str, object]:
        lang = lang.lower()
        if lang == "auto":
            lang = "ar"
        basic_model = self.get_basic_model(lang)
        result = self._run_model(basic_model, image_path)
        metrics = self._evaluate(result)
        escalated = False
        model_used = "basic"

        if metrics["avg_confidence"] < confidence_threshold or metrics["recognized_words"] == 0:
            escalated = True
            model_used = "escalated"
            escalated_model = self.get_escalated_model(lang)
            result = self._run_model(escalated_model, image_path)
            metrics = self._evaluate(result)

        predictions = self._format_predictions(result)
        return {
            "predictions": predictions,
            "model_used": model_used,
            "escalated": escalated,
            "recognized_words": metrics["recognized_words"],
            "average_confidence": metrics["avg_confidence"],
        }

    def _run_model(self, model: PaddleOCR, image_path: str) -> List[Dict[str, object]]:
        return model.predict(
            image_path,
            text_det_limit_side_len=self.text_det_limit_side_len,
            return_word_box=True,
        )

    def detect_text(self, image_path: str, lang: str = "ar") -> str:
        lang = lang.lower()
        if lang == "auto":
            lang = "ar"

        model = self.get_basic_model(lang)
        result = model.predict(
            image_path,
            text_det_limit_side_len=self.text_det_limit_side_len,
            return_word_box=False,
        )

        return " ".join(
            text
            for item in result
            for text in item.get("rec_texts", [])
        )

    def _format_predictions(self, result: List[Dict[str, object]]) -> List[Dict[str, object]]:
        predictions: List[Dict[str, object]] = []
        for item in result:
            rec_texts = item.get("rec_texts", [])
            rec_scores = item.get("rec_scores", [])
            text_word_boxes = item.get("text_word_boxes", [])
            for idx, (text, confidence) in enumerate(zip(rec_texts, rec_scores)):
                pred = {"text": text, "confidence": float(confidence)}
                if idx < len(text_word_boxes):
                    box = text_word_boxes[idx]
                    if box is not None and len(box) > 0 and len(box[0]) >= 4:
                        pred["bbox"] = {
                            "x1": float(box[0][0]),
                            "y1": float(box[0][1]),
                            "x2": float(box[0][2]),
                            "y2": float(box[0][3]),
                        }
                predictions.append(pred)
        return predictions

    def group_predictions_into_rows(
        self,
        predictions: List[Dict[str, object]],
        y_tolerance: float = 5.0,
    ) -> List[Dict[str, object]]:
        """Group predictions into rows based on Y-coordinate proximity."""
        if not predictions:
            return []

        predictions_with_bbox = [
            p for p in predictions if p.get("bbox")
        ]
        if not predictions_with_bbox:
            return []

        sorted_preds = sorted(
            predictions_with_bbox,
            key=lambda p: (p["bbox"]["y1"], p["bbox"]["x1"]),
        )

        rows: List[Dict[str, object]] = []
        current_row: List[Dict[str, object]] = []
        current_y_start = None
        current_y_end = None

        for pred in sorted_preds:
            y1 = pred["bbox"]["y1"]
            y2 = pred["bbox"]["y2"]

            if current_y_start is None:
                current_y_start = y1
                current_y_end = y2
                current_row = [pred]
            elif abs(y1 - current_y_start) <= y_tolerance:
                current_row.append(pred)
                current_y_end = max(current_y_end, y2)
            else:
                rows.append({
                    "y_start": current_y_start,
                    "y_end": current_y_end,
                    "items": current_row,
                })
                current_y_start = y1
                current_y_end = y2
                current_row = [pred]

        if current_row:
            rows.append({
                "y_start": current_y_start,
                "y_end": current_y_end,
                "items": current_row,
            })

        return rows

    def _evaluate(self, result: List[Dict[str, object]]) -> Dict[str, float]:
        scores: List[float] = []
        count = 0
        for item in result:
            rec_texts = item.get("rec_texts", [])
            rec_scores = item.get("rec_scores", [])
            count += len(rec_texts)
            scores.extend(float(score) for score in rec_scores)

        return {
            "recognized_words": count,
            "avg_confidence": float(mean(scores)) if scores else 0.0,
        }
