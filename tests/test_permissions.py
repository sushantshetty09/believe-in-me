import pytest
from myagent.permissions import PermissionManager, PermissionLevel

def test_permission_levels():
    pm = PermissionManager(auto_approve_all=False)

    # Auto allow read-only
    p1, _ = pm.check_tool_permission("read_file", {"path": "a.txt"})
    assert p1 == PermissionLevel.AUTO_ALLOW

    # Ask for modifications
    p2, _ = pm.check_tool_permission("write_file", {"path": "a.txt", "content": "hi"})
    assert p2 == PermissionLevel.ASK

    # Block dangerous commands
    p3, _ = pm.check_tool_permission("run_command", {"command": "rm -rf /"})
    assert p3 == PermissionLevel.BLOCK

    # Auto approve all mode
    pm_auto = PermissionManager(auto_approve_all=True)
    p4, _ = pm_auto.check_tool_permission("write_file", {"path": "a.txt"})
    assert p4 == PermissionLevel.AUTO_ALLOW
