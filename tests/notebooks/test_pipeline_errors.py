"""Test `notebooks/00_pipeline_errors.ipynb`.

Notebook ini dimuat lewat `%run` oleh `01_human_detection_and_cropping.ipynb` dan
`02_face_upper_lower_body_detection_and_cropping.ipynb`, jadi didefinisikan dan diuji
terpisah dari kedua notebook itu.
"""

from pathlib import Path

from testbook import testbook

NOTEBOOK_PATH = str(Path(__file__).resolve().parents[2] / "notebooks" / "00_pipeline_errors.ipynb")
PIPELINE_ERROR_NAMES = (
    "ImageReadError",
    "DetectionError",
    "NoDetectionError",
    "MultipleDetectionError",
    "CropTooSmallError",
    "CropSaveError",
    "FaceDetectionError",
    "NoFaceDetectedError",
    "MultipleFaceDetectedError",
    "PoseDetectionError",
    "NoPersonPoseDetectedError",
    "MultiplePersonPoseDetectedError",
    "InsufficientKeypointsError",
)


def test_errors_notebook_defines_all_pipeline_errors() -> None:
    with testbook(NOTEBOOK_PATH, execute=True, timeout=120) as client:
        for name in PIPELINE_ERROR_NAMES:
            client.ref(name)
