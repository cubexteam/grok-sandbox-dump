# grok-sandbox-dump

> 🔍 Анализ изолированной среды выполнения кода Grok (xAI) — системные файлы, конфигурация контейнера и Python REPL.

---

## Что это такое

Этот репозиторий содержит дамп внутренней среды выполнения кода **Grok** (xAI). Файлы были получены изнутри контейнера, в котором Grok запускает пользовательский Python-код. Дамп включает системные файлы, информацию об окружении и исходный код Python REPL-сервера.

---

## Содержимое

```
application.zip
├── pyrepl.py               # Python REPL-сервер Grok (исходный код)
├── os-release              # Версия ОС
├── issue                   # /etc/issue
├── passwd                  # Пользователи системы
├── hosts                   # /etc/hosts
├── resolv.conf             # DNS-конфигурация
├── .bashrc_from_root       # .bashrc root-пользователя
├── group                   # Группы системы
├── profile                 # /etc/profile
├── proc/
│   ├── version             # Версия ядра Linux
│   ├── mounts              # Смонтированные файловые системы
│   ├── cgroup              # cgroup-иерархия контейнера
│   └── cmdline             # Командная строка init-процесса
└── extra/
    ├── shadow              # /etc/shadow (хэши паролей)
    ├── .profile            # Профиль пользователя
    ├── environment         # Переменные окружения
    ├── cpuinfo             # /proc/cpuinfo
    ├── meminfo             # /proc/meminfo
    ├── sources.list        # APT-источники пакетов
    └── hostname            # Имя хоста
```

---

## Характеристики среды

### Операционная система
| Параметр | Значение |
|---|---|
| ОС | Ubuntu 24.04.4 LTS (Noble Numbat) |
| Ядро | Linux 4.4.0 (виртуализированное) |
| Hostname | `localhost.localdomain` |

### Железо (виртуальное)
| Параметр | Значение |
|---|---|
| CPU | Intel Sapphire Rapids (model 143) |
| vCPU | 2 ядра @ 2699 MHz |
| L2 cache | 8192 KB |
| RAM | 2 GB |
| Swap | Нет |

### Контейнеризация
| Параметр | Значение |
|---|---|
| Файловая система | overlay (read-write) |
| Init-процесс | `catatonit -P` (из `/hades-container-tools/`) |
| cgroup prefix | `/hds-*` (hades) |
| Виртуальные тома | 9p-протокол (Plan 9 filesystem) |
| Изоляция | cgroups v1: cpu, cpuacct, cpuset, memory, pids, devices |

### Монтирования (выборка)
```
none /           overlay   rw
none /dev        dev       rw,nosuid
none /sys        sysfs     ro,noexec,nosuid
none /proc       proc      rw,noexec,nosuid
none /etc/hosts  9p        ro
none /README.xai 9p        ro       ← артефакт xAI
none /hades-container-tools 9p ro   ← инфраструктура "Hades"
```

---

## pyrepl.py — Python REPL Grok

Ключевая находка: исходный код сервера, который Grok использует для выполнения Python-кода.

### Принцип работы

```
stdin → JSON → PyRepl.line() → exec() → JSON → stdout
```

1. Читает команды из stdin построчно в формате JSON
2. Поддерживает две команды: `{"ping": ...}` и `{"eval": "<код>"}`
3. Выполняет код через `exec()` в разделяемом `locals`-словаре (состояние сохраняется между вызовами)
4. Перехватывает stdout/stderr через `contextlib.redirect_*`
5. Возвращает результат в JSON: `{"ret": ..., "stdout": ..., "stderr": ...}`

### Пример протокола

```json
// Запрос
{"eval": "x = 42\nx * 2"}

// Ответ
{"ret": "84", "stdout": "", "stderr": ""}

// Ping/pong
{"ping": 1} → {"pong": 17}
```

### Особенности реализации

- Состояние сохраняется между вызовами (`self.locals` — общий словарь)
- AST-парсинг перед `exec` — последнее выражение автоматически становится возвращаемым значением (`_ret`)
- Ошибки синтаксиса и runtime возвращаются в поле `pyerror` с полным traceback

---

## Инфраструктурные выводы

- Проект называется **"Hades"** (`/hades-container-tools`, cgroup prefix `hds-`)
- Файл `/README.xai` монтируется как отдельный 9p-том — вероятно, содержит документацию или метаданные среды
- Среда полностью изолирована: нет swap, нет сети (только DNS через 9p), read-only /sys
- Ядро 4.4.0 — старое, что типично для гипервизорных сред с собственным патчем

---

## Disclaimer

Данный репозиторий создан исключительно в исследовательских целях. Никаких учётных данных, токенов или приватной информации пользователей не содержится. Анализ проводился на основе публично доступных и общеизвестных принципов контейнеризации Linux.
