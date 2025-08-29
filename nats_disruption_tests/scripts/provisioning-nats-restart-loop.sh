#!/bin/bash
# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH


while true ; do docker compose restart nats1 nats2 nats3 ; sleep 40 ; done

