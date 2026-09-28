"""Test notebook `notebooks/02_face_detection_and_cropping.ipynb` (K8, K13-K16) dan
`notebooks/00_pipeline_errors.ipynb`.

Notebook dijalankan lewat `testbook`, bukan diimpor sebagai modul `.py`, karena kode
inti sengaja tetap satu notebook per tahap (K6/K16). Sel bertag "manual-run" (yang
memanggil model InsightFace sungguhan pada `data/cropped/`, termasuk semua sel runner
"define -> demonstrate") tidak dieksekusi di sini. Deteksi wajah diuji dengan
`insightface.app.FaceAnalysis` atau fungsi `detect_faces` yang di-mock, tanpa mengunduh
atau memanggil model sungguhan.
"""

from pathlib import Path

import cv2
import numpy as np
import pytest
from testbook import testbook

NOTEBOOKS_DIR = Path(__file__).resolve().parents[2] / "notebooks"
NOTEBOOK_PATH = str(NOTEBOOKS_DIR / "02_face_detection_and_cropping.ipynb")
PIPELINE_ERROR_NAMES = (
    "ImageReadError",
    "FaceDetectionError",
    "NoFaceDetectedError",
    "CropTooSmallError",
    "CropSaveError",
)


@pytest.fixture(scope="module")
def tb():
    with testbook(
        NOTEBOOK_PATH, execute=True, timeout=120, skip_cells_with_tag="manual-run"
    ) as client:
        yield client


def test_notebook_loads_pipeline_errors_from_errors_notebook(tb) -> None:
    for name in PIPELINE_ERROR_NAMES:
        tb.ref(name)


def test_notebook_defines_all_core_components(tb) -> None:
    for name in (
        "BoundingBox",
        "load_face_analyzer",
        "detect_faces",
        "validate_single_face",
        "NoFaceDetectedError",
        "crop_with_padding",
        "save_crop",
        "CropTooSmallError",
        "build_crop_filename",
        "RegionOutcome",
        "RegionSummary",
        "total_skipped",
        "ProcessSummary",
        "process_image",
        "process_identity",
        "run_pipeline",
    ):
        tb.ref(name)


def test_detect_faces_translates_mocked_insightface_result_to_bounding_boxes(tb) -> None:
    tb.inject(
        """
        from unittest.mock import MagicMock

        _fake_face = MagicMock()
        _fake_face.bbox = [1.0, 2.0, 3.0, 4.0]
        _fake_face.det_score = 0.87
        _fake_analyzer = MagicMock()
        _fake_analyzer.get.return_value = [_fake_face]

        _boxes = detect_faces(_fake_analyzer, np.zeros((10, 10, 3), dtype=np.uint8))
        assert _boxes == [BoundingBox(x1=1, y1=2, x2=3, y2=4, confidence=0.87)]
        """
    )


def test_validate_single_face_selects_highest_confidence(tb) -> None:
    tb.inject(
        """
        _one = [BoundingBox(x1=0, y1=0, x2=10, y2=10, confidence=0.9)]
        assert validate_single_face(_one) is _one[0]

        try:
            validate_single_face([])
            assert False, "harus raise NoFaceDetectedError"
        except NoFaceDetectedError:
            pass

        _lower_confidence = BoundingBox(x1=20, y1=20, x2=30, y2=30, confidence=0.8)
        assert validate_single_face(_one + [_lower_confidence]) is _one[0]

        _higher_confidence = BoundingBox(x1=30, y1=30, x2=40, y2=40, confidence=0.95)
        assert validate_single_face(_one + [_higher_confidence]) is _higher_confidence
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
        assert build_crop_filename(Path("foto1.jpg")) == "foto1_face.jpg"
        assert build_crop_filename(Path("/a/b/pink-chan.png")) == "pink-chan_face.jpg"
        assert build_crop_filename(Path("foto1.jpg"), suffix="custom") == "foto1_custom.jpg"
        """
    )


def test_region_summary_add_and_total_skipped_sums_all_skip_categories(tb) -> None:
    tb.inject(
        """
        _summary = RegionSummary()
        _summary.add(RegionOutcome.CROPPED)
        _summary.add(RegionOutcome.CROPPED)
        _summary.add(RegionOutcome.SKIPPED_NO_DETECTION)
        _summary.add(RegionOutcome.SKIPPED_TOO_SMALL)
        _summary.add(RegionOutcome.SKIPPED_TOO_SMALL)
        _summary.add(RegionOutcome.SKIPPED_UNREADABLE)

        assert _summary.cropped == 2
        assert _summary.skipped_no_detection == 1
        assert _summary.skipped_too_small == 2
        assert _summary.skipped_unreadable == 1
        assert total_skipped(_summary) == 4
        """
    )


def _write_synthetic_image(path: Path, fill_value: int = 0) -> None:
    # PNG (lossless) supaya nilai pixel yang dipakai untuk membedakan gambar di
    # fake detect_faces tidak berubah akibat kompresi JPEG.
    image = np.full((100, 100, 3), fill_value, dtype=np.uint8)
    cv2.imwrite(str(path), image)


def test_process_identity_skips_problematic_images_and_crops_valid_ones(
    tb, tmp_path: Path
) -> None:
    identity_dir = tmp_path / "identity"
    face_dir = tmp_path / "face"
    identity_dir.mkdir()

    _write_synthetic_image(identity_dir / "valid.png", fill_value=10)
    _write_synthetic_image(identity_dir / "no_face.png", fill_value=20)
    _write_synthetic_image(identity_dir / "too_small.png", fill_value=30)
    (identity_dir / "broken.jpg").write_bytes(b"not an image")

    code = """
        import unittest.mock

        _boxes_by_fill_value = {
            10: [BoundingBox(x1=10, y1=10, x2=90, y2=90, confidence=0.9)],
            20: [],
            30: [BoundingBox(x1=0, y1=0, x2=2, y2=2, confidence=0.9)],
        }

        def _fake_detect_faces(analyzer, image):
            return _boxes_by_fill_value[int(image[0, 0, 0])]

        with unittest.mock.patch("__main__.detect_faces", side_effect=_fake_detect_faces):
            _summary = process_identity(
                Path(IDENTITY_DIR), Path(FACE_DIR), None, 0.5, 10
            )

        assert _summary.face.cropped == 1
        assert _summary.face.skipped_no_detection == 1
        assert _summary.face.skipped_too_small == 1
        assert _summary.face.skipped_unreadable == 1
        assert sorted(p.name for p in Path(FACE_DIR).iterdir()) == ["valid_face.jpg"]
    """
    code = code.replace("IDENTITY_DIR", repr(str(identity_dir))).replace(
        "FACE_DIR", repr(str(face_dir))
    )
    tb.inject(code)


def test_rerun_on_same_data_overwrites_instead_of_duplicating(tb, tmp_path: Path) -> None:
    identity_dir = tmp_path / "identity_rerun"
    face_dir = tmp_path / "face_rerun"
    identity_dir.mkdir()
    _write_synthetic_image(identity_dir / "valid.png", fill_value=10)

    code = """
        import unittest.mock

        def _fake_detect_faces(analyzer, image):
            return [BoundingBox(x1=10, y1=10, x2=90, y2=90, confidence=0.9)]

        with unittest.mock.patch("__main__.detect_faces", side_effect=_fake_detect_faces):
            process_identity(Path(IDENTITY_DIR), Path(FACE_DIR), None, 0.5, 10)
            process_identity(Path(IDENTITY_DIR), Path(FACE_DIR), None, 0.5, 10)

        _output_files = list(Path(FACE_DIR).iterdir())
        assert [p.name for p in _output_files] == ["valid_face.jpg"]
    """
    code = code.replace("IDENTITY_DIR", repr(str(identity_dir))).replace(
        "FACE_DIR", repr(str(face_dir))
    )
    tb.inject(code)
