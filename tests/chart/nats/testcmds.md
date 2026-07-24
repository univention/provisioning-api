## create stream

```
nats stream add teststream --subjects='testsubject.>' --storage=file --replicas=1 --ack --retention=limits --discard=old  --max-msg-size=-1 --max-msgs=-1 --max-msgs-per-subject=-1 --max-bytes=-1 --max-age=-1  --dupe-window="2m0s" --no-allow-rollup --no-deny-delete --no-deny-purge
```

## add consumer
```
nats consumer add teststream testconsumer --pull --deliver=all --ack=explicit --replay=instant --filter="" --max-deliver=-1 --max-pending=0 --no-headers-only --backoff=none
```

## publish message
```
echo $(date) | nats publish testsubject.test1
```
## consume message

```
nats consumer next teststream testconsumer
```
