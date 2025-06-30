# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH
try:
    from pydantic.v1 import BaseModel
    PYDANTIC_V1 = True
except ImportError:
    from pydantic import BaseModel
    PYDANTIC_V1 = False


class BaseModelWrapper(BaseModel):
    def model_dump(self, *args, **kwargs):
        return self.dict(*args, **kwargs)

    def model_dump_json(self, *args, **kwargs):
        return self.json(*args, **kwargs)

    @classmethod
    def model_validate(cls, data, *args, **kwargs):

        if PYDANTIC_V1:
            return cls.parse_obj(data)
        else:
            return super().model_validate(data, *args, **kwargs)
