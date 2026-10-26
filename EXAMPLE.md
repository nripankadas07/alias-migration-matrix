# Reproduce a useful result

Follow the installation command in [the README](README.md), then run the supplied example. counts.VALUE_CHANGED is 1. In that case old.values.asset ends in :0 and new.values.asset ends in :1. The ordinary one-key payloads remain accepted.

The input is a bounded JSON scenario. [The core API](alias_migration_matrix.py) contains the exact accepted fields and validation bounds. [Tests](test_core.py) include concrete expected outputs and failure cases. The CLI reads at most1 MiB and emits escaped HTML when `--html` is supplied. It runs locally without a service account.

The example is synthetic. The diagnostic returns exit 0 even when it finds a problem. Invalid input returns 2; runtime/library errors can raise an exception. Inspect the finding fields, not just the exit status.

The installed-wheel check copies examples into a temporary working directory and invokes the installed command there. Supported CI configurations are Linux with Python 3.12 and 3.13 against the exact pinned upstream dependency. No Windows/macOS claim or fair performance comparison is made.
