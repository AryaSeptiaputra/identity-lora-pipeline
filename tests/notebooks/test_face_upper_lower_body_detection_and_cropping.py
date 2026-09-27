"""Test notebook `notebooks/02_face_upper_lower_body_detection_and_cropping.ipynb`
(K7-K16) dan `notebooks/00_pipeline_errors.ipynb`.

Notebook dijalankan lewat `testbook`, bukan diimpor sebagai modul `.py`, karena kode
inti sengaja tetap satu notebook per modul di fase MVP ini (K16, konsisten K6). Sel
bertag "manual-run" (yang memanggil model InsightFace/DWPose sungguhan pada
`data/cropped/`, termasuk semua sel runner "define -> demonstrate") tidak dieksekusi
di sini — sesuai D4, tanda berhasil MVP adalah notebook bisa dijalankan tanpa error,
bukan pipeline pada data sungguhan. Deteksi diuji dengan `FaceAnalysis`/`Wholebody`
(rtmlib) yang di-mock, tanpa mengunduh atau memanggil model sungguhan. K9 (revisi
rancangan 003): `load_pose_detector` diuji dengan `onnxruntime.get_available_providers`
di-mock, termasuk kasus GPU tidak tersedia (`GPUNotAvailableError`, gagal keras, tidak
fallback CPU).
"""

from pathlib import Path

import cv2
import numpy as np
import pytest
from testbook import testbook

NOTEBOOKS_DIR = Path(__file__).resolve().parents[2] / "notebooks"
NOTEBOOK_PATH = str(NOTEBOOKS_DIR / "02_face_upper_lower_body_detection_and_cropping.ipynb")
PIPELINE_ERROR_NAMES = (
    "FaceDetectionError",
    "NoFaceDetectedError",
    "MultipleFaceDetectedError",
    "PoseDetectionError",
    "NoPersonPoseDetectedError",
    "MultiplePersonPoseDetectedError",
    "InsufficientKeypointsError",
    "GPUNotAvailableError",
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


def test_notebook_defines_face_detection_components(tb) -> None:
    for name in (
        "BoundingBox",
        "load_face_analyzer",
        "detect_faces",
        "validate_single_face",
    ):
        tb.ref(name)


def test_detect_faces_translates_mocked_face_analysis_result_to_bounding_boxes(tb) -> None:
    with tb.patch("__main__.FaceAnalysis"):
        tb.inject(
            """
            from unittest.mock import MagicMock
            import numpy as np

            _fake_face = MagicMock()
            _fake_face.bbox = np.array([1.0, 2.0, 3.0, 4.0])
            _fake_face.det_score = 0.93

            _analyzer = load_face_analyzer("buffalo_sc", 0.5)
            _analyzer.get.return_value = [_fake_face]

            _boxes = detect_faces(_analyzer, np.zeros((10, 10, 3), dtype=np.uint8))
            assert _boxes == [BoundingBox(x1=1, y1=2, x2=3, y2=4, confidence=0.93)]
            """
        )


def test_validate_single_face_boundary_cases(tb) -> None:
    tb.inject(
        """
        _one = [BoundingBox(x1=0, y1=0, x2=10, y2=10, confidence=0.9)]
        assert validate_single_face(_one) is _one[0]

        try:
            validate_single_face([])
            assert False, "harus raise NoFaceDetectedError"
        except NoFaceDetectedError:
            pass

        _two = _one + [BoundingBox(x1=20, y1=20, x2=30, y2=30, confidence=0.8)]
        try:
            validate_single_face(_two)
            assert False, "harus raise MultipleFaceDetectedError"
        except MultipleFaceDetectedError:
            pass
        """
    )


def test_notebook_defines_pose_and_keypoint_components(tb) -> None:
    for name in (
        "load_pose_detector",
        "detect_pose",
        "validate_single_person_pose",
        "UPPER_KEYPOINT_INDICES",
        "LOWER_KEYPOINT_INDICES",
        "UPPER_ANCHOR_INDICES",
        "LOWER_ANCHOR_INDICES",
        "derive_body_part_bbox",
    ):
        tb.ref(name)


def test_load_pose_detector_raises_when_cuda_not_available(tb) -> None:
    # K9 (revisi rancangan 003): GPU wajib, tidak fallback CPU (koreksi Arya,
    # titik periksa 10) — verifikasi eksplisit sebelum memuat model.
    with tb.patch("__main__.ort.get_available_providers", return_value=["CPUExecutionProvider"]):
        tb.inject(
            """
            try:
                load_pose_detector("balanced", "cuda")
                assert False, "harus raise GPUNotAvailableError"
            except GPUNotAvailableError:
                pass
            """
        )


def test_load_pose_detector_constructs_wholebody_when_cuda_available(tb) -> None:
    with (
        tb.patch(
            "__main__.ort.get_available_providers",
            return_value=["CUDAExecutionProvider", "CPUExecutionProvider"],
        ),
        tb.patch("__main__.Wholebody"),
    ):
        tb.inject(
            """
            _model = load_pose_detector("balanced", "cuda")
            Wholebody.assert_called_once_with(mode="balanced", backend="onnxruntime", device="cuda")
            assert _model is Wholebody.return_value
            """
        )


def test_detect_pose_translates_mocked_wholebody_result_to_keypoint_arrays(tb) -> None:
    tb.inject(
        """
        from unittest.mock import MagicMock
        import numpy as np

        _fake_keypoints = np.zeros((1, 133, 2))
        _fake_scores = np.zeros((1, 133))
        _fake_keypoints[0, 5] = (10.0, 20.0)
        _fake_scores[0, 5] = 0.9

        _model = MagicMock(return_value=(_fake_keypoints, _fake_scores))

        _people = detect_pose(_model, np.zeros((10, 10, 3), dtype=np.uint8))
        assert len(_people) == 1
        assert _people[0].shape == (17, 3)
        assert tuple(_people[0][5]) == (10.0, 20.0, 0.9)
        """
    )


def test_validate_single_person_pose_boundary_cases(tb) -> None:
    tb.inject(
        """
        import numpy as np

        _one_person = np.zeros((17, 3))
        assert validate_single_person_pose([_one_person]) is _one_person

        try:
            validate_single_person_pose([])
            assert False, "harus raise NoPersonPoseDetectedError"
        except NoPersonPoseDetectedError:
            pass

        try:
            validate_single_person_pose([_one_person, _one_person])
            assert False, "harus raise MultiplePersonPoseDetectedError"
        except MultiplePersonPoseDetectedError:
            pass
        """
    )


def test_derive_body_part_bbox_valid_group_computes_bbox_from_passing_points(tb) -> None:
    tb.inject(
        f"""
        import numpy as np

        _keypoints = np.zeros((17, 3))
        for _i in {sorted({5, 6, 7})}:
            _keypoints[_i] = (float(_i), float(_i), 0.9)

        _box = derive_body_part_bbox(_keypoints, UPPER_KEYPOINT_INDICES, UPPER_ANCHOR_INDICES, 0.5)
        assert (_box.x1, _box.y1, _box.x2, _box.y2) == (5, 5, 7, 7)
        assert _box.confidence == 0.9
        """
    )
    tb.inject(
        f"""
        import numpy as np

        _keypoints = np.zeros((17, 3))
        for _i in {sorted({11, 13, 14})}:
            _keypoints[_i] = (float(_i), float(_i), 0.9)

        _box = derive_body_part_bbox(_keypoints, LOWER_KEYPOINT_INDICES, LOWER_ANCHOR_INDICES, 0.5)
        assert (_box.x1, _box.y1, _box.x2, _box.y2) == (11, 11, 14, 14)
        """
    )


def test_derive_body_part_bbox_raises_when_anchor_missing(tb) -> None:
    tb.inject(
        f"""
        import numpy as np

        # cukup 2+ titik total, tapi tidak ada anchor bahu (5, 6)
        _keypoints = np.zeros((17, 3))
        for _i in {sorted({7, 8, 9})}:
            _keypoints[_i] = (float(_i), float(_i), 0.9)

        try:
            derive_body_part_bbox(_keypoints, UPPER_KEYPOINT_INDICES, UPPER_ANCHOR_INDICES, 0.5)
            assert False, "harus raise InsufficientKeypointsError"
        except InsufficientKeypointsError:
            pass
        """
    )


def test_notebook_defines_cropping_and_orchestration_components(tb) -> None:
    for name in (
        "crop_with_padding",
        "save_crop",
        "build_crop_filename",
        "RegionOutcome",
        "RegionSummary",
        "ProcessSummary",
        "total_skipped",
        "process_image",
        "process_identity",
        "run_pipeline",
    ):
        tb.ref(name)


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


def test_build_crop_filename_derived_from_source_name_with_suffix(tb) -> None:
    tb.inject(
        """
        assert build_crop_filename(Path("foto1.jpg"), "face") == "foto1_face.jpg"
        assert build_crop_filename(Path("foto1.jpg"), "upper") == "foto1_upper.jpg"
        assert build_crop_filename(Path("foto1.jpg"), "lower") == "foto1_lower.jpg"
        assert build_crop_filename(Path("/a/b/pink-chan.png"), "face") == "pink-chan_face.jpg"
        """
    )


def test_total_skipped_sums_all_skip_categories(tb) -> None:
    tb.inject(
        """
        _summary = RegionSummary(
            cropped=5,
            skipped_no_detection=1,
            skipped_multiple_detection=2,
            skipped_insufficient_keypoints=3,
            skipped_too_small=4,
            skipped_unreadable=5,
        )
        assert total_skipped(_summary) == 15
        """
    )


def _write_synthetic_image(path: Path) -> None:
    image = np.zeros((100, 100, 3), dtype=np.uint8)
    cv2.imwrite(str(path), image)


def test_process_image_treats_face_and_body_parts_independently(tb, tmp_path: Path) -> None:
    readable_path = tmp_path / "photo.jpg"
    _write_synthetic_image(readable_path)
    unreadable_path = tmp_path / "broken.jpg"
    unreadable_path.write_bytes(b"not an image")
    face_dir = tmp_path / "face"
    upper_dir = tmp_path / "upper"
    lower_dir = tmp_path / "lower"

    code = """
        import unittest.mock

        import numpy as np

        _valid_keypoints = np.zeros((17, 3))
        _valid_keypoints[5] = (10.0, 10.0, 0.9)
        _valid_keypoints[6] = (30.0, 30.0, 0.9)
        _valid_keypoints[11] = (10.0, 10.0, 0.9)
        _valid_keypoints[12] = (30.0, 30.0, 0.9)
        _upper_only_keypoints = np.zeros((17, 3))
        _upper_only_keypoints[5] = (10.0, 10.0, 0.9)
        _upper_only_keypoints[6] = (30.0, 30.0, 0.9)

        _face_box = [BoundingBox(x1=10, y1=10, x2=90, y2=90, confidence=0.9)]

        # Kasus 1: wajah berhasil, pose gagal (tidak ada orang) -> upper/lower
        # dilewati, wajah tetap tersimpan (K12).
        with (
            unittest.mock.patch("__main__.detect_faces", return_value=_face_box),
            unittest.mock.patch("__main__.detect_pose", return_value=[]),
        ):
            _face, _upper, _lower = process_image(
                Path(IMG_OK_PATH), Path(FACE_DIR), Path(UPPER_DIR), Path(LOWER_DIR),
                None, None, 0.0, 10, 0.5,
            )
        assert _face == RegionOutcome.CROPPED
        assert _upper == RegionOutcome.SKIPPED_NO_DETECTION
        assert _lower == RegionOutcome.SKIPPED_NO_DETECTION
        assert (Path(FACE_DIR) / build_crop_filename(Path(IMG_OK_PATH), "face")).exists()

        # Kasus 2: wajah gagal (tidak ada wajah), pose berhasil untuk kedua grup ->
        # wajah dilewati, upper dan lower tetap tersimpan (K12).
        with (
            unittest.mock.patch("__main__.detect_faces", return_value=[]),
            unittest.mock.patch("__main__.detect_pose", return_value=[_valid_keypoints]),
        ):
            _face, _upper, _lower = process_image(
                Path(IMG_OK_PATH), Path(FACE_DIR), Path(UPPER_DIR), Path(LOWER_DIR),
                None, None, 0.0, 10, 0.5,
            )
        assert _face == RegionOutcome.SKIPPED_NO_DETECTION
        assert _upper == RegionOutcome.CROPPED
        assert _lower == RegionOutcome.CROPPED

        # Kasus 3: wajah dan upper berhasil, lower dilewati karena keypoint tidak
        # cukup -> upper dan lower independen satu sama lain (K12).
        with (
            unittest.mock.patch("__main__.detect_faces", return_value=_face_box),
            unittest.mock.patch("__main__.detect_pose", return_value=[_upper_only_keypoints]),
        ):
            _face, _upper, _lower = process_image(
                Path(IMG_OK_PATH), Path(FACE_DIR), Path(UPPER_DIR), Path(LOWER_DIR),
                None, None, 0.0, 10, 0.5,
            )
        assert _face == RegionOutcome.CROPPED
        assert _upper == RegionOutcome.CROPPED
        assert _lower == RegionOutcome.SKIPPED_INSUFFICIENT_KEYPOINTS

        # Kasus 4: gambar tidak bisa dibaca -> ketiga jenis dilewati.
        _face, _upper, _lower = process_image(
            Path(IMG_BAD_PATH), Path(FACE_DIR), Path(UPPER_DIR), Path(LOWER_DIR),
            None, None, 0.0, 10, 0.5,
        )
        assert _face == RegionOutcome.SKIPPED_UNREADABLE
        assert _upper == RegionOutcome.SKIPPED_UNREADABLE
        assert _lower == RegionOutcome.SKIPPED_UNREADABLE
    """
    code = (
        code.replace("IMG_OK_PATH", repr(str(readable_path)))
        .replace("IMG_BAD_PATH", repr(str(unreadable_path)))
        .replace("FACE_DIR", repr(str(face_dir)))
        .replace("UPPER_DIR", repr(str(upper_dir)))
        .replace("LOWER_DIR", repr(str(lower_dir)))
    )
    tb.inject(code)


def test_process_identity_creates_output_dirs_and_aggregates_region_summaries(
    tb, tmp_path: Path
) -> None:
    identity_dir = tmp_path / "identity"
    face_dir = tmp_path / "face"
    upper_dir = tmp_path / "upper"
    lower_dir = tmp_path / "lower"
    identity_dir.mkdir()
    _write_synthetic_image(identity_dir / "valid.jpg")
    _write_synthetic_image(identity_dir / "no_detection.jpg")

    code = """
        import unittest.mock

        import numpy as np

        _valid_keypoints = np.zeros((17, 3))
        _valid_keypoints[5] = (10.0, 10.0, 0.9)
        _valid_keypoints[6] = (30.0, 30.0, 0.9)
        _valid_keypoints[11] = (10.0, 10.0, 0.9)
        _valid_keypoints[12] = (30.0, 30.0, 0.9)

        def _fake_detect_faces(analyzer, image):
            return [BoundingBox(x1=10, y1=10, x2=90, y2=90, confidence=0.9)]

        # _list_images mengurutkan berkas secara alfabetis, jadi "no_detection.jpg"
        # dipanggil lebih dulu ([]), lalu "valid.jpg" ([_valid_keypoints]). detect_pose
        # (K9 revisi) tidak lagi menerima path (hanya image array), jadi dibedakan lewat
        # urutan panggilan, bukan nama berkas.
        with (
            unittest.mock.patch("__main__.detect_faces", side_effect=_fake_detect_faces),
            unittest.mock.patch("__main__.detect_pose", side_effect=[[], [_valid_keypoints]]),
        ):
            _summary = process_identity(
                Path(IDENTITY_DIR), Path(FACE_DIR), Path(UPPER_DIR), Path(LOWER_DIR),
                None, None, 0.0, 10, 0.5,
            )

        assert Path(FACE_DIR).is_dir() and Path(UPPER_DIR).is_dir() and Path(LOWER_DIR).is_dir()
        assert _summary.face.cropped == 2
        assert _summary.upper_body.cropped == 1
        assert _summary.upper_body.skipped_no_detection == 1
        assert _summary.lower_body.cropped == 1
        assert _summary.lower_body.skipped_no_detection == 1
        assert sorted(p.name for p in Path(FACE_DIR).iterdir()) == [
            "no_detection_face.jpg",
            "valid_face.jpg",
        ]
        assert sorted(p.name for p in Path(UPPER_DIR).iterdir()) == ["valid_upper.jpg"]
        assert sorted(p.name for p in Path(LOWER_DIR).iterdir()) == ["valid_lower.jpg"]
    """
    code = (
        code.replace("IDENTITY_DIR", repr(str(identity_dir)))
        .replace("FACE_DIR", repr(str(face_dir)))
        .replace("UPPER_DIR", repr(str(upper_dir)))
        .replace("LOWER_DIR", repr(str(lower_dir)))
    )
    tb.inject(code)


def test_rerun_on_same_data_overwrites_instead_of_duplicating(tb, tmp_path: Path) -> None:
    identity_dir = tmp_path / "identity_rerun"
    face_dir = tmp_path / "face_rerun"
    upper_dir = tmp_path / "upper_rerun"
    lower_dir = tmp_path / "lower_rerun"
    identity_dir.mkdir()
    _write_synthetic_image(identity_dir / "valid.jpg")

    code = """
        import unittest.mock

        import numpy as np

        _valid_keypoints = np.zeros((17, 3))
        _valid_keypoints[5] = (10.0, 10.0, 0.9)
        _valid_keypoints[6] = (30.0, 30.0, 0.9)
        _valid_keypoints[11] = (10.0, 10.0, 0.9)
        _valid_keypoints[12] = (30.0, 30.0, 0.9)

        with (
            unittest.mock.patch(
                "__main__.detect_faces",
                return_value=[BoundingBox(x1=10, y1=10, x2=90, y2=90, confidence=0.9)],
            ),
            unittest.mock.patch("__main__.detect_pose", return_value=[_valid_keypoints]),
        ):
            process_identity(
                Path(IDENTITY_DIR), Path(FACE_DIR), Path(UPPER_DIR), Path(LOWER_DIR),
                None, None, 0.0, 10, 0.5,
            )
            process_identity(
                Path(IDENTITY_DIR), Path(FACE_DIR), Path(UPPER_DIR), Path(LOWER_DIR),
                None, None, 0.0, 10, 0.5,
            )

        assert [p.name for p in Path(FACE_DIR).iterdir()] == ["valid_face.jpg"]
        assert [p.name for p in Path(UPPER_DIR).iterdir()] == ["valid_upper.jpg"]
        assert [p.name for p in Path(LOWER_DIR).iterdir()] == ["valid_lower.jpg"]
    """
    code = (
        code.replace("IDENTITY_DIR", repr(str(identity_dir)))
        .replace("FACE_DIR", repr(str(face_dir)))
        .replace("UPPER_DIR", repr(str(upper_dir)))
        .replace("LOWER_DIR", repr(str(lower_dir)))
    )
    tb.inject(code)


def test_derive_body_part_bbox_raises_when_fewer_than_two_points_pass(tb) -> None:
    tb.inject(
        f"""
        import numpy as np

        # anchor lolos, tapi hanya 1 titik total di grup
        _keypoints = np.zeros((17, 3))
        for _i in {sorted({5})}:
            _keypoints[_i] = (float(_i), float(_i), 0.9)

        try:
            derive_body_part_bbox(_keypoints, UPPER_KEYPOINT_INDICES, UPPER_ANCHOR_INDICES, 0.5)
            assert False, "harus raise InsufficientKeypointsError"
        except InsufficientKeypointsError:
            pass
        """
    )
