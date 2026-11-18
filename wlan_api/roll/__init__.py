import fcntl
import os
import pathlib
import tempfile

STATE_FILE_NAME = "last_roll"


class RollStore:
    """Persists the highest roll number for which a voucher PDF was generated.

    The state is a single integer in a plain text file inside Flask's instance
    folder, so it survives deployments (the folder is not part of the checkout).
    If no state exists yet, ``start_roll`` is suggested as the next roll.
    """

    def __init__(self, directory, start_roll=1):
        self.path = pathlib.Path(directory) / STATE_FILE_NAME
        self.lock_path = self.path.with_suffix(".lock")
        self.start_roll = start_roll

    def last_roll(self):
        try:
            return int(self.path.read_text().strip())
        except FileNotFoundError:
            return None

    def next_roll(self):
        last = self.last_roll()
        if last is None:
            return self.start_roll
        return max(last + 1, self.start_roll)

    def is_used(self, roll):
        last = self.last_roll()
        return last is not None and roll <= last

    def record(self, roll):
        """Remember ``roll`` as generated, never lowering the stored value."""
        with open(self.lock_path, "w") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            last = self.last_roll()
            if last is not None and last >= roll:
                return
            fd, tmp = tempfile.mkstemp(dir=self.path.parent, prefix=".last_roll.")
            with os.fdopen(fd, "w") as f:
                f.write(f"{roll}\n")
            os.replace(tmp, self.path)
