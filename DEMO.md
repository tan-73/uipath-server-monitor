# UiPath Homelab Health Monitor — Demo Guide

## Command and key reference

| Command/key | Action |
|---|---|
| `./demo-control reset` | Restore all three services to Healthy |
| `./demo-control interactive` | Open the visual presentation dashboard |
| `D` or `1` | Degrade Beta: running application returns HTTP 503 |
| `X` or `3` | Stop Gamma: complete outage |
| `H` or `2` | Recover Beta |
| `S` or `4` | Start and recover Gamma |
| `R` | Reset all services from inside the dashboard |
| `Q` | Quit the dashboard |

Dashboard keys work immediately; do not press Enter.

## Before presenting

1. Confirm Tailscale is connected on Windows and Ubuntu.
2. In UiPath, use approximately **14 cycles** and a **5-second interval**.
3. Make the UiPath Output panel large and readable.
4. Reset and open the dashboard:

   ```bash
   cd /home/tan/rpa-project
   ./demo-control reset
   ./demo-control interactive
   ```

5. Arrange the dashboard on the left and UiPath Studio on the right.

## Live demonstration

### 1. Introduce the system

> UiPath on Windows monitors three isolated services on my Ubuntu homelab over Tailscale. The CLI is a safe scenario controller and visual observer; UiPath performs the actual monitoring, classification, logging, and reporting.

Point out the security controls: no Docker API is exposed, existing homelab services are untouched, and resource metrics are simulated.

### 2. Show the healthy baseline

Start the UiPath workflow. Show Alpha, Beta, and Gamma in green and wait for two complete cycles.

Alpha remains the healthy control throughout the demonstration.

### 3. Degrade Beta

After Cycle 2, press `D`.

Show:

- Beta turning yellow
- HTTP 503 and dependency failure
- A warning incident opening in the timeline
- UiPath reporting `Healthy → Degraded` and `WarningPending`

Wait for one more check and point out `Transition=None`, proving duplicate suppression.

### 4. Stop Gamma

After Cycle 4, press `X`.

Show:

- Gamma turning red with no HTTP response
- A critical incident opening in the timeline
- Alpha remaining green
- UiPath reporting `Healthy → Down` and `CriticalPending`

Explain that Beta is a reachable application failure, while Gamma is a complete outage.

### 5. Recover both services

After Cycle 6, press `H` to recover Beta. After Cycle 8, press `S` to start Gamma.

Show both services returning to green, the timeline resolving each incident with its duration, and UiPath reporting `RecoveryPending`.

### 6. Show the result

When UiPath finishes, highlight:

- Healthy, Degraded, and Down totals
- Incident and recovery counts
- Average response time per service
- The generated CSV log and Run ID

Finish with:

> Phases 1–3 and the visual presentation layer are complete. Phase 4 will add secure Gmail alerts and a presentation-ready incident report.

## Action schedule

| After cycle | Action |
|---:|---|
| 2 | Press `D` |
| 4 | Press `X` |
| 6 | Press `H` |
| 8 | Press `S` |
| End | Show summary, then press `R` and `Q` |

## Visual story

```text
ALL GREEN → BETA YELLOW → GAMMA RED → ALL GREEN
```

## Backup

Before presenting, record one successful run and retain screenshots of the Healthy, Degraded, Down, and Recovered states, plus one previous CSV log and final UiPath summary.
