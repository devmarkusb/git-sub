from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


def test_help_exits_zero(gitsub, capsys, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["git-sub", "--help"])
    assert gitsub.main() == 0
    out = capsys.readouterr().out
    assert "git-sub" in out
    assert "submodule" in out.lower()


def test_inside_work_tree_true(gitsub):
    with patch.object(gitsub.subprocess, "run", return_value=MagicMock(returncode=0, stdout="true\n")) as run:
        assert gitsub.inside_work_tree(Path("/tmp/repo")) is True
    run.assert_called_once()


def test_inside_work_tree_false_wrong_stdout(gitsub):
    with patch.object(gitsub.subprocess, "run", return_value=MagicMock(returncode=0, stdout="false\n")):
        assert gitsub.inside_work_tree(Path("/tmp/repo")) is False


def test_inside_work_tree_false_bad_rc(gitsub):
    with patch.object(gitsub.subprocess, "run", return_value=MagicMock(returncode=1, stdout="true\n")):
        assert gitsub.inside_work_tree(Path("/tmp/repo")) is False


def test_repo_uses_lfs_true(gitsub):
    with patch.object(gitsub.subprocess, "run", return_value=MagicMock(returncode=0)) as run:
        assert gitsub.repo_uses_lfs(Path("/tmp/repo")) is True
    run.assert_called_once()
    args, kwargs = run.call_args
    assert args[0][:3] == ["git", "grep", "-q"]


def test_repo_uses_lfs_false(gitsub):
    with patch.object(gitsub.subprocess, "run", return_value=MagicMock(returncode=1)):
        assert gitsub.repo_uses_lfs(Path("/tmp/repo")) is False


def test_submodule_update_success_first_try(gitsub):
    cwd = Path("/tmp/repo")
    with patch.object(gitsub.subprocess, "run", return_value=MagicMock(returncode=0, stderr="", stdout="")) as run:
        gitsub.submodule_update(cwd)
    run.assert_called_once()
    assert "--recommend-shallow" in run.call_args[0][0]


def test_submodule_update_fallback_on_unknown_option(gitsub):
    cwd = Path("/tmp/repo")
    first = MagicMock(returncode=1, stderr="unknown option: recommend-shallow", stdout="")

    def run_side_effect(cmd, **kwargs):
        if "--recommend-shallow" in cmd:
            return first
        return MagicMock(returncode=0)

    with patch.object(gitsub.subprocess, "run", side_effect=run_side_effect):
        with patch.object(gitsub, "run_git_tty") as tty:
            gitsub.submodule_update(cwd)
    tty.assert_called_once_with(
        ["submodule", "update", "--init", "--recursive"],
        cwd=cwd,
        check=True,
    )


def test_submodule_update_fallback_on_recommend_shallow_message(gitsub):
    cwd = Path("/tmp/repo")
    first = MagicMock(returncode=1, stderr="recommend-shallow not supported", stdout="")

    def run_side_effect(cmd, **kwargs):
        if "--recommend-shallow" in cmd:
            return first
        return MagicMock(returncode=0)

    with patch.object(gitsub.subprocess, "run", side_effect=run_side_effect):
        with patch.object(gitsub, "run_git_tty") as tty:
            gitsub.submodule_update(cwd)
    tty.assert_called_once()


def test_submodule_update_other_error_exits(gitsub, capsys):
    cwd = Path("/tmp/repo")
    bad = MagicMock(returncode=7, stderr="fatal: not a git repo", stdout="")
    with patch.object(gitsub.subprocess, "run", return_value=bad):
        with pytest.raises(SystemExit) as exc:
            gitsub.submodule_update(cwd)
    assert exc.value.code == 7
    err = capsys.readouterr().err
    assert "fatal" in err or "git submodule failed" in err


def test_ensure_git_lfs_present(gitsub):
    with patch.object(gitsub.shutil, "which", return_value="/usr/bin/git-lfs"):
        gitsub.ensure_git_lfs(Path("/tmp/repo"))  # no exception


def test_ensure_git_lfs_missing_linux(gitsub, monkeypatch, capsys):
    monkeypatch.setattr(gitsub.sys, "platform", "linux")
    with patch.object(gitsub.shutil, "which", return_value=None):
        with pytest.raises(SystemExit) as exc:
            gitsub.ensure_git_lfs(Path("/tmp/repo"))
    assert exc.value.code == 1
    assert "git-lfs" in capsys.readouterr().err


def test_ensure_git_lfs_missing_windows(gitsub, monkeypatch, capsys):
    monkeypatch.setattr(gitsub.sys, "platform", "win32")
    with patch.object(gitsub.shutil, "which", return_value=None):
        with pytest.raises(SystemExit) as exc:
            gitsub.ensure_git_lfs(Path("/tmp/repo"))
    assert exc.value.code == 1
    err = capsys.readouterr().err
    assert "winget" in err or "git-lfs.com" in err


def test_ensure_git_lfs_missing_darwin(gitsub, monkeypatch, capsys):
    monkeypatch.setattr(gitsub.sys, "platform", "darwin")
    with patch.object(gitsub.shutil, "which", return_value=None):
        with pytest.raises(SystemExit) as exc:
            gitsub.ensure_git_lfs(Path("/tmp/repo"))
    assert exc.value.code == 1
    assert "brew" in capsys.readouterr().err


def test_lfs_setup_runs_install_and_pull(gitsub):
    cwd = Path("/tmp/repo")
    with patch.object(gitsub.shutil, "which", return_value="/x/git-lfs"):
        with patch.object(gitsub, "run_git_tty") as tty:
            gitsub.lfs_setup(cwd)
    assert len(tty.call_args_list) == 2
    assert tty.call_args_list[0].args[0] == ["lfs", "install", "--local"]
    assert tty.call_args_list[0].kwargs == {"cwd": cwd, "check": True}
    assert tty.call_args_list[1].args[0] == ["lfs", "pull"]
    assert tty.call_args_list[1].kwargs == {"cwd": cwd, "check": True}


def test_run_git_tty_check_failure(gitsub):
    with patch.object(gitsub.subprocess, "run", return_value=MagicMock(returncode=3)) as run:
        with pytest.raises(SystemExit) as exc:
            gitsub.run_git_tty(["status"], cwd=Path("/tmp"), check=True)
    assert exc.value.code == 3
    run.assert_called_once_with(["git", "status"], cwd=Path("/tmp"))


def test_run_git_tty_no_check(gitsub):
    with patch.object(gitsub.subprocess, "run", return_value=MagicMock(returncode=99)) as run:
        gitsub.run_git_tty(["x"], cwd=Path("/tmp"), check=False)
    run.assert_called_once()


def test_main_no_lfs_early_exit(gitsub, monkeypatch, tmp_path):
    monkeypatch.setattr(sys, "argv", ["git-sub"])
    cwd = tmp_path
    monkeypatch.chdir(cwd)
    with patch.object(gitsub, "submodule_update") as su:
        with patch.object(gitsub, "work_tree_root", return_value=cwd):
            with patch.object(gitsub, "repo_uses_lfs", return_value=False):
                assert gitsub.main() == 0
    su.assert_called_once_with(cwd)


def test_main_lfs_path(gitsub, monkeypatch, tmp_path):
    monkeypatch.setattr(sys, "argv", ["git-sub"])
    cwd = tmp_path
    monkeypatch.chdir(cwd)
    with patch.object(gitsub, "submodule_update"):
        with patch.object(gitsub, "work_tree_root", return_value=cwd):
            with patch.object(gitsub, "repo_uses_lfs", return_value=True):
                with patch.object(gitsub, "lfs_setup") as lfs:
                    assert gitsub.main() == 0
    lfs.assert_called_once_with(cwd)


def test_main_not_in_work_tree_fails_before_modifying_checkout(gitsub, monkeypatch, tmp_path):
    monkeypatch.setattr(sys, "argv", ["git-sub"])
    monkeypatch.chdir(tmp_path)
    bad = MagicMock(returncode=128, stdout=b"", stderr=b"fatal: not a git repository")
    with patch.object(gitsub.subprocess, "run", return_value=bad) as run:
        with pytest.raises(SystemExit) as exc:
            gitsub.main()
    assert exc.value.code == 128
    run.assert_called_once_with(
        ["git", "rev-parse", "--show-toplevel"], cwd=tmp_path, capture_output=True,
    )


def test_repo_uses_lfs_only_searches_attribute_declarations(gitsub):
    cwd = Path("/tmp/repo")
    with patch.object(gitsub.subprocess, "run", return_value=MagicMock(returncode=1)) as run:
        assert not gitsub.repo_uses_lfs(cwd)
    cmd = run.call_args.args[0]
    assert "--" in cmd
    assert cmd[cmd.index("--") + 1:] == [":(top).gitattributes", ":(top)**/.gitattributes"]
    assert "-E" in cmd
    assert "filter=lfs" not in cmd  # Match an attribute token, not an arbitrary substring.


def test_repo_uses_lfs_reports_git_errors(gitsub, capsys):
    bad = MagicMock(returncode=128, stderr="fatal: unable to read index", stdout="")
    with patch.object(gitsub.subprocess, "run", return_value=bad):
        with pytest.raises(SystemExit) as exc:
            gitsub.repo_uses_lfs(Path("/tmp/repo"))
    assert exc.value.code == 128
    assert "unable to read index" in capsys.readouterr().err


def test_submodule_sync_precedes_update(gitsub, tmp_path):
    (tmp_path / ".gitmodules").write_text("[submodule]\n")
    with patch.object(gitsub.subprocess, "run", return_value=MagicMock(returncode=0)) as run:
        gitsub.submodule_update(tmp_path)
    assert [call.args[0][1:3] for call in run.call_args_list] == [
        ["submodule", "sync"], ["submodule", "update"], ["submodule", "sync"]
    ]


def test_submodule_sync_failure_prevents_update(gitsub, tmp_path):
    (tmp_path / ".gitmodules").write_text("[submodule]\n")
    with patch.object(gitsub.subprocess, "run", return_value=MagicMock(returncode=7)) as run:
        with pytest.raises(SystemExit) as exc:
            gitsub.submodule_update(tmp_path)
    assert exc.value.code == 7
    run.assert_called_once_with(["git", "submodule", "sync", "--recursive"], cwd=tmp_path)


def test_submodule_does_not_retry_operational_error_containing_option(gitsub):
    bad = MagicMock(returncode=128, stderr="fatal: repository '/tmp/recommend-shallow' not found", stdout="")
    with patch.object(gitsub.subprocess, "run", return_value=bad) as run:
        with pytest.raises(SystemExit) as exc:
            gitsub.submodule_update(Path("/tmp/repo"))
    assert exc.value.code == 128
    run.assert_called_once()


def test_main_rejects_unknown_arguments_before_running_git(gitsub, monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["git-sub", "--hlep"])
    result = MagicMock(returncode=0, stdout="false\n", stderr="")
    with patch.object(gitsub.subprocess, "run", return_value=result) as run:
        assert gitsub.main() == 2
    run.assert_not_called()
    assert "--hlep" in capsys.readouterr().err


def test_main_from_subdirectory_uses_repository_root(gitsub, tmp_path, monkeypatch):
    root = tmp_path
    nested = root / "src"
    nested.mkdir()
    (root / ".gitmodules").write_text("[submodule]\n")
    monkeypatch.chdir(nested)
    monkeypatch.setattr(sys, "argv", ["git-sub"])

    def git_result(cmd, **kwargs):
        if cmd[1:] == ["rev-parse", "--show-toplevel"]:
            return MagicMock(returncode=0, stdout=os.fsencode(root) + b"\n", stderr=b"")
        if cmd[1:] == ["rev-parse", "--is-inside-work-tree"]:
            return MagicMock(returncode=0, stdout="true\n", stderr="")
        if cmd[1] == "grep":
            return MagicMock(returncode=1, stdout="", stderr="")
        return MagicMock(returncode=0, stdout="", stderr="")

    with patch.object(gitsub.subprocess, "run", side_effect=git_result) as run:
        assert gitsub.main() == 0
    syncs = [call for call in run.call_args_list if call.args[0][1:3] == ["submodule", "sync"]]
    assert len(syncs) == 2
    assert syncs[0].kwargs["cwd"] == root
    for call in run.call_args_list:
        if call.args[0][1] in ("submodule", "grep"):
            assert call.kwargs["cwd"] == root


@pytest.mark.parametrize("root", ["/tmp/repo", "/tmp/repo\n", "/tmp/repo\rname"])
def test_work_tree_root_preserves_directory_name(gitsub, root):
    with patch.object(gitsub.subprocess, "run", return_value=MagicMock(returncode=0, stdout=os.fsencode(root) + b"\n")):
        assert gitsub.work_tree_root(Path("/tmp")) == Path(root)


def test_submodule_update_falls_back_on_old_git_usage(gitsub):
    bad = MagicMock(returncode=1, stdout="", stderr="usage: git submodule [--quiet] update [--init]\n")
    with patch.object(gitsub.subprocess, "run", return_value=bad):
        with patch.object(gitsub, "run_git_tty") as tty:
            gitsub.submodule_update(Path("/tmp/repo"))
    tty.assert_called_once_with(
        ["submodule", "update", "--init", "--recursive"], cwd=Path("/tmp/repo"), check=True,
    )


def test_lfs_install_failure_prevents_pull(gitsub):
    with patch.object(gitsub, "ensure_git_lfs"):
        with patch.object(gitsub.subprocess, "run", return_value=MagicMock(returncode=4)) as run:
            with pytest.raises(SystemExit) as exc:
                gitsub.lfs_setup(Path("/tmp/repo"))
    assert exc.value.code == 4
    run.assert_called_once_with(["git", "lfs", "install", "--local"], cwd=Path("/tmp/repo"))


def test_submodule_update_resyncs_urls_after_successful_checkout(gitsub, tmp_path):
    (tmp_path / ".gitmodules").write_text("[submodule]\n")
    with patch.object(gitsub.subprocess, "run", return_value=MagicMock(returncode=0)) as run:
        gitsub.submodule_update(tmp_path)
    assert [call.args[0][2] for call in run.call_args_list] == ["sync", "update", "sync"]


def test_submodule_update_propagates_post_checkout_sync_failure(gitsub, tmp_path):
    (tmp_path / ".gitmodules").write_text("[submodule]\n")
    results = [MagicMock(returncode=0), MagicMock(returncode=0), MagicMock(returncode=9)]
    with patch.object(gitsub.subprocess, "run", side_effect=results) as run:
        with pytest.raises(SystemExit) as exc:
            gitsub.submodule_update(tmp_path)
    assert exc.value.code == 9
    assert [call.args[0][2] for call in run.call_args_list] == ["sync", "update", "sync"]


def test_submodule_update_preserves_failure_without_repeating_update(gitsub, tmp_path):
    (tmp_path / ".gitmodules").write_text("[submodule]\n")
    results = [MagicMock(returncode=0), MagicMock(returncode=7, stdout="", stderr="fatal: update failed")]
    with patch.object(gitsub.subprocess, "run", side_effect=results) as run:
        with pytest.raises(SystemExit) as exc:
            gitsub.submodule_update(tmp_path)
    assert exc.value.code == 7
    assert [call.args[0][2] for call in run.call_args_list] == ["sync", "update"]
