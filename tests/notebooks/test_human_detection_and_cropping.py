"""Test notebook `notebooks/01_human_detection_and_cropping.ipynb` (K1-K6) dan
`notebooks/00_pipeline_errors.ipynb`.

Notebook dijalankan lewat `testbook`, bukan diimpor sebagai modul `.py`, karena kode
inti sengaja tetap satu notebook di fase MVP ini (K6). Sel bertag "manual-run" (yang
memanggil model YOLOv8n sungguhan pada `data/raw/`, termasuk semua sel runner
"define -> demonstrate") tidak dieksekusi di sini — sesuai D4, tanda berhasil MVP
adalah notebook bisa dijalankan tanpa error, bukan pipeline pada data sungguhan.
Deteksi diuji dengan `ultralytics.YOLO` atau fungsi `detect_humans` yang di-mock, tanpa
mengunduh atau memanggil model sungguhan.
"""

from pathlib import Path

import cv2
import numpy as np
import pytest
from testbook import testbook

NOTEBOOKS_DIR = Path(__file__).resolve().parents[2] / "notebooks"
NOTEBOOK_PATH = str(NOTEBOOKS_DIR / "01_human_detection_and_cropping.ipynb")
ERRORS_NOTEBOOK_PATH = str(NOTEBOOKS_DIR / "00_pipeline_errors.ipynb")
PIPELINE_ERROR_NAMES = (
    "ImageReadError",
    "DetectionError",
    "NoDetectionError",
    "MultipleDetectionError",
    "CropTooSmallError",
    "CropSaveError",
)


@pytest.fixture(scope="module")
def tb():
    with testbook(
        NOTEBOOK_PATH, execute=True, timeout=120, skip_cells_with_tag="manual-run"
    ) as client:
        yield client


def test_errors_notebook_defines_all_pipeline_errors() -> None:
    with testbook(ERRORS_NOTEBOOK_PATH, execute=True, timeout=120) as client:
        for name in PIPELINE_ERROR_NAMES:
            client.ref(name)


def test_notebook_loads_pipeline_errors_from_errors_notebook(tb) -> None:
    for name in PIPELINE_ERROR_NAMES:
        tb.ref(name)


def test_notebook_defines_all_core_components(tb) -> None:
    for name in (
        "BoundingBox",
        "load_detector",
        "detect_humans",
        "validate_single_detection",
        "NoDetectionError",
        "MultipleDetectionError",
        "crop_with_padding",
        "save_crop",
        "CropTooSmallError",
        "build_crop_filename",
        "ProcessSummary",
        "total_skipped",
        "process_identity",
        "run_pipeline",
    ):
        tb.ref(name)


def test_detect_humans_translates_mocked_yolo_result_to_bounding_boxes(tb) -> None:
    with tb.patch("__main__.YOLO"):
        tb.inject(
            """
            from unittest.mock import MagicMock

            _fake_box = MagicMock()
            _fake_box.xyxy = [MagicMock(tolist=lambda: [1.0, 2.0, 3.0, 4.0])]
            _fake_box.conf = [0.87]
            _fake_result = MagicMock(boxes=[_fake_box])

            _model = load_detector("yolov8n.pt")
            _model.predict.return_value = [_fake_result]

            _boxes = detect_humans(_model, Path("dummy.jpg"), conf_threshold=0.5)
            assert _boxes == [BoundingBox(x1=1, y1=2, x2=3, y2=4, confidence=0.87)]
            """
        )


def test_validate_single_detection_boundary_cases(tb) -> None:
    tb.inject(
        """
        _one = [BoundingBox(x1=0, y1=0, x2=10, y2=10, confidence=0.9)]
        assert validate_single_detection(_one) is _one[0]

        try:
            validate_single_detection([])
            assert False, "harus raise NoDetectionError"
        except NoDetectionError:
            pass

        _two = _one + [BoundingBox(x1=20, y1=20, x2=30, y2=30, confidence=0.8)]
        try:
            validate_single_detection(_two)
            assert False, "harus raise MultipleDetectionError"
        except MultipleDetectionError:
            pass
        """
    )


def test_crop_with_padding_applies_padding_and_rejects_small_crop(tb) -> None:
    tb.inject(
        """
        _image = np.zeros((100, 100, 3), dtype=np.uint8)
        _box = BoundingBox(x1=40, y1=40, x2=60, y2=60, confidence=0.9)

        _region = crop_with_padding(_image, _box, padding_ratio=0.5, min_side_px=30)
        assert _region.shape[:2] == (40, 40)

        try:
            crop_with_padding(_image, _box, padding_ratio=0.5, min_side_px=50)
            assert False, "harus raise CropTooSmallError"
        except CropTooSmallError:
            pass
        """
    )


def test_build_crop_filename_derived_from_source_name(tb) -> None:
    tb.inject(
        """
        assert build_crop_filename(Path("foto1.jpg")) == "foto1_person.jpg"
        assert build_crop_filename(Path("/a/b/pink-chan.png")) == "pink-chan_person.jpg"
        """
    )


def test_total_skipped_sums_all_skip_categories(tb) -> None:
    tb.inject(
        """
        _summary = ProcessSummary(
            cropped=5,
            skipped_no_detection=1,
            skipped_multiple_detection=2,
            skipped_too_small=3,
            skipped_unreadable=4,
        )
        assert total_skipped(_summary) == 10
        """
    )


def _write_synthetic_image(path: Path) -> None:
    image = np.zeros((100, 100, 3), dtype=np.uint8)
    cv2.imwrite(str(path), image)


def test_process_identity_skips_problematic_images_and_crops_valid_ones(
    tb, tmp_path: Path
) -> None:
    identity_dir = tmp_path / "identity"
    output_dir = tmp_path / "cropped"
    identity_dir.mkdir()

    for name in ("valid.jpg", "no_person.jpg", "two_person.jpg", "too_small.jpg"):
        _write_synthetic_image(identity_dir / name)

    code = """
        import unittest.mock

        _boxes_by_name = {
            "valid.jpg": [BoundingBox(x1=10, y1=10, x2=90, y2=90, confidence=0.9)],
            "no_person.jpg": [],
            "two_person.jpg": [
                BoundingBox(x1=0, y1=0, x2=10, y2=10, confidence=0.9),
                BoundingBox(x1=20, y1=20, x2=30, y2=30, confidence=0.9),
            ],
            "too_small.jpg": [BoundingBox(x1=0, y1=0, x2=2, y2=2, confidence=0.9)],
        }

        def _fake_detect_humans(model, image_path, conf_threshold):
            return _boxes_by_name[Path(image_path).name]

        with unittest.mock.patch("__main__.detect_humans", side_effect=_fake_detect_humans):
            _summary = process_identity(
                Path(IDENTITY_DIR), Path(OUTPUT_DIR), None, 0.5, 0.0, 10
            )

        assert _summary.cropped == 1
        assert _summary.skipped_no_detection == 1
        assert _summary.skipped_multiple_detection == 1
        assert _summary.skipped_too_small == 1
        assert sorted(p.name for p in Path(OUTPUT_DIR).iterdir()) == ["valid_person.jpg"]
    """
    code = code.replace("IDENTITY_DIR", repr(str(identity_dir))).replace(
        "OUTPUT_DIR", repr(str(output_dir))
    )
    tb.inject(code)


def test_rerun_on_same_data_overwrites_instead_of_duplicating(tb, tmp_path: Path) -> None:
    identity_dir = tmp_path / "identity_rerun"
    output_dir = tmp_path / "cropped_rerun"
    identity_dir.mkdir()
    _write_synthetic_image(identity_dir / "valid.jpg")

    code = """
        import unittest.mock

        def _fake_detect_humans(model, image_path, conf_threshold):
            return [BoundingBox(x1=10, y1=10, x2=90, y2=90, confidence=0.9)]

        with unittest.mock.patch("__main__.detect_humans", side_effect=_fake_detect_humans):
            process_identity(Path(IDENTITY_DIR), Path(OUTPUT_DIR), None, 0.5, 0.0, 10)
            process_identity(Path(IDENTITY_DIR), Path(OUTPUT_DIR), None, 0.5, 0.0, 10)

        _output_files = list(Path(OUTPUT_DIR).iterdir())
        assert [p.name for p in _output_files] == ["valid_person.jpg"]
    """
    code = code.replace("IDENTITY_DIR", repr(str(identity_dir))).replace(
        "OUTPUT_DIR", repr(str(output_dir))
    )
    tb.inject(code)
