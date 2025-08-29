#!/bin/bash
# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

SVC=${1:-udm-listener}
while true ; do
    while docker compose stats --no-stream  | grep -q $SVC; do
        echo -n "$SVC: ";
        date ;
    done ;
    docker compose logs $SVC | tail -200 > $SVC.crash.$(date +%Y%m%d-%H%M%s).log;
    sleep 5;
    docker compose up -d $SVC 2>&1;
done | tee -a $SVC.mon.log
