import pytest
from pathlib import Path
from myagent.tools import execute_tool, safe_path
from myagent.tools.files import list_dir, read_file, write_file, edit_file, search, run_command

def test_safe_path(tmp_path):
    valid = safe_path("sub/file.txt", workdir=tmp_path)
    assert valid == tmp_path / "sub" / "file.txt"

    with pytest.raises(ValueError):
        safe_path("../outside.txt", workdir=tmp_path)

def test_write_read_edit_file(tmp_path):
    f_path = "test.txt"
    # Write
    res_write = write_file(f_path, "Hello World\nLine 2", workdir=tmp_path)
    assert "Successfully wrote" in res_write

    # Read
    res_read = read_file(f_path, workdir=tmp_path)
    assert "Hello World" in res_read

    # Edit
    res_edit = edit_file(f_path, old="Hello World", new="Hello Python", workdir=tmp_path)
    assert "Successfully edited" in res_edit

    # Read updated
    res_read_2 = read_file(f_path, workdir=tmp_path)
    assert "Hello Python" in res_read_2

def test_list_and_search(tmp_path):
    write_file("a.py", "def foo(): pass", workdir=tmp_path)
    write_file("b.py", "def bar(): pass", workdir=tmp_path)

    # List
    res_list = list_dir(".", workdir=tmp_path)
    assert "a.py" in res_list
    assert "b.py" in res_list

    # Search
    res_search = search(r"def foo", path=".", workdir=tmp_path)
    assert "a.py" in res_search
    assert "def foo" in res_search

def test_run_command(tmp_path):
    res = run_command("echo 'Agent Test'", workdir=tmp_path)
    assert "exit code: 0" in res
    assert "Agent Test" in res
