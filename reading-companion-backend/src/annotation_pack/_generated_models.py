# Generated file; do not edit. source=contract/annotation-pack/v0/schema/annotation-pack.schema.json sha256=cf680dbca455f6111a30eb5c884d0e3cf45300cb1ef4ce3c5d5b77c3e2e0930f tool=datamodel-code-generator==0.74.0 formatter=ruff==0.15.5

from __future__ import annotations

from typing import Any, Literal
from pydantic import (
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    RootModel,
    conint,
    constr,
)
from enum import Enum


class FieldContextItem(BaseModel):
    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
    )
    field_protected: Literal[True] = Field(..., alias="@protected")
    sr: Literal["https://captain4whale.github.io/second-reader/ns/annotation-pack#"]


class UuidUrn(
    RootModel[
        constr(
            pattern=r"^urn:uuid:[0-9a-f]{8}-[0-9a-f]{4}-5[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
        )
    ]
):
    root: constr(
        pattern=r"^urn:uuid:[0-9a-f]{8}-[0-9a-f]{4}-5[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
    )


class AbsoluteIri(RootModel[constr(pattern=r"^[A-Za-z][A-Za-z0-9+.-]*:")]):
    root: constr(pattern=r"^[A-Za-z][A-Za-z0-9+.-]*:")


class UtcDateTime(RootModel[AwareDatetime]):
    root: AwareDatetime


class Sha256Hex(RootModel[constr(pattern=r"^[0-9a-f]{64}$")]):
    root: constr(pattern=r"^[0-9a-f]{64}$")


class Semver(
    RootModel[
        constr(
            pattern=r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$"
        )
    ]
):
    root: constr(
        pattern=r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$"
    )


class LanguageTag(RootModel[constr(pattern=r"^[A-Za-z]{2,8}(?:-[A-Za-z0-9]{1,8})*$")]):
    root: constr(pattern=r"^[A-Za-z]{2,8}(?:-[A-Za-z0-9]{1,8})*$")


class RelativeEpubHref(RootModel[str]):
    model_config = ConfigDict(
        regex_engine="python-re",
    )
    root: constr(
        pattern=r"^(?![A-Za-z][A-Za-z0-9+.-]*:)(?!/)(?!.*(?:^|/)\.\.(?:/|$))(?!.*[?#\\])[^\s]+$",
        min_length=1,
    )


class SrScheme(Enum):
    isbn_10 = "isbn-10"
    isbn_13 = "isbn-13"
    uri = "uri"
    opf_identifier = "opf-identifier"
    work_uri = "work-uri"


class Identifier(BaseModel):
    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
    )
    type: Literal["sr:Identifier"]
    sr_scheme: SrScheme = Field(..., alias="sr:scheme")
    sr_value: constr(min_length=1, max_length=2048) = Field(..., alias="sr:value")


class Fingerprint(BaseModel):
    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
    )
    type: Literal["sr:Fingerprint"]
    sr_algorithm: Literal["sha256"] = Field(..., alias="sr:algorithm")
    sr_algorithm_version: constr(min_length=1, max_length=128) = Field(
        ..., alias="sr:algorithmVersion"
    )
    sr_value: Sha256Hex = Field(..., alias="sr:value")


class EditionContentFingerprint(Fingerprint):
    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
    )
    sr_algorithm_version: Literal["sr-book-document-text-v1"] = Field(
        ..., alias="sr:algorithmVersion"
    )


class ChapterFingerprint(BaseModel):
    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
    )
    type: Literal["sr:ChapterFingerprint"]
    sr_chapter_id: int = Field(..., alias="sr:chapterId")
    sr_order: conint(ge=1) = Field(..., alias="sr:order")
    sr_title: constr(max_length=512) | None = Field(None, alias="sr:title")
    sr_resource_hrefs: list[RelativeEpubHref] | None = Field(
        None, alias="sr:resourceHrefs", min_length=1
    )
    sr_algorithm: Literal["sha256"] = Field(..., alias="sr:algorithm")
    sr_algorithm_version: Literal["sr-book-document-chapter-v1"] = Field(
        ..., alias="sr:algorithmVersion"
    )
    sr_value: Sha256Hex = Field(..., alias="sr:value")


class SrIdentityStrength(Enum):
    asserted = "asserted"
    provisional = "provisional"


class WorkIdentity(BaseModel):
    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
    )
    id: UuidUrn
    type: Literal["sr:WorkIdentity"]
    sr_identity_strength: SrIdentityStrength = Field(..., alias="sr:identityStrength")
    sr_identifiers: list[Identifier] | None = Field(
        None, alias="sr:identifiers", min_length=1
    )


class EditionIdentity(BaseModel):
    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
    )
    id: UuidUrn
    type: Literal["sr:EditionIdentity"]
    sr_content_fingerprint: EditionContentFingerprint = Field(
        ..., alias="sr:contentFingerprint"
    )
    sr_publication_identifiers: list[Identifier] | None = Field(
        None, alias="sr:publicationIdentifiers"
    )
    sr_language: LanguageTag | None = Field(None, alias="sr:language")
    sr_chapter_fingerprints: list[ChapterFingerprint] = Field(
        ..., alias="sr:chapterFingerprints", min_length=1
    )


class FileIdentity(BaseModel):
    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
    )
    id: UuidUrn
    type: Literal["sr:FileIdentity"]
    dc_format: Literal["application/epub+zip"] = Field(..., alias="dc:format")
    sr_sha256: Sha256Hex = Field(..., alias="sr:sha256")
    sr_byte_length: conint(ge=0) = Field(..., alias="sr:byteLength")


class DcCreatorItem(RootModel[constr(min_length=1, max_length=512)]):
    root: constr(min_length=1, max_length=512)


class DcIdentifierItem(RootModel[constr(min_length=1, max_length=2048)]):
    root: constr(min_length=1, max_length=2048)


class PublicationIdentity(BaseModel):
    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
    )
    dc_format: Literal["application/epub+zip"] = Field(..., alias="dc:format")
    dc_title: constr(min_length=1, max_length=1024) = Field(..., alias="dc:title")
    dc_creator: list[DcCreatorItem] | None = Field(
        None, alias="dc:creator", min_length=1
    )
    dc_identifier: list[DcIdentifierItem] = Field(
        ..., alias="dc:identifier", min_length=3
    )
    sr_work: WorkIdentity = Field(..., alias="sr:work")
    sr_edition: EditionIdentity = Field(..., alias="sr:edition")
    sr_file: FileIdentity = Field(..., alias="sr:file")


class Type(Enum):
    person = "Person"
    organization = "Organization"
    software = "Software"


class Creator(BaseModel):
    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
    )
    id: AbsoluteIri
    type: Type
    name: constr(min_length=1, max_length=256)


class Generator(BaseModel):
    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
    )
    id: AbsoluteIri
    type: Literal["Software"]
    name: constr(min_length=1, max_length=256)
    sr_version: Semver = Field(..., alias="sr:version")


class AnnotationTrack(BaseModel):
    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
    )
    id: UuidUrn
    type: Literal["sr:AnnotationTrack"]
    sr_key: constr(pattern=r"^[a-z0-9][a-z0-9._-]{0,63}$") = Field(..., alias="sr:key")
    name: constr(min_length=1, max_length=128) | None = None
    creator: Creator


class ProfileReference(BaseModel):
    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
    )
    type: Literal["sr:ProfileReference"]
    sr_web_annotation: Literal[
        "https://www.w3.org/TR/2017/REC-annotation-model-20170223/"
    ] = Field(..., alias="sr:webAnnotation")
    sr_epub_annotations: Literal[
        "https://www.w3.org/TR/2026/WD-epub-anno-10-20260521/"
    ] = Field(..., alias="sr:epubAnnotations")
    sr_conformance: Literal["aligned"] = Field(..., alias="sr:conformance")


class Digest(BaseModel):
    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
    )
    type: Literal["sr:Digest"]
    sr_algorithm: Literal["sha256"] = Field(..., alias="sr:algorithm")
    sr_canonicalization: constr(min_length=1, max_length=128) | None = Field(
        None, alias="sr:canonicalization"
    )
    sr_value: Sha256Hex = Field(..., alias="sr:value")


class SemanticDigest(Digest):
    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
    )
    sr_canonicalization: Literal["sr-canonical-json-v1"] = Field(
        ..., alias="sr:canonicalization"
    )


class InputSnapshotDigest(BaseModel):
    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
    )
    type: Literal["sr:Digest"]
    sr_algorithm: Literal["sha256"] = Field(..., alias="sr:algorithm")
    sr_canonicalization: Any | None = Field(None, alias="sr:canonicalization")
    sr_value: Sha256Hex = Field(..., alias="sr:value")


class Provenance(BaseModel):
    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
    )
    type: Literal["sr:Provenance"]
    sr_producer: AbsoluteIri = Field(..., alias="sr:producer")
    sr_adapter_version: Semver = Field(..., alias="sr:adapterVersion")
    sr_input_snapshot_digest: InputSnapshotDigest = Field(
        ..., alias="sr:inputSnapshotDigest"
    )
    sr_input_snapshot_algorithm_version: constr(min_length=1, max_length=128) = Field(
        ..., alias="sr:inputSnapshotAlgorithmVersion"
    )


class TextualBody(BaseModel):
    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
    )
    type: Literal["TextualBody"]
    value: constr(min_length=1, max_length=16384)
    format: Literal["text/plain"]
    language: LanguageTag | None = None


class TextQuoteSelector(BaseModel):
    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
    )
    type: Literal["TextQuoteSelector"]
    exact: constr(min_length=1, max_length=1024)
    prefix: constr(max_length=128)
    suffix: constr(max_length=128)
    sr_normalization: Literal["sr-epub-resource-text-v1"] = Field(
        ..., alias="sr:normalization"
    )


class ParagraphPosition(BaseModel):
    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
    )
    sr_chapter_id: int = Field(..., alias="sr:chapterId")
    sr_paragraph_index: conint(ge=1) = Field(..., alias="sr:paragraphIndex")
    sr_char_offset: conint(ge=0) = Field(..., alias="sr:charOffset")


class ParagraphCharSelector(BaseModel):
    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
    )
    type: Literal["sr:ParagraphCharSelector"]
    sr_coordinate_system: Literal["sr-book-document-paragraph-char-v1"] = Field(
        ..., alias="sr:coordinateSystem"
    )
    sr_offset_unit: Literal["unicode-code-point"] = Field(..., alias="sr:offsetUnit")
    sr_start: ParagraphPosition = Field(..., alias="sr:start")
    sr_end: ParagraphPosition = Field(..., alias="sr:end")


class EpubCfiSelector(BaseModel):
    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
    )
    type: Literal["sr:EpubCfiSelector"]
    value: constr(pattern=r"^epubcfi\(.+\)$", max_length=2048)
    sr_verification: Literal["quote-round-trip"] = Field(..., alias="sr:verification")


class SrFingerprint(Fingerprint):
    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
    )
    sr_algorithm_version: Literal["sr-book-document-chapter-v1"] = Field(
        ..., alias="sr:algorithmVersion"
    )


class ChapterContext(BaseModel):
    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
    )
    type: Literal["sr:ChapterContext"]
    sr_chapter_id: int = Field(..., alias="sr:chapterId")
    sr_order: conint(ge=1) = Field(..., alias="sr:order")
    name: constr(max_length=512) | None = None
    sr_fingerprint: SrFingerprint = Field(..., alias="sr:fingerprint")


class AnnotationTarget(BaseModel):
    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
    )
    type: Literal["SpecificResource"]
    source: RelativeEpubHref
    selector: list[TextQuoteSelector | ParagraphCharSelector | EpubCfiSelector] = Field(
        ..., max_length=3, min_length=2
    )
    sr_anchor_id: UuidUrn = Field(..., alias="sr:anchorId")
    sr_chapter: ChapterContext = Field(..., alias="sr:chapter")


class Motivation(Enum):
    highlighting = "highlighting"
    commenting = "commenting"


class SrKind(Enum):
    highlight = "highlight"
    note = "note"


class Annotation(BaseModel):
    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
    )
    id: UuidUrn
    type: Literal["Annotation"]
    motivation: Motivation
    creator: Creator
    created: UtcDateTime
    body: TextualBody | None = None
    target: AnnotationTarget
    sr_kind: SrKind = Field(..., alias="sr:kind")


class AnnotationPackDocument(BaseModel):
    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
    )
    field_context: tuple[
        Literal["https://www.w3.org/ns/epub-anno.jsonld"], FieldContextItem
    ] = Field(..., alias="@context")
    id: UuidUrn
    type: Literal["AnnotationSet"]
    generator: Generator
    generated: UtcDateTime
    about: PublicationIdentity
    items: list[Annotation]
    sr_spec_version: Literal["0.1.0"] = Field(..., alias="sr:specVersion")
    sr_schema_version: Literal["0.1.0"] = Field(..., alias="sr:schemaVersion")
    sr_extension_version: Literal["0.1"] = Field(..., alias="sr:extensionVersion")
    sr_profile: ProfileReference = Field(..., alias="sr:profile")
    sr_track: AnnotationTrack = Field(..., alias="sr:track")
    sr_provenance: Provenance = Field(..., alias="sr:provenance")
    sr_semantic_digest: SemanticDigest = Field(..., alias="sr:semanticDigest")
