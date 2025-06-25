# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH
try:
    from pydantic.v1 import BaseModel
except ImportError:
    from pydantic import BaseModel


class BaseModelWrapper(BaseModel):
    def model_dump(self, *args, **kwargs):
        return self.dict(*args, **kwargs)

    def model_dump_json(self, *args, **kwargs):
        return self.json(*args, **kwargs)

    def model_validate(self, data):
        return self.parse_obj(data)
