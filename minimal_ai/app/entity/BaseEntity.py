import json
from typing import Any, Callable

from pydantic import BaseModel, ConfigDict

_json_encoders: dict[Any, Callable[[Any], Any]] = {}


def to_camelcase(string: str) -> str:
    """The alias generator for PublicEntity."""

    resp = "".join(
        word.capitalize() if index else word
        for index, word in enumerate(string.split("_"))
    )
    return resp


class BaseEntity(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
        use_enum_values=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
        from_attributes=True,
        json_encoders=_json_encoders,
        loc_by_alias=True,
        alias_generator=to_camelcase,
    )

    def flat_dict(self, by_alias=True):
        """This method might be useful if the data should be passed
        only with primitives that are allowed by JSON format.
        The regular .model_dump() does not return the ISO datetime format
        but the .model_dump_json() - does.
        This method is just a combination of them both.
        """
        return json.loads(self.model_dump_json(by_alias=by_alias))
