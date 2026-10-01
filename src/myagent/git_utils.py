import subprocess
from pathlib import Path
from typing import Tuple

CHECKPOINT_FLAG_FILE = ".myagent_checkpoint_created"

def is_git_repo(workdir: Path) -> bool:
    r = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], cwd=workdir, capture_output=True, text=True)
    return r.returncode == 0

def create_checkpoint(workdir: Path) -> Tuple[bool, str]:
    if not is_git_repo(workdir):
        return False, "Not a git repository."
    r = subprocess.run(["git", "stash", "create"], cwd=workdir, capture_output=True, text=True)
    commit_hash = r.stdout.strip()
    if commit_hash:
        subprocess.run(["git", "stash", "store", "-m", "myagent-checkpoint", commit_hash], cwd=workdir, capture_output=True)
        flag_path = workdir / ".myagent" / CHECKPOINT_FLAG_FILE
        flag_path.parent.mkdir(parents=True, exist_ok=True)
        flag_path.write_text(commit_hash)
        return True, commit_hash
    return True, "No local uncommitted changes to stash."

def undo_checkpoint(workdir: Path) -> Tuple[bool, str]:
    if not is_git_repo(workdir):
        return False, "Not a git repository."
    flag_path = workdir / ".myagent" / CHECKPOINT_FLAG_FILE
    if not flag_path.exists():
        return False, "No checkpoint was created by myagent in this session."

    r = subprocess.run(["git", "stash", "pop"], cwd=workdir, capture_output=True, text=True)
    flag_path.unlink(missing_ok=True)
    if r.returncode == 0:
        return True, "Successfully restored state from myagent git checkpoint."
    return False, f"Git undo failed: {r.stderr.strip()}"
