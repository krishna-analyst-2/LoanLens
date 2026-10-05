import numpy as np
import pytest

from loanlens.bands import AGE_BANDS, CREDIT_BANDS, DTI_BANDS, RATE_BANDS, band, labels


@pytest.mark.parametrize("age, expected", [
    (18, "18-25"), (25, "18-25"), (26, "26-35"), (55, "46-55"), (56, "56+"), (69, "56+"),
])
def test_age_band_edges(age, expected):
    assert band(age, AGE_BANDS) == expected


@pytest.mark.parametrize("rate, expected", [
    (7.99, "Low (<8%)"), (8, "Moderate (8-13%)"), (12.995, "Moderate (8-13%)"), (25, "Very High (18%+)"),
])
def test_rate_band_edges(rate, expected):
    assert band(rate, RATE_BANDS) == expected


def test_dti_boundary_goes_to_upper_band():
    assert band(0.3, DTI_BANDS) == "Medium (0.3-0.5)"


def test_missing_value_is_unknown():
    assert band(np.nan, CREDIT_BANDS) == "Unknown"
    assert band(None, AGE_BANDS) == "Unknown"


def test_labels_end_with_unknown():
    assert labels(AGE_BANDS) == ["18-25", "26-35", "36-45", "46-55", "56+", "Unknown"]
