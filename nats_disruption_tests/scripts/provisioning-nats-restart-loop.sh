#!/bin/bash

while true ; do docker compose restart nats1 nats2 nats3 ; sleep 40 ; done

