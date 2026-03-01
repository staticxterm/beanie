from functools import partial
from typing import Annotated, Optional

import pytest
from pydantic import BaseModel
from pydantic.fields import FieldInfo

from beanie.odm.fields import BackLink, Link, LinkTypes
from beanie.odm.utils.init import Initializer

detect_link = partial(
    Initializer.detect_link, Initializer.__new__(Initializer)
)


# ---------------------------------------------------------------------------
# Minimal document stubs — just enough for DocsRegistry.evaluate_fr to resolve
# ---------------------------------------------------------------------------


class MyDoc(BaseModel):
    id: str = "stub"


# ---------------------------------------------------------------------------
# Helpers to build a FieldInfo with a specific annotation
# ---------------------------------------------------------------------------


def make_field(annotation) -> tuple[FieldInfo, str]:
    """Returns (FieldInfo, field_name) with the given annotation attached."""
    field = FieldInfo.from_annotation(annotation)
    field.annotation = annotation
    return field, "test_field"


def make_backlink_field(
    annotation, original_field: str = "test_field"
) -> tuple[FieldInfo, str]:
    """Returns a FieldInfo with original_field in json_schema_extra, as Beanie expects."""
    field = FieldInfo.from_annotation(annotation)
    field.annotation = annotation
    field.json_schema_extra = {"original_field": original_field}
    return field, "test_field"


# ---------------------------------------------------------------------------
# Link — Direct
# ---------------------------------------------------------------------------


def test_direct_link():
    field, name = make_field(Link[MyDoc])
    result = detect_link(field, name)
    assert result is not None
    assert result.link_type == LinkTypes.DIRECT


def test_direct_backlink():
    field, name = make_backlink_field(BackLink[MyDoc])
    result = detect_link(field, name)
    assert result is not None
    assert result.link_type == LinkTypes.BACK_DIRECT


# ---------------------------------------------------------------------------
# Link — List
# ---------------------------------------------------------------------------


def test_list_link():
    field, name = make_field(list[Link[MyDoc]])
    result = detect_link(field, name)
    assert result is not None
    assert result.link_type == LinkTypes.LIST


def test_list_backlink():
    field, name = make_backlink_field(list[BackLink[MyDoc]])
    result = detect_link(field, name)
    assert result is not None
    assert result.link_type == LinkTypes.BACK_LIST


# ---------------------------------------------------------------------------
# Link — Optional
# ---------------------------------------------------------------------------


def test_optional_link():
    field, name = make_field(Optional[Link[MyDoc]])  # noqa: UP045
    result = detect_link(field, name)
    assert result is not None
    assert result.link_type == LinkTypes.OPTIONAL_DIRECT


def test_optional_backlink():
    field, name = make_backlink_field(Optional[BackLink[MyDoc]])  # noqa: UP045
    result = detect_link(field, name)
    assert result is not None
    assert result.link_type == LinkTypes.OPTIONAL_BACK_DIRECT


# ---------------------------------------------------------------------------
# Link — Optional List
# ---------------------------------------------------------------------------


def test_optional_list_link():
    field, name = make_field(Optional[list[Link[MyDoc]]])  # noqa: UP045
    result = detect_link(field, name)
    assert result is not None
    assert result.link_type == LinkTypes.OPTIONAL_LIST


def test_optional_list_backlink():
    field, name = make_backlink_field(Optional[list[BackLink[MyDoc]]])  # noqa: UP045
    result = detect_link(field, name)
    assert result is not None
    assert result.link_type == LinkTypes.OPTIONAL_BACK_LIST


# ---------------------------------------------------------------------------
# Annotated forms
# ---------------------------------------------------------------------------


def test_annotated_direct_link():
    field, name = make_field(Annotated[MyDoc, Link[MyDoc]])
    result = detect_link(field, name)
    assert result is not None
    assert result.link_type == LinkTypes.DIRECT


def test_annotated_direct_backlink():
    field, name = make_backlink_field(Annotated[MyDoc | None, BackLink[MyDoc]])
    result = detect_link(field, name)
    assert result is not None
    assert result.link_type == LinkTypes.BACK_DIRECT


def test_annotated_optional_link():
    field, name = make_field(Annotated[MyDoc | None, Optional[Link[MyDoc]]])  # noqa: UP045
    result = detect_link(field, name)
    assert result is not None
    assert result.link_type == LinkTypes.OPTIONAL_DIRECT


def test_annotated_optional_backlink():
    field, name = make_backlink_field(
        Annotated[MyDoc | None, Optional[BackLink[MyDoc]]]  # noqa: UP045
    )
    result = detect_link(field, name)
    assert result is not None
    assert result.link_type == LinkTypes.OPTIONAL_BACK_DIRECT


def test_annotated_with_extra_metadata_link():
    field, name = make_field(Annotated[MyDoc, dict, Link[MyDoc]])
    result = detect_link(field, name)
    assert result is not None
    assert result.link_type == LinkTypes.DIRECT


def test_annotated_with_extra_metadata_backlink():
    field, name = make_backlink_field(Annotated[MyDoc, dict, BackLink[MyDoc]])
    result = detect_link(field, name)
    assert result is not None
    assert result.link_type == LinkTypes.BACK_DIRECT


# ---------------------------------------------------------------------------
# Negative cases
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "annotation",
    [
        str,
        int,
        MyDoc,
        list[str],
        Optional[str],  # noqa: UP045
        str | None,
        Annotated[str, str],
    ],
)
def test_non_link_returns_none(annotation):
    field, name = make_field(annotation)
    assert detect_link(field, name) is None
