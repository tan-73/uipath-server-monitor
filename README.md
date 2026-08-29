# UiPath Homelab Health Monitor

A college RPA project demonstrating a UiPath Robot on Windows monitoring an isolated Docker demo stack on an Ubuntu homelab over Tailscale.

The working Robot classifies services as **Healthy**, **Degraded**, or **Down**, tracks state
transitions, suppresses duplicate incident transitions, writes structured monitoring logs, and
generates a run summary, and sends transition-based SMTP alerts without receiving access to Docker
or the Ubuntu host.

## Current status

- Phase 1 — Prerequisites: complete
- Phase 2 — Isolated server demo stack: complete
- Phase 3 — UiPath monitor: complete
- Presentation CLI — interactive dashboard: complete
- SMTP implementation: complete in the smtp-implement branch
- Phase 4 — Proper email alerts and reporting: critical outage alert verified; final validation pending
- Phase 5 — Rehearsal and final documentation: not started

## Architecture

```text
Windows computer
└── UiPath Studio Community 2026.0.200 STS
    ├── Windows/VB monitoring workflow
    ├── UiPath.WebAPI.Activities 2.5.2
    └── Polls HTTP endpoints through Tailscale
             │
             ▼
Ubuntu homelab: 100.103.92.83
├── Isolated Docker Compose project: uipath-homelab-monitor
│   ├── demo-alpha  100.103.92.83:18081
│   ├── demo-beta   100.103.92.83:18082
│   └── demo-gamma  100.103.92.83:18083
└── Local interactive presentation CLI
```

UiPath observes only HTTP behavior. It does not connect to Docker, the Docker socket, or a Docker API.

## What alpha, beta, and gamma represent

The three services are controlled test subjects with different roles in the monitoring demonstration:

| Service | Role | Normal demonstration behavior |
|---|---|---|
| `demo-alpha` | Healthy control | Remains healthy throughout the demonstration, proving that the monitor and network still work while other services fail. |
| `demo-beta` | Soft/application failure | Its container keeps running, but the application changes from healthy to degraded and `/health` returns HTTP 503. This represents a dependency or application-level failure. |
| `demo-gamma` | Hard/service outage | Its container is stopped, so no HTTP response exists and UiPath receives a connection failure. This represents a completely unavailable service. |

The names are neutral labels rather than real homelab applications. This keeps the experiment separate from existing services and makes each failure scenario predictable and safe.

### State interpretation

| Observed behavior | UiPath classification | Meaning |
|---|---|---|
| HTTP 200 with `status: healthy` | Healthy | The application is reachable and its checks pass. |
| HTTP 503 with `status: degraded` | Degraded | The container and HTTP server are running, but an application dependency is simulated as unavailable. |
| Connection refused or timeout | Down | No application response is available because the demo container is stopped. |

## HTTP endpoints

Each running service exposes:

- `GET /health` — application status and dependency result
- `GET /metrics` — explicitly simulated CPU, memory, disk, and error values
- `GET /diagnostics` — demonstration diagnostic details

Healthy endpoints:

```text
http://100.103.92.83:18081/health
http://100.103.92.83:18082/health
http://100.103.92.83:18083/health
```

The ports bind specifically to the server's Tailscale address, not `0.0.0.0`.

## Project files

```text
app/server.py        Dependency-free HTTP demo application
app/statectl.py      Allowlisted healthy/degraded state writer
app/healthcheck.py   Direct loopback Docker health check
tests/               Local application tests
Dockerfile           Non-root Python container image
compose.yaml         Isolated three-service Compose stack
demo-control         Restricted demonstration controller
IMPLEMENTATION.md    Authoritative implementation handoff
uipath/               Authoritative UiPath project and import notes
```

## Server prerequisites

- Ubuntu host connected to Tailscale as `100.103.92.83`
- Docker Engine and Docker Compose
- Local user able to run Docker through `sudo`
- TCP ports `18081`, `18082`, and `18083` available on the Tailscale address

## Deploy the demo stack

From the Ubuntu server:

```bash
cd /home/tan/rpa-project
sudo docker compose up -d --build
sudo docker compose ps
```

All three containers should eventually show `healthy`.

## Safe demo controls

Run commands from `/home/tan/rpa-project`:

```bash
./demo-control status
./demo-control interactive
./demo-control degrade demo-beta
./demo-control recover demo-beta
./demo-control down demo-gamma
./demo-control start demo-gamma
./demo-control reset
```

The controller uses exact action and service allowlists:

- Only `demo-beta` may be degraded or recovered.
- Only `demo-gamma` may be stopped or started.
- Unknown names, extra arguments, and arbitrary container names are rejected.
- `reset` starts only these three demo services and sets their application states to healthy.

Because the local user does not have direct Docker socket access, Docker operations may prompt for the Ubuntu `sudo` password. Never place that password in this project.

## Interactive presentation dashboard

For a visual, keyboard-controlled demonstration, open a reasonably large SSH terminal
(approximately 100 columns by 28 rows) and run:

```bash
cd /home/tan/rpa-project
./demo-control interactive
```

The controller may request the Ubuntu `sudo` password once before opening the dashboard.
It uses an alternate terminal screen, refreshes automatically every two seconds, and restores
the normal terminal when you quit.

The dashboard deliberately observes the services through their Tailscale HTTP endpoints—the
same external view used by UiPath. It shows:

- Green, yellow, and red Healthy/Degraded/Down classifications
- HTTP status and measured round-trip time
- Simulated CPU, memory, disk, and error metrics
- Application dependency status and failure reason
- A five-event visual incident timeline with incident IDs and open-incident count
- Fault injection, detection, escalation, recovery action, and resolution events
- Measured incident duration when recovery is observed
- A short explanation of the last presentation action

Timeline colours and symbols are consistent with the service cards:

| Symbol | Meaning |
|---|---|
| Yellow `⚠` | Degraded incident opened |
| Red `✖` | Critical outage, escalation, or failed action |
| Cyan `▶` | Presenter action or recovery request |
| Green `✓` | Recovery observed and incident resolved |
| Grey `◆` | Informational session event |

Timeline data is held only in memory for the current interactive session. It is intended as a
live presentation aid; the UiPath CSV remains the persistent audit record.

Use a single key; Enter is not required:

| Key | Safe action | Expected visual result |
|---|---|---|
| `1` or `D` | Degrade `demo-beta` | Beta turns yellow, reports HTTP 503, and keeps responding |
| `2` or `H` | Recover `demo-beta` | Beta returns to green |
| `3` or `X` | Stop `demo-gamma` | Gamma turns red with no HTTP response |
| `4` or `S` | Start `demo-gamma` | Gamma returns to green when HTTP is ready |
| `R` | Reset the three demo services | Restores the healthy baseline |
| `Q` | Quit | Returns to the normal shell |

These controls retain the existing strict allowlist. They cannot accept arbitrary container
names or shell commands, and the dashboard does not expose Docker or any secret over the
network.

## Demonstration sequence

1. Establish the healthy baseline:

   ```bash
   ./demo-control reset
   ```

2. Open the presentation dashboard:

   ```bash
   ./demo-control interactive
   ```

3. Start the UiPath monitoring workflow on Windows.
4. Leave `demo-alpha` healthy as the control.
5. Press `1` or `D`; confirm beta turns yellow and UiPath classifies HTTP 503 as Degraded.
6. Press `3` or `X`; confirm gamma turns red and UiPath classifies the connection failure as Down.
7. Press `2` or `H`; confirm beta and UiPath record a recovery.
8. Press `4` or `S`; confirm gamma becomes reachable and UiPath records a recovery.
9. Press `R` to restore the healthy baseline.
10. After the Robot produces its final summary, press `Q` to exit the dashboard.

The workflow uses the UiPath Integration Service connection for warning, critical, escalation, and
recovery alerts. The send result is written to AlertSent; SMTP failures are logged and do not stop
the monitoring loop. Run Analyze File and the Windows transition tests before marking Phase 4
complete.

Runtime progress: a gamma hard-outage test has successfully produced a CRITICAL email for
Healthy → Down, including HTTP status 0, the connection-refused reason, the endpoint, timestamp,
and Run ID. Recovery, duplicate suppression, warning, and SMTP-failure tests remain to be closed.

## Manual endpoint checks

```bash
curl -i http://100.103.92.83:18081/health
curl -i http://100.103.92.83:18082/health
curl -i http://100.103.92.83:18083/health
```

When beta is degraded, its health endpoint intentionally returns HTTP 503 while its container remains running. Docker therefore marks that container `unhealthy`; this is expected. After recovery, the application responds immediately, while Docker's displayed health status may take one health-check interval to update.

Run the local tests with:

```bash
python3 -m unittest discover -s tests -v
docker compose -f compose.yaml config --quiet
bash -n demo-control
```

## Security and isolation

- No existing homelab service is used as a failure target.
- Ports are published only on the Tailscale address.
- The Docker socket and Docker API are not exposed remotely.
- Containers run as an unprivileged user with all Linux capabilities dropped.
- The root filesystem is read-only; only the small per-service state volume is writable.
- CPU, memory, and process limits constrain each demo container.
- Threshold violations are simulated values and do not exhaust host resources.
- Each service has a distinct state volume, and the stack has a uniquely named network.
- Credentials, Gmail connections, app passwords, tokens, and webhook URLs must never be committed.
- `.env`, logs, and future monitoring output are ignored by Git.

## UiPath Phase 3 results

The Windows workflow has been tested successfully:

- Three endpoints were polled in each cycle through Tailscale.
- An 18-cycle healthy run produced 54 Healthy checks with no false incidents.
- Degrading beta produced HTTP 503 and a `Healthy → Degraded` warning transition.
- The next degraded beta check produced no duplicate transition.
- CSV logs used a unique Run ID and recorded timestamps, service states, HTTP results,
  measured response times, reasons, and transitions.
- The final trace included totals, incident/recovery counts, incident timestamps, log path,
  and average response time per service.

The corrected active workflow currently resides on the Windows machine. The generated reference
archive under `uipath/` predates a manual UiPath Studio repair to an unrendered ErrorActivity;
see `uipath/generated/IMPORT.md` before reusing it.

## Stopping the demo stack

To stop only this Compose project while retaining its state volumes:

```bash
cd /home/tan/rpa-project
sudo docker compose stop
```

To start it again:

```bash
sudo docker compose start
./demo-control reset
```

Do not operate on unrelated containers during the demonstration.

## Next phase

Run UiPath Analyze File and the Windows transition tests for the SMTP implementation. Gmail
credentials must use a secure Windows/UiPath connection or credential store and must never be
placed in XAML, logs, screenshots, or repository files.

## SMTP implementation

The workflow uses UiPath.Mail.Activities with the configured UiPath Integration Service
connection. It sends transition-specific messages and records the activity result in AlertSent.
The connection remains machine/runtime configuration; no password or token is stored in the
project.
