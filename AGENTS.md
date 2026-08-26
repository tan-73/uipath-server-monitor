# Repository Agent Instructions

## Project model

This repository coordinates a cross-platform UiPath health-monitor project.

- Linux runs the isolated Docker demo stack.
- Windows runs UiPath Studio/Robot and monitors Linux over Tailscale HTTP.
- GitHub is the source-control handoff between both machines.
- Git synchronizes files, not running containers, UiPath processes, Docker volumes, or runtime state.

Keep responsibilities separate. Linux must not run the UiPath workflow, and Windows must not receive Docker socket or host-control access for monitoring.

## Repository layout

- `app/`, `Dockerfile`, `compose.yaml`: Linux demo services and container configuration.
- `demo-control`: allowlisted Linux demonstration controller.
- `tests/`: server-side tests.
- `uipath/ServerMonitorPhase3/`: authoritative UiPath project.
- `README.md`, `DEMO.md`, `IMPLEMENTATION.md`: project documentation.

The UiPath project entry point is `uipath/ServerMonitorPhase3/project.json`, and its main workflow is `uipath/ServerMonitorPhase3/Main.xaml`. Do not use deleted legacy files or recreate the former `uipath/generated/` layout unless explicitly requested.

## Git collaboration workflow

Before editing on either machine, run `git pull --rebase origin main`.

After editing and testing:

    git status
    git add <specific-files>
    git commit -m "Describe the change"
    git push origin main

Do not edit the same files concurrently on Windows and Linux. Push Windows UiPath changes before pulling them on Linux; pull Linux application changes on Windows before editing shared documentation or configuration. Resolve conflicts deliberately. Never force-push or use destructive resets to hide conflicts.

Fetching remote refs does not update the working tree. Use `git pull --ff-only origin main` when the local checkout has no local commits and should be updated to the remote branch.

## Windows / UiPath procedure

Use the cloned repository as the source-controlled location for the UiPath project. Open `<clone>\\uipath\\ServerMonitorPhase3\\project.json`.

After Studio changes:

1. Run UiPath Analyze File.
2. Run the workflow against the healthy demo stack.
3. Test degraded, down, and recovery transitions when appropriate.
4. Do not commit generated monitoring CSV logs or temporary Studio files.
5. Commit and push the UiPath project and intentional documentation changes.

UiPath credentials and mail connections belong in Windows Credential Manager, UiPath Assets, Orchestrator, or another secure runtime mechanism. Never place Gmail passwords, tokens, Tailscale keys, or connection secrets in XAML, JSON, `.env`, logs, or Git history.

## Linux server procedure

The Linux checkout deploys only the server-side demo stack:

    cd /home/tan/rpa-project
    git pull --rebase origin main
    python3 -m unittest discover -s tests -v
    bash -n demo-control
    docker compose -f compose.yaml config --quiet
    sudo docker compose up -d --build

Use `demo-control` for demonstration actions. Do not stop, reconfigure, expose, or load-test unrelated homelab services. Preserve the Tailscale-only port bindings and Docker isolation controls in `compose.yaml`.

## Safe change boundaries

- Monitoring is HTTP polling from Windows to Linux.
- Linux must not expose the Docker socket or an unauthenticated Docker API.
- Server changes must remain under this repository and must not modify unrelated services.
- Keep secrets, logs, caches, backups, archives, and machine-specific files ignored by Git.
- Validate server tests and Compose configuration on Linux; validate UiPath with Analyze File and runtime tests on Windows.
- Treat the UiPath workflow and Linux demo stack as separate deployable components connected by documented HTTP endpoints.
