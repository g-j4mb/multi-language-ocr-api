# Multi-language OCR API

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)](https://fastapi.tiangolo.com/)
[![PaddleOCR](https://img.shields.io/badge/PaddleOCR-2.7.0-orange.svg)](https://github.com/PaddlePaddle/PaddleOCR)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A high-performance, production-ready FastAPI service for multilingual text recognition using PaddleOCR with intelligent model escalation and multi-format document processing.

## 🚀 Features

- **Multilingual Support**: Specialized models for accurate recognition across multiple languages
- **Multi-Format Processing**: Supports images, PDFs, and Word documents (.docx)
- **Intelligent Model Escalation**: Automatically switches to more accurate models when confidence is low
- **Language Detection**: Automatically detects the language of extracted text
- **RESTful API**: Clean, documented endpoints with OpenAPI/Swagger support
- **Batch Processing**: Process multiple files simultaneously
- **Configurable Thresholds**: Adjustable confidence thresholds for model escalation
- **Comprehensive Testing**: Full unit test coverage with pytest
- **Production Ready**: Error handling, logging, and proper resource management

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [API Documentation](#api-documentation)
- [Configuration](#configuration)
- [Testing](#testing)
- [Development](#development)
- [Project Structure](#project-structure)
- [Docker](#docker)
- [CI/CD](#ci-cd)
- [Contributing](#contributing)
- [Changelog](#changelog)
- [License](#license)

## 🛠 Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- (Optional) Docker for containerized deployment

### Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/g-j4mb/multi-language-ocr-api.git
   cd multi-language-ocr-api
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Docker Setup

Alternatively, use Docker for a containerized setup:

```bash
# Build the image
make docker-build

# Run the container
make docker-run
```

## 🚀 Quick Start

1. **Start the API server:**
   ```bash
   python api.py
   # Or using make: make run
   ```

2. **Access the API:**
   - **Swagger UI**: http://localhost:8000/docs
   - **ReDoc**: http://localhost:8000/redoc
   - **Health Check**: http://localhost:8000/health

3. **Test with a sample image:**
   ```bash
   curl -X POST "http://localhost:8000/ocr/predict" \
     -F "file=@sample_image.png"
   ```

## 📚 API Documentation

### Endpoints

#### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "ok",
  "service": "Multi-language OCR API",
  "version": "2.0.0"
}
```

#### Single File OCR Prediction
```http
POST /ocr/predict
```

**Parameters:**
- `file` (required): Image, PDF, or Word document file
- `confidence_threshold` (optional): Float between 0.0-1.0, default 0.75

**Parameters:**
- `file` (required): Image, PDF, or Word document file
- `confidence_threshold` (optional): Float between 0.0-1.0, default 0.75
- `lang` (optional): OCR language code, e.g. `ar`, `fa`, `tr`, `en`. Use `auto` to detect language from extracted text.

**Response:**
```json
{
  "filename": "document.pdf",
  "file_type": "pdf",
  "language": "ar",
  "language_confidence": 0.98,
  "model_used": "basic",
  "escalated": false,
  "total_predictions": 15,
  "average_confidence": 0.89,
  "extracted_text": null,
  "predictions": [
    {
      "text": "النص العربي",
      "confidence": 0.95
    }
  ]
}
```

#### Batch File OCR Prediction
```http
POST /ocr/predict-batch
```

**Parameters:**
- `files` (required): Multiple files as multipart form data
- `confidence_threshold` (optional): Float between 0.0-1.0, default 0.75
- `lang` (optional): OCR language code, e.g. `ar`, `fa`, `tr`, `en`. Use `auto` to detect language from extracted text.

**Response:** Array of single file responses

### Supported File Formats

- **Images**: PNG, JPG, JPEG, BMP, TIFF
- **Documents**: PDF, DOCX

### Model Escalation

The API uses a two-tier model system:

1. **Basic Model**: Fast, lightweight mobile models for initial processing
2. **Escalated Model**: More accurate server models when confidence is below threshold

Escalation occurs when:
- Average confidence < `confidence_threshold`
- No words are recognized

## ⚙️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OCR_DEVICE` | `cpu` | Device for OCR processing (`cpu` or `gpu`) |
| `OCR_TEXT_DET_LIMIT_SIDE_LEN` | `960` | Maximum image dimension for processing |

### Model Configuration

The service automatically downloads required models on first use:
- PP-OCRv5 Mobile Detection
- Arabic-specific PP-OCRv5 mobile recognition override
- PP-OCRv5 Server models (for escalation)

## 🧪 Testing

### Run Unit Tests

```bash
# Using pytest directly
.venv\Scripts\python.exe -m pytest tests/test_api.py

# Or with verbose output
.venv\Scripts\python.exe -m pytest tests/test_api.py -v

# Or using make
make test
```

### Test Coverage

```bash
# Run tests with coverage report
make test-coverage
```

The test suite covers:
- Language detection functionality
- File processing for different formats
- OCR model escalation logic
- API endpoint responses
- Error handling scenarios

### Integration Testing

Use the provided client script for manual testing:

```bash
python client.py
```

## 📁 Project Structure

```
multi-language-ocr-api/
├── api.py                 # Main FastAPI application
├── file_processors.py     # Document processing utilities
├── language_detector.py   # Language detection service
├── ocr_service.py         # OCR model management and escalation
├── schemas.py             # Pydantic data models
├── client.py              # Example API client
├── requirements.txt       # Python dependencies
├── pytest.ini            # Test configuration
├── Makefile              # Development automation
├── Dockerfile            # Docker container definition
├── .dockerignore         # Docker ignore patterns
├── .github/
│   └── workflows/
│       └── ci-cd.yml     # GitHub Actions CI/CD pipeline
├── tests/
│   └── test_api.py       # Unit tests
├── output/               # Generated output directory
├── CONTRIBUTING.md       # Contribution guidelines
├── CHANGELOG.md          # Version history
├── LICENSE               # MIT license
└── README.md             # This file
```

## 🐳 Docker

### Build and Run

```bash
# Build the Docker image
docker build -t multi-language-ocr-api .

# Run the container
docker run -p 8000:8000 multi-language-ocr-api
```

### Using Makefile

```bash
# Build Docker image
make docker-build

# Run Docker container
make docker-run
```

## � CI/CD

This project uses GitHub Actions for continuous integration and deployment. The CI/CD pipeline includes:

- **Automated Testing**: Runs unit tests on every push and pull request
- **Code Quality**: Linting, formatting, and type checking
- **Docker Build**: Ensures the Docker image builds successfully
- **Coverage Reports**: Generates test coverage reports

### Pipeline Status

[![CI/CD](https://github.com/g-j4mb/multi-language-ocr-api/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/g-j4mb/multi-language-ocr-api/actions/workflows/ci-cd.yml)

## �🛠 Development

### Prerequisites

- Python 3.8+
- pip
- (Optional) Docker

### Setup Development Environment

```bash
# Install all dependencies including dev tools
make install
make dev-setup

# Run pre-commit hooks (if configured)
pre-commit install
```

### Code Quality

```bash
# Run linting
make lint

# Format code
make format

# Check formatting
make check-format

# Run type checking
make type-check
```

### Testing

```bash
# Run unit tests
make test

# Run tests with coverage
make test-coverage
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Development Setup

```bash
# Install development dependencies
make dev-setup

# Run linting
make lint

# Format code
make format

# Run type checking
make type-check

# Clean up generated files
make clean
```

## � Changelog

See [CHANGELOG.md](CHANGELOG.md) for a detailed list of changes and version history.

## �📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [PaddlePaddle](https://github.com/PaddlePaddle/PaddleOCR) for the excellent OCR engine
- [FastAPI](https://fastapi.tiangolo.com/) for the web framework
- [langdetect](https://pypi.org/project/langdetect/) for language detection

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/g-j4mb/multi-language-ocr-api/issues) page
2. Create a new issue with detailed information
3. Include sample files and error messages when possible

## 🔄 Changelog

### Version 2.0.0
- Added multi-format document support (PDF, DOCX)
- Implemented intelligent model escalation
- Added language detection
- Enhanced API with comprehensive error handling
- Added full unit test coverage

### Version 1.0.0
- Initial release with basic multilingual OCR functionality
- FastAPI-based REST API
- Single image processing support
