# UiPath Homelab Health Monitor — Implementation Handoff

## Status

Updated 2026-08-21 after the interactive presentation dashboard was tested successfully.

| Work item | Status |
|---|---|
| Phase 1 — prerequisites | Complete |
| Phase 2 — isolated Docker demo stack | Complete |
| Phase 3 — UiPath monitor | Complete and tested from Windows |
| Interactive presentation CLI | Complete and user-tested |
| Phase 4 — Gmail alerts and final reporting | Awaiting user go-ahead |
| Phase 5 — rehearsal and final documentation | Not started |

This document remains the authoritative handoff for continuing the build. Phase 4 must not
begin until the user explicitly gives the go-ahead. Preserve the existing demo behavior and
all unrelated homelab services.

## Project objective

Build a college RPA project that demonstrates a UiPath Robot monitoring a real Linux homelab from a Windows computer.

The demonstration must show:

1. Multiple services operating normally.
2. One service becoming degraded while its container remains running.
3. A different service becoming completely unavailable because its container is stopped.
4. UiPath detecting and classifying each state.
5. Transition-based warning, critical, and recovery alerts.
6. A timestamped monitoring log and a final health summary.

## Environment

### Windows monitoring machine

- UiPath Studio Community `2026.0.200 STS` is installed.
- The project is a modern Windows/VB project.
- `UiPath.WebAPI.Activities 2.5.2` and `UiPath.System.Activities 26.6.3` are installed.
- The Windows computer will run the UiPath workflow during the demonstration.
- Tailscale reachability to `100.103.92.83` has been confirmed from Windows.
- The selected Phase 4 alert destination is Gmail email.

### Homelab server

- Host: Lenovo IdeaPad 510-15IKB
- OS: Ubuntu 24.04 LTS, x86-64
- CPU: Intel Core i5-7200U, 2 cores / 4 threads
- RAM: approximately 7.7 GiB
- Root storage: approximately 457 GiB, with over 400 GiB free at last inspection
- Tailscale address: `100.103.92.83`
- Docker Engine `29.2.1` and Docker Compose `v5.1.0` were confirmed.
- Python 3.12, Java 21, Node.js 18, npm 9, and FFmpeg are installed on the host.
- The server already runs many production-like personal services. The demo must remain isolated from them.

## Safety boundaries

- Do not stop, degrade, reconfigure, or load-test existing homelab services.
- Do not expose the Docker socket or unauthenticated Docker API to the Windows computer.
- Do not cause genuine CPU, RAM, storage, or network exhaustion. Simulate threshold violations in demo responses.
- Bind demo ports to the Tailscale address, not `0.0.0.0`, unless the user explicitly approves a different exposure model.
- Do not put webhook URLs, tokens, machine keys, or credentials in Git-tracked files.
- Store secrets in an ignored `.env` file or UiPath/Orchestrator assets.
- Use unique project, container, volume, network, and port names to avoid collisions with existing stacks.
- Keep all server-side project files under `/home/tan/rpa-project`.

## Implemented architecture

```text
Windows computer
└── UiPath Studio / Robot
    ├── Polls service health over Tailscale HTTP
    ├── Parses JSON responses
    ├── Classifies service state
    ├── Tracks previous state
    ├── Writes monitoring results
    └── Sends warning, critical, and recovery alerts (Phase 4)
             │
             │ Tailscale
             ▼
Ubuntu homelab: 100.103.92.83
└── Isolated Docker Compose demo stack
    ├── demo-alpha: baseline healthy service
    ├── demo-beta: controllable degraded service
    └── demo-gamma: controllable hard-failure service
└── Local interactive presentation CLI
    ├── Observes the same Tailscale HTTP endpoints as UiPath
    └── Invokes only allowlisted demo actions
```

The Windows Robot should infer application availability from HTTP behavior. It does not require Docker access.

## Server-side demo stack

Three lightweight HTTP services share one application image while using distinct service names
and state volumes. The Compose project is named `uipath-homelab-monitor`.

The ports were collision-checked before deployment and bind only to the server's Tailscale
address:

| Service | Tailscale endpoint | Primary role |
|---|---|---|
| `demo-alpha` | `http://100.103.92.83:18081` | Remains healthy as a control |
| `demo-beta` | `http://100.103.92.83:18082` | Changes between healthy and degraded |
| `demo-gamma` | `http://100.103.92.83:18083` | Is stopped to demonstrate a hard outage |

Each running service should expose:

- `GET /health`
- `GET /metrics`
- `GET /diagnostics`

### Expected health behavior

Healthy:

```http
HTTP/1.1 200 OK
Content-Type: application/json
```

```json
{
  "service": "demo-beta",
  "status": "healthy",
  "timestampUtc": "2026-01-01T00:00:00Z",
  "responseTimeMs": 12,
  "dependency": "connected",
  "message": "All checks passed"
}
```

Degraded:

```http
HTTP/1.1 503 Service Unavailable
Content-Type: application/json
```

```json
{
  "service": "demo-beta",
  "status": "degraded",
  "timestampUtc": "2026-01-01T00:00:00Z",
  "responseTimeMs": 1500,
  "dependency": "unavailable",
  "message": "Simulated dependency failure"
}
```

Down:

- The target container is stopped.
- The Robot receives connection refused or a timeout.
- There is no fabricated HTTP response for this state.

### Simulated metrics

The metrics response can contain realistic-looking demonstration values:

```json
{
  "cpuPercent": 18.4,
  "memoryPercent": 42.1,
  "diskPercent": 31.7,
  "errorCount": 0
}
```

When a service is degraded, one or more values may cross configured warning thresholds. These are simulated values and must not result from actual resource exhaustion.

## Demo controller

The implemented server-side controller supports:

```bash
./demo-control status
./demo-control interactive
./demo-control degrade demo-beta
./demo-control recover demo-beta
./demo-control down demo-gamma
./demo-control start demo-gamma
./demo-control reset
```

Requirements:

- `degrade` changes application state without stopping its container.
- `recover` returns the running application to healthy state.
- `down` stops only the explicitly named demo container.
- `start` starts only the explicitly named demo container.
- `reset` returns all demo services to a known healthy state.
- Reject unknown service names and unsafe arguments.
- Never accept arbitrary container names or shell fragments.

### Interactive presentation mode

`./demo-control interactive` opens an `htop`-inspired, keyboard-controlled terminal
dashboard. It refreshes every two seconds and shows colored classifications, HTTP status,
round-trip time, simulated metric bars, dependency details, and a five-event visual incident
timeline.

The session timeline assigns incident IDs such as `INC-001`, counts currently open incidents,
records presenter actions, distinguishes warning and critical events, records escalation from
Degraded to Down, and closes an incident with its observed duration when the service returns to
Healthy. Timeline events are intentionally held only in memory; UiPath's CSV is the persistent
monitoring record.

| Key | Action |
|---|---|
| `1` or `D` | Degrade only `demo-beta` |
| `2` or `H` | Recover only `demo-beta` |
| `3` or `X` | Stop only `demo-gamma` |
| `4` or `S` | Start only `demo-gamma` |
| `R` | Reset the isolated three-service stack |
| `Q` | Exit and restore the normal terminal |

The user confirmed this mode works. It uses HTTP for observation and does not expose Docker,
credentials, or control endpoints over the network.

## Implemented UiPath workflow

The monitor is implemented as a modern Windows/VB UiPath process.

Installed packages:

- `UiPath.WebAPI.Activities 2.5.2`
- `UiPath.System.Activities 26.6.3`

Core workflow:

```text
Main
├── Load configuration and monitored-service list
├── Initialize previous-state dictionary
├── While monitoring is enabled
│   ├── For Each service
│   │   ├── Start response timer
│   │   ├── Try
│   │   │   ├── HTTP Request: GET /health
│   │   │   ├── Capture status code and body
│   │   │   ├── Deserialize JSON
│   │   │   └── Classify Healthy or Degraded
│   │   ├── Catch timeout/connection exception
│   │   │   └── Classify Down
│   │   ├── Compare current state with previous state
│   │   ├── Write timestamped result
│   │   ├── Mark an alert only on a meaningful transition
│   │   └── Update previous-state dictionary
│   └── Delay for configured polling interval
└── Generate final summary
```

Suggested monitoring interval:

- Live demonstration: 10 seconds
- Normal scheduled use: 1–5 minutes

The tested demonstration configuration used 10-second polling. The workflow successfully
completed an 18-cycle healthy run with 54 healthy checks, then a separate degraded-state test
correctly detected `demo-beta` as Degraded from HTTP 503 and suppressed its duplicate alert
transition on the following cycle.

The active corrected workflow is on the user's Windows machine. A generated reference project
and import notes are retained under `uipath/generated/`. The initially generated XAML required
a manual UiPath Studio repair: an unrendered `ErrorActivity` beneath “Record Request Start”
was replaced with a proper Try Catch containing a `System.Exception` catch. Do not assume the
archived generated XAML includes that Windows-side repair unless the corrected project is copied
back into this repository.

## State-transition alert rules

| Previous state | Current state | Action |
|---|---|---|
| Unknown | Healthy | Log initialization; no incident alert |
| Healthy | Degraded | Send warning alert |
| Healthy | Down | Send critical alert |
| Degraded | Degraded | Log only; suppress duplicate alert |
| Degraded | Down | Send critical escalation |
| Down | Down | Log only; suppress duplicate alert |
| Degraded | Healthy | Send recovery alert |
| Down | Healthy | Send recovery alert |

Optionally require two consecutive failed checks before declaring an outage. During the college presentation, make this configurable so detection remains quick.

## Alert destination

The user selected email, preferably Gmail. The exact supported Gmail activity or connection
method must be confirmed in UiPath Studio at the start of Phase 4.

Before implementing alerts:

1. Inspect the mail activities available in UiPath Studio Community `2026.0.200 STS`.
2. Choose a supported secure Gmail connection method.
3. Store credentials in a secure Windows/UiPath credential store, never in XAML or this repository.
4. Redact email addresses and authentication details from screenshots and logs when appropriate.

Every alert should include:

- Service name
- Previous and current state
- UTC timestamp
- Endpoint
- HTTP status or exception category
- Failure reason
- Severity
- Run or correlation identifier

## Logs and final report

The Robot currently produces a unique per-run CSV log with:

```text
TimestampUtc,Service,PreviousState,CurrentState,HttpStatus,ResponseTimeMs,Reason,AlertSent,TransitionAction,RunId
```

Until Phase 4 is implemented, `AlertSent` remains `False`; `TransitionAction` records values
such as `WarningPending`, `CriticalPending`, `CriticalEscalationPending`, and
`RecoveryPending`.

The current trace summary shows:

- Total checks
- Healthy checks
- Degraded checks
- Down checks
- Incident count
- Recovery count
- Average response time per service
- First and last incident timestamps

Phase 4 will turn the transition results into real Gmail messages and polish the final report
into a presentation-ready artifact.

## Final demonstration sequence

1. Reset all services to healthy.
2. Start the UiPath workflow on Windows.
3. Show three successful health checks.
4. Open `./demo-control interactive` and press `1` or `D`.
5. Show UiPath detecting HTTP 503 and sending a warning.
6. Press `3` or `X` to stop `demo-gamma`.
7. Show UiPath catching a connection failure and sending a critical alert.
8. Keep `demo-alpha` healthy to prove the monitor remains operational.
9. Press `2` or `H` to recover beta, then `4` or `S` to start gamma.
10. Show recovery notifications and the final report.
11. Press `R` to restore the healthy baseline, then `Q` to exit.

## Implementation phases

### Phase 1 — Verify prerequisites

Status: **Complete.**

- Confirm UiPath Studio edition and version on Windows.
- Confirm Windows can reach `100.103.92.83` over Tailscale.
- Check proposed server ports for collisions.
- Confirm Docker Compose access and existing project naming.
- Select the alert destination.

### Phase 2 — Build the isolated server stack

Status: **Complete.**

- Create the demo application.
- Add Dockerfile and Compose configuration.
- Add Docker health checks.
- Bind ports only to the Tailscale address.
- Implement controlled state changes.
- Add the safe `demo-control` command.
- Test healthy, degraded, down, and recovered behavior using `curl`.

### Phase 3 — Build the UiPath monitor

Status: **Complete and tested from Windows.**

- Create service configuration.
- Implement HTTP polling and timeout handling.
- Parse JSON responses.
- Implement state classification and transition tracking.
- Write structured logs.
- Test against all demo states.

### Phase 4 — Add alerts and reporting

Status: **Not started; waiting for explicit user approval.**

- Configure Gmail securely without embedding credentials in the workflow.
- Connect existing transition values to warning, critical, escalation, and recovery emails.
- Preserve the existing duplicate suppression for unchanged unhealthy states.
- Include service, endpoint, previous/current state, severity, UTC timestamp, HTTP status or
  exception, reason, and Run ID in each message.
- Generate a presentation-ready final report from the existing counters and per-service averages.
- Test warning, hard-down, escalation where applicable, recovery, and duplicate suppression.

### Phase 5 — Rehearse and document

- Write a repeatable demonstration runbook.
- Capture screenshots of each state and alert.
- Document architecture, activity choices, security controls, limitations, and future improvements.
- Verify `reset` restores the stack after every rehearsal.

## Acceptance criteria

- All three services are simultaneously reachable in the healthy state.
- Degrading `demo-beta` leaves its container running but changes `/health` to HTTP 503.
- Stopping `demo-gamma` produces a connection failure from Windows.
- `demo-alpha` remains healthy throughout the incident demonstration.
- UiPath correctly distinguishes Healthy, Degraded, and Down.
- Duplicate alerts are suppressed while a state remains unchanged.
- Recovery alerts are produced when services return to healthy.
- Logs and summary contain correct timestamps and service names.
- No existing homelab service is modified or interrupted.
- No Docker API, webhook secret, or privileged host interface is exposed.

## Next authorized task

Wait for the user's explicit Phase 4 go-ahead. Then inspect the mail activities and secure
connection choices visible in the user's UiPath Studio installation before editing the workflow.
Do not deploy another container, expose a control API, modify unrelated homelab services, or
store Gmail credentials in project files.
