# SPDX-FileCopyrightText: 2024 Univention GmbH
# SPDX-License-Identifier: AGPL-3.0-only

import jsonpath


def findone(data, path):
    return jsonpath.match(path, data).obj


def findall(data, path):
    return jsonpath.match(path, data).obj
