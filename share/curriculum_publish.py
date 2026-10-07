"""Publish only between operator lessons; never truncate the installed JSON."""

import fcntl
import os
from pathlib import Path
import tempfile


def operator_session_lock():
    root = Path(os.environ.get("XDG_STATE_HOME", str(Path.home() / ".local/state")))
    return root / "vim-daily" / ".v2-session.lock"


def operator_session_locks():
    # A generator invoked with isolated XDG state still publishes the installed
    # repository JSON. It must not ignore the normal operator's active lesson.
    configured = operator_session_lock()
    standard = Path.home() / ".local/state/vim-daily/.v2-session.lock"
    return list(dict.fromkeys([configured, standard]))


def publish(path, text, *, lock_path=None):
    """Hold a read-only shared session lock across the atomic replacement.

    A stale pathname is harmless. An actual exclusive session owner refuses
    publication. The default checks the configured operator state. Tests pass
    an explicit isolated lock path. Every required lock must already exist;
    otherwise first-session lock creation could race publication. It never
    creates or modifies a learner lock.
    """
    path = Path(path)
    lock_paths = [Path(lock_path)] if lock_path is not None else operator_session_locks()
    handles = []
    temporary = None
    try:
        for candidate in lock_paths:
            try:
                handle = candidate.open("rb")
            except FileNotFoundError:
                raise RuntimeError("No operator session lock exists at %s; installed curriculum publication is refused." % candidate)
            handles.append(handle)
            try:
                fcntl.flock(handle, fcntl.LOCK_SH | fcntl.LOCK_NB)
            except BlockingIOError:
                raise RuntimeError("An operator lesson is active; curriculum publication is refused. Close the lesson before regeneration.")
        if not handles:
            # Refuse unguarded publication rather than race a first lesson.
            raise RuntimeError("No operator session lock exists; installed curriculum publication is refused.")
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         prefix=".curriculum-publish-", delete=False) as output:
            temporary = Path(output.name)
            output.write(text)
            output.flush()
            os.fsync(output.fileno())
        os.chmod(temporary, path.stat().st_mode & 0o777 if path.exists() else 0o644)
        os.replace(temporary, path)
        temporary = None
    finally:
        if temporary is not None:
            temporary.unlink()
        for handle in handles:
            handle.close()
