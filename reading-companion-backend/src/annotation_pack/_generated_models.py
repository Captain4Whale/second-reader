# Generated file; do not edit. source=contract/annotation-pack/v0/schema/annotation-pack.schema.json sha256=583e4ff7025161572c437352e1f1d3d45d84e45e07687ea51db4046819c655c1 tool=datamodel-code-generator==0.74.0 formatter=ruff==0.15.5

from __future__ import annotations

from pydantic import (
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    RootModel,
    conint,
    constr,
)
from typing import Literal
from enum import Enum


class UuidV5Urn(
    RootModel[
        constr(
            pattern=r"^urn:uuid:[0-9a-f]{8}-[0-9a-f]{4}-5[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
        )
    ]
):
    root: constr(
        pattern=r"^urn:uuid:[0-9a-f]{8}-[0-9a-f]{4}-5[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
    )


class UtcDateTime(RootModel[AwareDatetime]):
    root: AwareDatetime


class RelativeEpubHref(RootModel[str]):
    model_config = ConfigDict(
        regex_engine="python-re",
    )
    root: constr(
        pattern=r"^(?![A-Za-z][A-Za-z0-9+.-]*:)(?!/)(?!.*(?:^|/)\.\.(?:/|$))(?!.*[?#\\])[^\s]+$",
        min_length=1,
        max_length=2048,
    )


class Generator(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )
    id: Literal["https://github.com/Captain4Whale/second-reader"]
    type: Literal["Software"]
    name: Literal["Second Reader Annotation Pack Exporter"]


class DcIdentifierItem(RootModel[constr(pattern=r"^nih:sha-256;[0-9a-f]{64}$")]):
    root: constr(pattern=r"^nih:sha-256;[0-9a-f]{64}$")


class DcCreatorItem(RootModel[constr(min_length=1, max_length=512)]):
    root: constr(min_length=1, max_length=512)


class Publication(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )
    dc_identifier: tuple[DcIdentifierItem] = Field(..., alias="dc:identifier")
    dc_format: Literal["application/epub+zip"] = Field(..., alias="dc:format")
    dc_title: constr(min_length=1, max_length=1024) = Field(..., alias="dc:title")
    dc_creator: list[DcCreatorItem] | None = Field(
        None, alias="dc:creator", min_length=1
    )


class Motivation(Enum):
    highlighting = "highlighting"
    commenting = "commenting"


class TextualBody(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )
    type: Literal["TextualBody"]
    value: constr(min_length=1, max_length=16384)


class TextQuoteSelector(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )
    type: Literal["TextQuoteSelector"]
    exact: constr(min_length=1, max_length=1024)
    prefix: constr(min_length=1, max_length=128) | None = None
    suffix: constr(min_length=1, max_length=128) | None = None


class TextPositionSelector(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )
    type: Literal["TextPositionSelector"]
    start: conint(ge=0)
    end: conint(ge=1)


class AnnotationTarget(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )
    source: RelativeEpubHref
    selector: tuple[TextQuoteSelector, TextPositionSelector]


class Annotation(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )
    id: UuidV5Urn
    type: Literal["Annotation"]
    motivation: Motivation
    created: UtcDateTime
    body: TextualBody | None = None
    target: AnnotationTarget


class AnnotationPackDocument(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
    )
    field_context: Literal["https://www.w3.org/ns/epub-anno.jsonld"] = Field(
        ..., alias="@context"
    )
    id: UuidV5Urn
    type: Literal["AnnotationSet"]
    generator: Generator
    generated: UtcDateTime
    about: Publication
    items: list[Annotation]
