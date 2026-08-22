import pytest
from controller.validator import InputValidator, ValidationResult

@pytest.fixture
def validator():
    return InputValidator()

def make_img(ref="img.tif", fmt="tiff", mod="optical", time=None):
    img = {"reference": ref, "format": fmt, "modality": mod}
    if time:
        img["acquisition_time"] = time
    return img

def test_valid_vqa_single_image(validator):
    req = {"images": [make_img()]}
    res = validator.validate(req, "vqa")
    assert res.valid is True
    assert len(res.errors) == 0

def test_vqa_zero_images(validator):
    req = {"images": []}
    res = validator.validate(req, "vqa")
    assert res.valid is False
    assert "No images were provided." in res.errors

def test_vqa_two_images(validator):
    req = {"images": [make_img(), make_img()]}
    res = validator.validate(req, "vqa")
    assert res.valid is False
    assert any("exactly 1 image" in e for e in res.errors)

def test_valid_captioning(validator):
    req = {"images": [make_img()]}
    res = validator.validate(req, "captioning")
    assert res.valid is True

def test_valid_grounding(validator):
    req = {"images": [make_img()]}
    res = validator.validate(req, "grounding")
    assert res.valid is True

def test_valid_change_vqa_two_images(validator):
    req = {"images": [
        make_img(time="2023-01-01T00:00:00Z"),
        make_img(time="2023-02-01T00:00:00Z")
    ]}
    res = validator.validate(req, "change_vqa")
    assert res.valid is True
    assert len(res.errors) == 0

def test_change_vqa_one_image(validator):
    req = {"images": [make_img()]}
    res = validator.validate(req, "change_vqa")
    assert res.valid is False
    assert any("exactly 2 images" in e for e in res.errors)

def test_change_vqa_without_timestamps(validator):
    req = {"images": [make_img(), make_img()]}
    res = validator.validate(req, "change_vqa")
    assert res.valid is True
    assert len(res.errors) == 0
    assert any("Acquisition time is unavailable" in w for w in res.warnings)

def test_valid_optical_sar_fusion(validator):
    req = {"images": [
        make_img(mod="optical"),
        make_img(mod="SAR")
    ]}
    res = validator.validate(req, "optical_sar_fusion")
    assert res.valid is True
    assert len(res.errors) == 0

def test_optical_sar_fusion_two_optical(validator):
    req = {"images": [make_img(mod="optical"), make_img(mod="optical")]}
    res = validator.validate(req, "optical_sar_fusion")
    assert res.valid is False
    assert any("one optical image and one SAR image" in e for e in res.errors)

def test_optical_sar_fusion_two_sar(validator):
    req = {"images": [make_img(mod="sar"), make_img(mod="SAR")]}
    res = validator.validate(req, "optical_sar_fusion")
    assert res.valid is False
    assert any("one optical image and one SAR image" in e for e in res.errors)

def test_optical_sar_fusion_missing_modality(validator):
    req = {"images": [
        make_img(mod="optical"),
        {"reference": "img2.tif", "format": "tiff"} # Missing modality
    ]}
    res = validator.validate(req, "optical_sar_fusion")
    assert res.valid is False
    assert any("modality information is required" in e for e in res.errors)

def test_unsupported_image_format(validator):
    req = {"images": [{"reference": "img.bmp", "format": "bmp"}]}
    res = validator.validate(req, "vqa")
    assert res.valid is False
    assert any("unsupported format" in e for e in res.errors)

def test_missing_image_reference(validator):
    req = {"images": [{"format": "tiff"}]}
    res = validator.validate(req, "vqa")
    assert res.valid is False
    assert any("missing a valid 'reference'" in e for e in res.errors)

def test_unknown_task(validator):
    req = {"images": [make_img()]}
    res = validator.validate(req, "unknown")
    assert res.valid is False
    assert any("not executable" in e for e in res.errors)

def test_invalid_request_type(validator):
    req = ["list", "not", "dict"]
    res = validator.validate(req, "vqa")
    assert res.valid is False
    assert any("dictionary" in e for e in res.errors)

def test_empty_image_list(validator):
    req = {"images": []}
    res = validator.validate(req, "vqa")
    assert res.valid is False
    assert any("No images were provided" in e for e in res.errors)

def test_case_insensitive_formats(validator):
    req = {"images": [
        make_img(fmt="TIFF"),
        make_img(fmt="GeoTIFF"),
        make_img(fmt="JPG")
    ]}
    res = validator.validate(req, "change_vqa") # requires 2 images, but we provided 3... wait, change_vqa requires exactly 2.
    assert res.valid is False # this would fail on image count, let's test format validation directly.
    
    # Better to test format validity independently by using a valid count task
    # Or just mock a task that requires 3 images? None exist.
    # We will test them one by one.
    
    res1 = validator.validate({"images": [make_img(fmt="TIFF")]}, "vqa")
    assert res1.valid is True
    
    res2 = validator.validate({"images": [make_img(fmt="GeoTIFF")]}, "captioning")
    assert res2.valid is True
    
    res3 = validator.validate({"images": [make_img(fmt="JPG")]}, "grounding")
    assert res3.valid is True
