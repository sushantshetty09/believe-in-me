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

    # Record current HEAD commit hash
    r_head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=workdir, capture_output=True, text=True)
    head_hash = r_head.stdout.strip() if r_head.returncode == 0 else ""

    # Attempt to create stash for uncommitted changes
    r_stash = subprocess.run(["git", "stash", "create"], cwd=workdir, capture_output=True, text=True)
    stash_hash = r_stash.stdout.strip()
    if stash_hash:
        subprocess.run(["git", "stash", "store", "-m", "myagent-checkpoint", stash_hash], cwd=workdir, capture_output=True)

    flag_path = workdir / ".myagent" / CHECKPOINT_FLAG_FILE
    flag_path.parent.mkdir(parents=True, exist_ok=True)
    flag_data = f"head:{head_hash}\nstash:{stash_hash}"
    flag_path.write_text(flag_data)

    return True, stash_hash or head_hash

def undo_checkpoint(workdir: Path) -> Tuple[bool, str]:
    if not is_git_repo(workdir):
        return False, "Not a git repository."
    flag_path = workdir / ".myagent" / CHECKPOINT_FLAG_FILE
    if not flag_path.exists():
        return False, "No checkpoint was created by myagent in this session."

    content = flag_path.read_text().splitlines()
    data = {}
    for line in content:
        if ":" in line:
            k, v = line.split(":", 1)
            data[k.strip()] = v.strip()

    # Revert working tree changes made by agent
    r_clean = subprocess.run(["git", "checkout", "--", "."], cwd=workdir, capture_output=True, text=True)
    subprocess.run(["git", "clean", "-fd"], cwd=workdir, capture_output=True)

    stash_hash = data.get("stash", "")
    if stash_hash:
        subprocess.run(["git", "stash", "pop"], cwd=workdir, capture_output=True)

    flag_path.unlink(missing_ok=True)
    return True, "Successfully restored state to pre-agent checkpoint."
