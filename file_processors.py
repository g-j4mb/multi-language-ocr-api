import tempfile
from pathlib import Path
from typing import Dict, List, Optional
from io import BytesIO

import fitz
from docx import Document
from PIL import Image

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".tif"}


class FileProcessor:
    def __init__(self, temp_dir: Optional[Path] = None):
        self.temp_dir = Path(temp_dir or tempfile.gettempdir())
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    def process_file(self, file_path: Path) -> Dict[str, object]:
        suffix = file_path.suffix.lower()
        if suffix in IMAGE_EXTENSIONS:
            return {
                "file_type": "image",
                "extracted_text": None,
                "image_paths": [file_path],
                "page_count": 1,
                "image_count": 1,
            }
        if suffix == ".pdf":
            images = self._pdf_to_images(file_path)
            return {
                "file_type": "pdf",
                "extracted_text": None,
                "image_paths": images,
                "page_count": len(images),
                "image_count": len(images),
            }
        if suffix == ".docx":
            return self._process_docx(file_path)
        raise ValueError(f"Unsupported file type: {suffix}")

    def _pdf_to_images(self, file_path: Path) -> List[Path]:
        images: List[Path] = []
        document = fitz.open(str(file_path))
        for page_number in range(len(document)):
            page = document.load_page(page_number)
            pix = page.get_pixmap(alpha=False)
            image_path = self.temp_dir / f"{file_path.stem}_page_{page_number + 1}.png"
            pix.save(str(image_path))
            images.append(image_path)
        document.close()
        return images

    def _process_docx(self, file_path: Path) -> Dict[str, object]:
        document = Document(str(file_path))
        extracted_text = "\n".join(
            paragraph.text for paragraph in document.paragraphs if paragraph.text.strip()
        )
        image_paths: List[Path] = []
        for rel in document.part._rels.values():
            if "image" not in rel.target_ref:
                continue
            image_bytes = rel.target_part.blob
            image = Image.open(BytesIO(image_bytes)).convert("RGB")
            image_path = self.temp_dir / f"{file_path.stem}_image_{len(image_paths) + 1}.png"
            image.save(str(image_path), format="PNG")
            image_paths.append(image_path)

        return {
            "file_type": "docx",
            "extracted_text": extracted_text.strip() or None,
            "image_paths": image_paths,
            "page_count": len(image_paths),
            "image_count": len(image_paths),
        }

    @staticmethod
    def cleanup(paths: List[Path]) -> None:
        for path in paths:
            try:
                path.unlink()
            except FileNotFoundError:
                pass
