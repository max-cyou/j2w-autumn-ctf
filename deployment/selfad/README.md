# SelfAD event deployment

This directory records a sanitized version of the SelfAD deployment used for
J2W Autumn CTF. The public domains, SSH port, worker concurrency and nginx
layout are real; secrets and passwords are not included.

The deployment ran SelfAD, Gitea, PostgreSQL and the runner on one VPS. It is
appropriate for reproducing the event or running a trusted demo, but the
privileged internal runner is not a safe isolation boundary for a new public
competition. For that, follow SelfAD's dedicated runner documentation.

## Files

- `.env.example` — sanitized production environment;
- `docker-compose.nginx.yml` — disables bundled Caddy and binds HTTP services
  to loopback for host nginx;
- `nginx.conf` — the two real virtual hosts, including the Gitea public-access
  gate.

## Reproduce the platform

Clone SelfAD separately and copy these files into that checkout:

```bash
git clone https://github.com/max-cyou/SelfAD.git /opt/selfad
cd /opt/selfad
cp /path/to/j2w-autumn-ctf/deployment/selfad/.env.example .env
cp /path/to/j2w-autumn-ctf/deployment/selfad/docker-compose.nginx.yml .
chmod 0600 .env
mkdir -p /srv/selfad/runner-pwf-tls
```

Generate a different random value for every `replace-with-*` entry:

```bash
openssl rand -hex 32
```

Point `ctf.jmp2win.xyz` and `git.ctf.jmp2win.xyz` at the host, obtain a TLS
certificate covering both names, and install `nginx.conf` as an nginx site.

Validate and start:

```bash
nginx -t

docker compose \
  -f docker-compose.production.yml \
  -f docker-compose.nginx.yml \
  -f docker-compose.single-vps.yml \
  config --quiet

docker compose \
  -f docker-compose.production.yml \
  -f docker-compose.nginx.yml \
  -f docker-compose.single-vps.yml \
  up -d --build
```

Complete initial setup using the secret placed in `.env`:

```text
https://ctf.jmp2win.xyz/setup?setup_token=<SELFAD_SETUP_TOKEN>
```

The Gitea GUI is closed by default and may be enabled in
**Admin → General → Git interface**. Git over SSH remains available on port
`2224` regardless of that switch.

Challenge source and jury repositories from this repository must still be
imported through the SelfAD administrator interface; they are not baked into
the Compose stack.
