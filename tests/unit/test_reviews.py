import pytest
from pydantic import ValidationError

from app.api.schemas import ReviewCreate
from tests.review_helpers import REVIEW


@pytest.mark.parametrize(
    "patch",
    [
        {"reason": "x" * 9},
        {"reason": "x" * 501},
        {"reason": None},
        {"reason": 123},
        {"reason": " " * 10},
        {"declared_reviewer": "x"},
        {"declared_reviewer": "x" * 81},
        {"declared_reviewer": "  x  "},
        {"declared_reviewer": None},
        {"declared_reviewer": 123},
        {"category": "financeiro"},
        {"priority": "urgente"},
        {"category": None},
        {"expected_version": 0},
        {"expected_version": True},
        {"expected_version": "3"},
        {"review_id": "11111111-1111-4111-8111-111111111111"},
        {"attempt_id": "injetado"},
        {"status": "resolvido"},
    ],
)
def test_us06_ca2_ca3_strict_review_contract(patch):
    with pytest.raises(ValidationError):
        ReviewCreate.model_validate({"expected_version": 3, **REVIEW, **patch})


@pytest.mark.parametrize("length,author", [(10, 2), (500, 80)])
def test_us06_ca3_trim_unicode_boundaries(length, author):
    body = ReviewCreate.model_validate(
        {
            "expected_version": 3,
            **REVIEW,
            "reason": "  " + "á" * length + "\n",
            "declared_reviewer": "  " + "ç" * author + "  ",
        }
    )
    assert len(body.reason) == length and len(body.declared_reviewer) == author
