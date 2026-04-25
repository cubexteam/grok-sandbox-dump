# grok-sandbox-dump

> 🔍 Analysis of the Grok (xAI) code execution sandbox — system files, container configuration, and Python REPL internals.

📖 [Читать на русском](README_RU.md)

---

## What is this?

This repository contains a dump of the internal code execution environment used by **Grok** (xAI). The files were obtained from inside the container where Grok runs user Python code. The dump includes system files, environment configuration, and the source code of the Python REPL server.

---

## Contents

```
application.zip
├── pyrepl.py               # Grok's Python REPL server (source code)
├── os-release              # OS version
├── issue                   # /etc/issue
├── passwd                  # System users
├── hosts                   # /etc/hosts
├── resolv.conf             # DNS configuration
├── .bashrc_from_root       # root user .bashrc
├── group                   # System groups
├── profile                 # /etc/profile
├── proc/
│   ├── version             # Linux kernel version
│   ├── mounts              # Mounted filesystems
│   ├── cgroup              # Container cgroup hierarchy
│   └── cmdline             # Init process command line
└── extra/
    ├── shadow              # /etc/shadow (password hashes)
    ├── .profile            # User profile
    ├── environment         # Environment variables
    ├── cpuinfo             # /proc/cpuinfo
    ├── meminfo             # /proc/meminfo
    ├── sources.list        # APT package sources
    └── hostname            # Hostname
```

---

## Environment Overview

### Operating System
| Parameter | Value |
|---|---|
| OS | Ubuntu 24.04.4 LTS (Noble Numbat) |
| Kernel | Linux 4.4.0 (virtualized) |
| Hostname | `localhost.localdomain` |

### Hardware (virtual)
| Parameter | Value |
|---|---|
| CPU | Intel Sapphire Rapids (model 143) |
| vCPU | 2 cores @ 2699 MHz |
| L2 cache | 8192 KB |
| RAM | 2 GB |
| Swap | None |

### Containerization
| Parameter | Value |
|---|---|
| Filesystem | overlay (read-write) |
| Init process | `catatonit -P` (from `/hades-container-tools/`) |
| cgroup prefix | `/hds-*` (hades) |
| Virtual volumes | 9p protocol (Plan 9 filesystem) |
| Isolation | cgroups v1: cpu, cpuacct, cpuset, memory, pids, devices |

### Mounts (selected)
```
none /                      overlay   rw
none /dev                   dev       rw,nosuid
none /sys                   sysfs     ro,noexec,nosuid
none /proc                  proc      rw,noexec,nosuid
none /etc/hosts             9p        ro
none /README.xai            9p        ro       ← xAI artifact
none /hades-container-tools 9p        ro       ← "Hades" infrastructure
```

---

## pyrepl.py — Grok's Python REPL

The most interesting find: the source code of the server Grok uses to execute Python code.

### How it works

```
stdin → JSON → PyRepl.line() → exec() → JSON → stdout
```

1. Reads commands from stdin line by line in JSON format
2. Supports two commands: `{"ping": ...}` and `{"eval": "<code>"}`
3. Executes code via `exec()` in a shared `locals` dict (state persists between calls)
4. Captures stdout/stderr via `contextlib.redirect_*`
5. Returns result as JSON: `{"ret": ..., "stdout": ..., "stderr": ...}`

### Protocol example

```json
// Request
{"eval": "x = 42\nx * 2"}

// Response
{"ret": "84", "stdout": "", "stderr": ""}

// Ping/pong
{"ping": 1} → {"pong": 17}
```

### Implementation notes

- State is preserved between calls (`self.locals` is a shared dict)
- AST parsing before `exec` — the last expression automatically becomes the return value (`_ret`)
- Syntax and runtime errors are returned in the `pyerror` field with a full traceback

---

## Infrastructure Findings

- The internal project is called **"Hades"** (`/hades-container-tools`, cgroup prefix `hds-`)
- `/README.xai` is mounted as a separate 9p volume — likely contains environment docs or metadata
- The environment is fully isolated: no swap, no network (DNS only via 9p), read-only `/sys`
- Kernel 4.4.0 is intentionally old — typical for hypervisor environments with custom patches

---

## Disclaimer

This repository is for research and educational purposes only. No credentials, tokens, or private user data are included. The analysis is based on publicly available Linux containerization principles.
