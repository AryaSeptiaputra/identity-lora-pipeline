"""Test notebook `notebooks/03_image_captioning.ipynb` dan `notebooks/00_pipeline_errors.ipynb`.

Notebook dijalankan lewat `testbook`, bukan diimpor sebagai modul `.py`, karena kode
inti sengaja tetap satu notebook per tahap (konsisten K6/K16). Sel bertag "manual-run"
(yang memanggil model JoyCaption sungguhan pada `data/cropped/`/`data/face/`, termasuk
semua sel runner "define -> demonstrate") tidak dieksekusi di sini. Model VLM
(`AutoProcessor`/`LlavaForConditionalGeneration`) di-mock sepenuhnya, tanpa mengunduh
atau memanggil bobot sungguhan.
"""

from pathlib import Path

import numpy as np
import pytest
from PIL import Image
from testbook import testbook

NOTEBOOKS_DIR = Path(__file__).resolve().parents[2] / "notebooks"
NOTEBOOK_PATH = str(NOTEBOOKS_DIR / "03_image_captioning.ipynb")
PIPELINE_ERROR_NAMES = (
    "ImageReadError",
    "CaptionGenerationError",
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
        "ImageCaption",
        "load_vlm_model",
        "generate_caption",
        "generate_captions",
        "save_caption",
        "post_process_caption",
        "list_image_paths",
        "caption_images",
        "run_captioning",
    ):
        tb.ref(name)


def _write_synthetic_image(path: Path) -> None:
    image = Image.fromarray(np.zeros((64, 64, 3), dtype=np.uint8))
    image.save(path)


def _inject_fake_vlm(tb) -> None:
    """Mendaftarkan processor dan model VLM palsu di namespace kernel notebook."""
    tb.inject(
        """
        import torch

        class _FakeTokenizer:
            def batch_decode(self, ids, skip_special_tokens=True):
                return [f"caption {i}" for i in range(ids.shape[0])]

        class _FakeBatchInputs(dict):
            def to(self, device):
                return self

        class _FakeProcessor:
            tokenizer = _FakeTokenizer()

            def apply_chat_template(self, conversation, tokenize=False, add_generation_prompt=True):
                content = conversation[0]["content"]
                assert isinstance(content, list), "content harus list blok image/text"
                assert {"type": "image"} in content
                assert any(block.get("type") == "text" for block in content)
                return "TEMPLATE"

            def __call__(self, text, images, return_tensors, padding):
                return _FakeBatchInputs(input_ids=torch.zeros((len(images), 3), dtype=torch.long))

        class _FakeModel:
            device = "cpu"
            fail_generate = False

            def generate(self, **kwargs):
                if self.fail_generate:
                    raise RuntimeError("model gagal")
                n = kwargs["input_ids"].shape[0]
                return torch.zeros((n, 6), dtype=torch.long)

        _fake_processor = _FakeProcessor()
        _fake_model = _FakeModel()
        """
    )


def test_generate_captions_uses_multimodal_chat_template_and_matches_batch_size(
    tb, tmp_path: Path
) -> None:
    image_paths = []
    for i in range(2):
        p = tmp_path / f"foto{i}.jpg"
        _write_synthetic_image(p)
        image_paths.append(p)

    _inject_fake_vlm(tb)
    code = f"""
        _captions = generate_captions(
            [Path(p) for p in {[str(p) for p in image_paths]!r}], _fake_processor, _fake_model
        )
        assert len(_captions) == 2
        assert all(isinstance(c, ImageCaption) for c in _captions)
        assert all(c.caption.startswith("caption") for c in _captions)
    """
    tb.inject(code)


def test_generate_captions_raises_image_read_error_for_broken_file(tb, tmp_path: Path) -> None:
    broken_path = tmp_path / "broken.jpg"
    broken_path.write_bytes(b"not an image")

    _inject_fake_vlm(tb)
    code = f"""
        try:
            generate_captions([Path({str(broken_path)!r})], _fake_processor, _fake_model)
            assert False, "harus raise ImageReadError"
        except ImageReadError:
            pass
    """
    tb.inject(code)


def test_generate_captions_raises_caption_generation_error_on_model_failure(
    tb, tmp_path: Path
) -> None:
    image_path = tmp_path / "foto.jpg"
    _write_synthetic_image(image_path)

    _inject_fake_vlm(tb)
    code = f"""
        _fake_model.fail_generate = True
        try:
            generate_captions([Path({str(image_path)!r})], _fake_processor, _fake_model)
            assert False, "harus raise CaptionGenerationError"
        except CaptionGenerationError:
            pass
        finally:
            _fake_model.fail_generate = False
    """
    tb.inject(code)


def test_save_caption_writes_text_file_next_to_image(tb, tmp_path: Path) -> None:
    image_path = tmp_path / "foto.jpg"
    _write_synthetic_image(image_path)

    code = f"""
        _caption = ImageCaption(caption="a photo of someone", prompt=PROMPT, temperature=TEMP)
        _caption_path = save_caption(Path({str(image_path)!r}), _caption)
        assert _caption_path == Path({str(image_path)!r}).with_suffix(".txt")
        assert _caption_path.read_text(encoding="utf-8") == "a photo of someone\\n"
    """
    tb.inject(code)


def test_post_process_caption_adds_trigger_word_once(tb, tmp_path: Path) -> None:
    caption_path = tmp_path / "foto.txt"
    caption_path.write_text("a photo of someone\n", encoding="utf-8")

    code = f"""
        _path = Path({str(caption_path)!r})
        post_process_caption(_path, "pinkchan")
        assert _path.read_text(encoding="utf-8") == "pinkchan, a photo of someone\\n"

        # idempoten: dipanggil dua kali tidak menduplikasi trigger word
        post_process_caption(_path, "pinkchan")
        assert _path.read_text(encoding="utf-8") == "pinkchan, a photo of someone\\n"
    """
    tb.inject(code)


def test_list_image_paths_collects_images_across_identities_up_to_limit(
    tb, tmp_path: Path
) -> None:
    for identity in ("alice", "bob"):
        identity_dir = tmp_path / identity
        identity_dir.mkdir()
        _write_synthetic_image(identity_dir / "a.jpg")
        _write_synthetic_image(identity_dir / "b.png")
        (identity_dir / "c.txt").write_text("bukan gambar", encoding="utf-8")

    code = f"""
        _paths = list_image_paths(Path({str(tmp_path)!r}), 3)
        assert len(_paths) == 3
        assert all(p.suffix.lower() in IMAGE_EXTENSIONS for p in _paths)
    """
    tb.inject(code)


def test_caption_images_batches_and_skips_failing_batch_without_stopping(
    tb, tmp_path: Path
) -> None:
    ok_paths = []
    for i in range(2):
        p = tmp_path / f"ok{i}.jpg"
        _write_synthetic_image(p)
        ok_paths.append(p)
    broken_path = tmp_path / "broken.jpg"
    broken_path.write_bytes(b"not an image")
    trailing_path = tmp_path / "trailing.jpg"
    _write_synthetic_image(trailing_path)

    _inject_fake_vlm(tb)
    all_paths = [*ok_paths, broken_path, trailing_path]
    code = f"""
        _caption_paths = caption_images(
            [Path(p) for p in {[str(p) for p in all_paths]!r}],
            _fake_processor,
            _fake_model,
            batch_size=2,
        )
        # Batch pertama (2 gambar valid) tersimpan; batch kedua (broken + trailing)
        # dilewati seluruhnya karena satu gambarnya rusak.
        assert sorted(p.name for p in _caption_paths) == ["ok0.txt", "ok1.txt"]
        assert not Path({str(trailing_path)!r}).with_suffix(".txt").exists()
    """
    tb.inject(code)
