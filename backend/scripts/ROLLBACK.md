# Rolling back a deploy

If the latest deploy is bad, roll back to the previous version:

```bash
cd /opt/tripmate
./scripts/deploy.sh "$(cat previous_tag.txt)"
```

This runs the normal deploy process, just targeting the tag that was live
before the last deploy. It goes through the same health check and blue-green
swap as any other deploy — nothing special-cased.

## How it works

- `current_tag.txt` always holds the tag that is live right now.
- `previous_tag.txt` always holds the tag that was live right before the
  current one.
- Every deploy (including a rollback) shifts `current_tag.txt` into
  `previous_tag.txt` before switching. So after rolling back, you can roll
  forward again the same way if needed.

## If the rollback itself fails health check

The failed rollback container is removed automatically and the old
(bad) container keeps running untouched - same as any failed deploy.
Check `docker logs` on the container to see why, and fix forward instead.
