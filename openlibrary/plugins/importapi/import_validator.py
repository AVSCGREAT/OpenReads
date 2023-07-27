# mostly generated by datamodel-codegen:
#   filename:  import.schema.json
#   timestamp: 2023-07-24T12:05:23+00:00

from __future__ import annotations

from enum import Enum
from typing import Annotated, Any, Optional, TypeVar

from annotated_types import MinLen
from pydantic import (
    AnyHttpUrl,
    BaseModel,
    ConfigDict,
    Field,
    PositiveInt,
    RootModel,
    StringConstraints,
    ValidationError,
)

T = TypeVar("T")

NonEmptyList = Annotated[list[T], MinLen(1)]
NonEmptyStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class PublishCountry(RootModel):
    root: Annotated[str, StringConstraints(pattern=r'^[a-z]{2,3}$')] = Field(
        ...,
        description='The MARC21 country code. See https://www.loc.gov/marc/countries/cou_home.html',
        examples=['enk', 'gw', 'flu'],
    )


class LanguageCode(RootModel):
    root: Annotated[str, StringConstraints(pattern=r'^[a-z]{3}$')] = Field(
        ...,
        description='The MARC21 language code. See https://www.loc.gov/marc/languages/language_code.html',
        examples=['eng', 'fre', 'ger', 'tha'],
    )


class Isbn10(RootModel):
    root: Annotated[str, StringConstraints(pattern=r'^([0-9][- ]?){9}[0-9X]$')]


class Isbn13(RootModel):
    root: Annotated[str, StringConstraints(pattern=r'^([0-9][- ]?){13}$')]


class WorkKey(RootModel):
    root: Annotated[str, StringConstraints(pattern=r'^/works/OL[0-9]+W$')]


class Language(BaseModel):
    model_config = ConfigDict(extra="forbid")

    key: Annotated[str, StringConstraints(pattern=r'^/languages/[a-z]{3}$')] = Field(
        ..., examples=['/languages/eng', '/languages/ger']
    )


class LcClassification(RootModel):
    root: NonEmptyStr = Field(
        ...,
        description='The Library of Congress Classification number. See https://www.loc.gov/catdir/cpso/lcc.html We include the imprint date as the last four digits.',  # noqa: E501
        examples=['BS571.5 .S68 1995', 'Z673.D62 C65 1994'],
    )


class Key(Enum):
    field_type_link = '/type/link'


class Type(BaseModel):
    model_config = ConfigDict(extra="forbid")

    key: Key


class Link(BaseModel):
    model_config = ConfigDict(extra="forbid")
    url: AnyHttpUrl
    title: NonEmptyStr
    type: Optional[Type] = None


class EntityType(Enum):
    person = 'person'
    org = 'org'
    event = 'event'


class Author(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: NonEmptyStr = Field(examples=['Hubbard, Freeman H.', 'Joan Miró'])
    personal_name: Optional[NonEmptyStr] = Field(
        None,
        description="Can be identical to 'name'. TODO: provide information on the intended difference.",
    )
    birth_date: Optional[NonEmptyStr] = Field(None, examples=[])
    death_date: Optional[NonEmptyStr] = Field(None, examples=[])
    entity_type: Optional[EntityType] = None
    title: Optional[NonEmptyStr] = Field(None, examples=["duc d'Otrante"])


class Book(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: NonEmptyStr
    subtitle: Optional[NonEmptyStr] = None
    source_records: NonEmptyList[NonEmptyStr]
    publishers: NonEmptyList[NonEmptyStr]
    authors: NonEmptyList[Author]
    publish_date: NonEmptyStr = Field(
        ..., examples=['1992', 'December 1992', '12 January 2002']
    )
    location: Optional[NonEmptyList[NonEmptyStr]] = None
    publish_places: Optional[NonEmptyList[NonEmptyStr]] = None
    number_of_pages: Optional[PositiveInt] = None
    pagination: Optional[NonEmptyStr] = None
    by_statement: Optional[NonEmptyStr] = None
    description: Optional[NonEmptyStr] = None
    publish_country: Optional[PublishCountry] = None
    languages: Optional[list[LanguageCode]] = None
    translated_from: Optional[list[LanguageCode]] = None
    translation_of: Optional[NonEmptyStr] = None
    isbn_10: Optional[list[Isbn10]] = None
    isbn_13: Optional[list[Isbn13]] = None
    oclc_numbers: Optional[NonEmptyList[NonEmptyStr]] = None
    lccn: Optional[NonEmptyList[NonEmptyStr]] = None
    lc_classifications: Optional[list[LcClassification]] = None
    dewey_decimal_class: Optional[NonEmptyList[NonEmptyStr]] = None
    notes: Optional[NonEmptyStr] = None
    edition_name: Optional[NonEmptyStr] = Field(
        None, examples=['1st ed.', '2000 edition']
    )
    table_of_contents: Optional[list] = None
    series: Optional[NonEmptyList[NonEmptyStr]] = None
    subjects: Optional[NonEmptyList[NonEmptyStr]] = None
    subject_times: Optional[NonEmptyList[NonEmptyStr]] = None
    subject_people: Optional[NonEmptyList[NonEmptyStr]] = None
    subject_places: Optional[NonEmptyList[NonEmptyStr]] = None
    contributions: Optional[NonEmptyList[NonEmptyStr]] = None
    work_titles: Optional[NonEmptyList[NonEmptyStr]] = None
    other_titles: Optional[NonEmptyList[NonEmptyStr]] = None
    links: Optional[list[Link]] = None
    physical_format: Optional[NonEmptyStr] = Field(
        None, examples=['Paperback', 'Hardcover', 'Spiral-bound']
    )
    physical_dimensions: Optional[NonEmptyStr] = Field(
        None, examples=['5.4 x 4.7 x 0.2 inches', '21 x 14.8 x 0.8 centimeters']
    )
    weight: Optional[NonEmptyStr] = Field(
        None, examples=['300 grams', '0.3 kilos', '12 ounces', '1 pounds']
    )
    identifiers: Optional[
        dict[
            Annotated[str, StringConstraints(pattern=r'^\w+')],
            NonEmptyList[NonEmptyStr],
        ]
    ] = Field(
        None,
        description='Unique identifiers used by external sites to identify a book. Used by Open Library to link offsite.',
        examples=[
            {'standard_ebooks': ['leo-tolstoy/what-is-art/aylmer-maude']},
            {'project_gutenberg': ['64317']},
        ],
    )
    cover: Optional[AnyHttpUrl] = Field(
        None,
        description="URL for an edition's cover",
        examples=['https://www.example.com/images/8.jpeg'],
    )


class Work(BaseModel):
    model_config = ConfigDict(extra="forbid")

    key: WorkKey


class import_validator:
    def validate(self, data: dict[str, Any]):
        """Validate the given import data.

        Return True if the import object is valid.
        """

        try:
            Book.model_validate(data)
        except ValidationError as e:
            raise e

        return True
