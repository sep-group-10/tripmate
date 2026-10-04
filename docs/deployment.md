# TripMate Deployment

Single server setup (no separate staging). Backend runs on one EC2 instance with blue-green zero-downtime deploys.

## Infrastructure

- **Server:** EC2 `t3.micro`, Ubuntu 24.04, Mumbai (`ap-south-1`)
- **Database:** RDS PostgreSQL (pgvector), private, only reachable from the EC2 security group
- **Domains:** `api.tripmate.kajatheepan.dev`
- **Images:** S3 + CloudFront
- **Email:** SES (production access)
- **Secrets:** AWS Parameter Store, under `/tripmate/prod/`
- **Registry:** GHCR — `ghcr.io/sep-group-10/tripmate-api`, tagged by commit SHA only (no `:latest`)

## Server users

| User | Purpose |
|---|---|
| `ubuntu` | Manual admin (sudo, system config) |
| `deploy` | Automated deploys only (in `docker` group, narrow passwordless sudo) |

## One-time server setup (already done)

1. EC2 launched, Elastic IP attached, security groups (`staging-ec2-sg`, `staging-rds-sg`) configured.
2. SSH hardened: key-only, no root login, `fail2ban`, separate `deploy` user + key.
3. Docker installed; `ubuntu` and `deploy` added to the `docker` group.
4. RDS created, connection tested.
5. nginx + Certbot — HTTPS certificate on `api.tripmate.kajatheepan.dev`.
6. IAM role `tripmate-prod-ec2-role` attached to the instance: SSM read (`/tripmate/prod/*`) + S3 + SES.
7. `/opt/tripmate/` created, owned by `deploy` — holds `deploy.sh`, `fetch-secrets.sh`, `.env.production`.
8. `/usr/local/bin/switch-backend.sh` (root-owned, manual) — rewrites nginx's upstream port and reloads.
9. Passwordless sudo for `deploy`, scoped to exactly 3 commands (`/etc/sudoers.d/deploy-tripmate`):
   - `systemctl reload nginx`
   - `docker compose -f /opt/tripmate/docker-compose.prod.yml *`
   - `/usr/local/bin/switch-backend.sh *`
10. `deploy` logged in to GHCR (`docker login`) using a PAT with `read:packages`.
11. nginx upstream config at `/etc/nginx/conf.d/upstream.conf`, read by `deploy.sh`, written only by `switch-backend.sh`.

## How a deploy works

Push to `main` touching `backend/**` → `.github/workflows/deploy.yml`:

1. **Build & push** — builds the image, tags with the full commit SHA, pushes to GHCR (uses `GITHUB_TOKEN`, not a stored secret).
2. **Deploy** — copies the repo's `deploy.sh` onto the server (always fresh, server never runs a stale copy), then runs it over SSH as `deploy`.

`deploy.sh` (on the server):

1. Takes an exclusive lock (`flock`) — a second deploy running at the same time waits/fails instead of colliding.
2. Reads nginx's config to find the live port (8000 or 8001) — this is the source of truth for what's live, not Docker.
3. Removes any container not matching the live port (safe only because the lock is already held).
4. Pulls the new image by SHA.
5. Starts the new container on the other port.
6. Health-checks it directly (`/health`), every 2s, up to 120s.
   - **Fails:** new container removed, old one untouched, exit non-zero (workflow shows red).
   - **Passes:** continue.
7. Saves current tag → `previous_tag.txt`, switches nginx via `switch-backend.sh`, writes new tag → `current_tag.txt`.
8. Waits 10s (drain), then stops and removes the old container.
9. Cleans up old images, keeps the newest 5.

## Rollback

```bash
ssh -i tripmate-deploy-key deploy@<server-ip>
/opt/tripmate/deploy.sh $(cat /opt/tripmate/previous_tag.txt)
```

This is just a normal deploy pointed at the previous tag — no special rollback path. After rolling back, `previous_tag.txt` correctly points to the version just rolled back from, so rolling forward again works the same way.

## Secrets

Stored in Parameter Store under `/tripmate/prod/`. Pulled onto the server with:
```bash
/opt/tripmate/fetch-secrets.sh
```
Writes `/opt/tripmate/.env.production` (`chmod 600`). Re-run manually if a secret value changes — not part of the automated deploy.

`AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` are **not** stored anywhere in production — the server's IAM role handles S3/SES/SSM automatically.

## GitHub Secrets used by the pipeline

| Name | Used for |
|---|---|
| `SSH_PRIVATE_KEY` | `deploy` user's private key |
| `SERVER_HOST` | Elastic IP |
| `SERVER_USER` | `deploy` |
| `GHCR_TOKEN` | Server's own `docker login` (pull side only — push side uses `GITHUB_TOKEN`) |

## Known limitations (accepted trade-offs)

- No separate staging environment — tested locally before every push to `main`.
- 10s drain on old-container shutdown: a long-running request (AI planning, up to 180s) caught at the exact moment of a switch can still be interrupted.
- Rollback depth is one step (current → previous only, not a full history).
- `switch-backend.sh` is not auto-synced from the repo — it rarely changes; update it manually on the server if it ever does.