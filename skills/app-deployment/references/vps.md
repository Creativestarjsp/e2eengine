# VPS (self-managed server)

Applies to any Linux server you operate: a VPS provider, or a single VM on AWS, GCP, or Azure.

## Fits

Full control, predictable cost, long-running processes, and several small services on one machine. The cost is operations: you patch, back up, monitor, and secure it. Do not choose it if nobody will do that work.

## Baseline before the first deploy

- A non-root deploy user; SSH by key only; password and root login disabled.
- Firewall allowing only SSH, 80, and 443.
- Automatic security updates.
- A reverse proxy (Caddy or Nginx) terminating TLS with automatically renewed certificates.
- Database not exposed to the internet.
- Backups of data volumes, stored off the server, with a tested restore.

Record what is done and what is not in `DEPLOYMENT.md`; an unpatched server is a known risk, not a detail.

## Project files

`Dockerfile`, `docker-compose.yml` (or `compose.yaml`), the reverse-proxy config, and an env file on the server that is never committed.

## Authentication

- Local: an SSH key for the deploy user.
- CI: a dedicated deploy key stored as a CI secret, with the server's host key pinned in `known_hosts`. Do not disable host key checking.

## Configuration and secrets

An env file on the server readable only by the deploy user (`chmod 600`), or Docker secrets. Values are placed on the server once from the store named in `CREDENTIALS.md`; they never pass through the repository.

## Preview deploy

A second compose project on the same server under a staging hostname, or a separate small server. Preview must use its own database.

## Production deploy

Image-based, so every release is an immutable, tagged artifact:

1. CI builds the image and pushes it to a registry, tagged with the commit SHA.
2. On the server: set the image tag in the env file, `docker compose pull`, `docker compose up -d`.
3. Run migrations as a one-off container before switching the app.
4. Smoke test through the public hostname.

Give each service a health check so compose reports unhealthy containers, and keep the previous image on the server.

## Rollback

Set the image tag back to the previous SHA and `docker compose up -d`. Keep at least the last few images; prune older ones on a schedule. Database changes are not reverted.

## Logs

`docker compose logs -f <service>`; `journalctl` for system services. Ship logs off the server if they matter after a disk failure.

## CI notes

The pipeline connects over SSH, runs the pull and up commands, and then runs the smoke test from outside the server.

## Gotchas

- Disk fills with old images and logs; set log rotation and prune.
- A single server is a single point of failure; state the recovery time honestly in the runbook.
- Restart policy `unless-stopped` and enabling the Docker service at boot are what bring the app back after a reboot.
