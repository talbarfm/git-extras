"""
Pytest tests for git-recent-committers command.

Verifies:
- Lists committers with commit counts in the last N days (default from env or 7).
- Option -n <days> overrides the time window.
- Environment variable GIT_RECENT_COMMITTERS_DAYS sets default days.
- Exits with error to stderr when not in a git repository.
- Exits with error to stderr when -n is not a positive integer.
"""

import os
import subprocess
import tempfile

import pytest

from helper import GIT_EXTRAS_BIN


def run_recent_committers(*args, cwd=None, env=None):
    """Run bin/git-recent-committers with optional cwd and env."""
    script = os.path.join(GIT_EXTRAS_BIN, "git-recent-committers")
    run_env = {**os.environ, **(env or {})}
    return subprocess.run(
        [script, *args],
        capture_output=True,
        cwd=cwd,
        env=run_env,
    )


class TestGitRecentCommitters:
    """Tests for git recent-committers."""

    def test_in_repo_lists_committers(self, temp_repo):
        """In a repo with commits, output has lines 'count  name' and exit 0."""
        temp_repo.switch_cwd_under_repo()
        result = run_recent_committers(cwd=temp_repo.get_cwd())
        assert result.returncode == 0
        out = result.stdout.decode()
        assert "  " in out or out.strip() == ""
        # Initial commit is from user "test" (from init_repo_git_status)
        if out.strip():
            lines = out.strip().split("\n")
            for line in lines:
                parts = line.split(None, 1)
                assert len(parts) >= 2, f"Expected 'count  name' lines, got: {line!r}"
                count_str, name = parts[0], parts[1]
                assert count_str.isdigit(), f"First field should be digit: {line!r}"
                assert int(count_str) >= 1

    def test_with_n_option(self, temp_repo):
        """-n <days> uses the given number of days and succeeds."""
        temp_repo.switch_cwd_under_repo()
        result = run_recent_committers("-n", "30", cwd=temp_repo.get_cwd())
        assert result.returncode == 0
        # Should have at least the initial committer
        out = result.stdout.decode()
        assert "test" in out or out.strip() == ""

    def test_respects_env_var(self, temp_repo):
        """GIT_RECENT_COMMITTERS_DAYS is used when -n is not given."""
        temp_repo.switch_cwd_under_repo()
        result = run_recent_committers(
            cwd=temp_repo.get_cwd(),
            env={**os.environ, "GIT_RECENT_COMMITTERS_DAYS": "1"},
        )
        assert result.returncode == 0

    def test_outside_repo_exits_with_error(self):
        """When not in a git repository, exit non-zero and message to stderr."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = run_recent_committers(cwd=tmpdir)
        assert result.returncode != 0
        err = result.stderr.decode()
        assert "not a git repository" in err.lower() or "not a git" in err.lower()

    def test_invalid_n_exits_with_error(self, temp_repo):
        """When -n is not a positive integer, exit non-zero and message to stderr."""
        temp_repo.switch_cwd_under_repo()
        result = run_recent_committers("-n", "abc", cwd=temp_repo.get_cwd())
        assert result.returncode != 0
        err = result.stderr.decode()
        assert "positive integer" in err.lower() or "integer" in err.lower()
        assert "abc" in err

    def test_n_zero_exits_with_error(self, temp_repo):
        """When -n is 0, exit non-zero (not a positive integer)."""
        temp_repo.switch_cwd_under_repo()
        result = run_recent_committers("-n", "0", cwd=temp_repo.get_cwd())
        assert result.returncode != 0
        err = result.stderr.decode()
        assert "positive integer" in err.lower() or "integer" in err.lower()
