"""
Example client to test the Multi-language OCR API
"""

import requests
import json
from pathlib import Path

API_URL = "http://localhost:8000"


def check_health():
    """Check if API is running"""
    try:
        response = requests.get(f"{API_URL}/health")
        print("✓ API is running:", response.json())
        return True
    except Exception as e:
        print("✗ API is not running:", e)
        return False


def predict_single_image(image_path):
    """Send a single image to OCR API"""
    if not Path(image_path).exists():
        print(f"✗ File not found: {image_path}")
        return None
    
    with open(image_path, "rb") as f:
        files = {"file": f}
        try:
            response = requests.post(f"{API_URL}/ocr/predict", files=files)
            result = response.json()
            print(f"✓ OCR Results for {image_path}:")
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return result
        except Exception as e:
            print(f"✗ Error: {e}")
            return None


def predict_batch(image_paths):
    """Send multiple images to OCR API"""
    files = []
    for image_path in image_paths:
        if Path(image_path).exists():
            files.append(("files", open(image_path, "rb")))
        else:
            print(f"✗ File not found: {image_path}")
    
    if not files:
        return None
    
    try:
        response = requests.post(f"{API_URL}/ocr/predict-batch", files=files)
        result = response.json()
        print(f"✓ Batch OCR Results:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        # Close all files
        for _, file_obj in files:
            file_obj.close()
        
        return result
    except Exception as e:
        print(f"✗ Error: {e}")
        for _, file_obj in files:
            file_obj.close()
        return None


if __name__ == "__main__":
    print("=== Multi-language OCR API Client ===\n")
    
    # Check health
    if check_health():
        print("\n--- Testing Single Image Prediction ---")
        predict_single_image("./sample.jpg")

        print("\n--- Testing Batch Prediction ---")
        # predict_batch(["./sample1.jpg", "./sample2.jpg"])
