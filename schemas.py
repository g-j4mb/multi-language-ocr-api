from typing import List, Optional

from pydantic import BaseModel, Field


class PerformanceMetrics(BaseModel):
    total_time_ms: float = Field(
        ..., description="Total end-to-end processing time in milliseconds"
    )
    ocr_time_ms: float = Field(
        ..., description="Time spent in OCR processing in milliseconds"
    )
    cpu_user_time: float = Field(..., description="User CPU time in seconds")
    cpu_system_time: float = Field(..., description="System CPU time in seconds")
    page_count: int = Field(..., description="Total number of pages/images processed")
    image_count: int = Field(..., description="Number of images processed")
    recognized_words: int = Field(..., description="Total words recognized")


class BoundingBox(BaseModel):
    x1: float = Field(..., description="Left x-coordinate")
    y1: float = Field(..., description="Top y-coordinate")
    x2: float = Field(..., description="Right x-coordinate")
    y2: float = Field(..., description="Bottom y-coordinate")


class OCRPrediction(BaseModel):
    text: str = Field(..., description="Recognized text segment")
    confidence: float = Field(..., description="OCR confidence score between 0 and 1")
    bbox: Optional[BoundingBox] = Field(
        None, description="Bounding box coordinates of the text"
    )


class OCRRow(BaseModel):
    y_start: float = Field(..., description="Y-coordinate of row start")
    y_end: float = Field(..., description="Y-coordinate of row end")
    items: List[OCRPrediction] = Field(..., description="All text items in this row")


class OCRResponse(BaseModel):
    filename: str
    file_type: str
    language: str
    language_confidence: float
    model_used: str
    escalated: bool
    total_predictions: int
    average_confidence: float
    extracted_text: Optional[str] = Field(
        None, description="Text extracted directly from Word documents"
    )
    predictions: List[OCRPrediction]
    rows: Optional[List[OCRRow]] = Field(
        None, description="Predictions grouped by row (Y-coordinate)"
    )
    metrics: Optional[PerformanceMetrics] = Field(
        None, description="Performance metrics including timing and CPU usage"
    )
