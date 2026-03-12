class TestGitAlias:
    def test_init(self, temp_repo):
        git = temp_repo.get_repo_git()
        git.config("--global", "alias.globalalias", "status")
        git.config("--global", "alias.x", "status")
        git.config("--local", "alias.localalias", "status")
        git.config("--local", "alias.y", "status")

    def test_list_all(self, temp_repo):
        actual = temp_repo.invoke_extras_command("alias")
        actual = actual.stdout.decode()
        assert "globalalias = status" in actual
        assert "x = status" in actual
        assert "localalias = status" in actual
        assert "y = status" in actual

    def test_list_all_globally(self, temp_repo):
        actual = temp_repo.invoke_extras_command("alias", "--global")
        actual = actual.stdout.decode()
        assert "globalalias = status" in actual

    def test_list_all_locally(self, temp_repo):
        actual = temp_repo.invoke_extras_command("alias", "--local")
        actual = actual.stdout.decode()
        assert "localalias = status" in actual

    def test_search_globally(self, temp_repo):
        actual = temp_repo.invoke_extras_command("alias", "--global", "global")
        actual = actual.stdout.decode()
        assert "globalalias = status" in actual
        actual = temp_repo.invoke_extras_command("alias", "--global", "local")
        actual = actual.stdout.decode()
        assert "" == actual

    def test_search_locally(self, temp_repo):
        actual = temp_repo.invoke_extras_command("alias", "--local", "local")
        actual = actual.stdout.decode()
        assert "localalias = status" in actual
        actual = temp_repo.invoke_extras_command("alias", "--local", "global")
        actual = actual.stdout.decode()
        assert "" == actual

    def test_get_alias_globally_and_defaultly(self, temp_repo):
        actual = temp_repo.invoke_extras_command("alias", "globalalias")
        actual = actual.stdout.decode()
        assert "globalalias = status" in actual

    def test_set_alias_globally_and_defaultly(self, temp_repo):
        temp_repo.invoke_extras_command("alias", "globalalias", "diff")
        actual = temp_repo.invoke_extras_command("alias")
        actual = actual.stdout.decode()
        assert "globalalias = diff" in actual

    def test_get_alias_locally(self, temp_repo):
        actual = temp_repo.invoke_extras_command("alias", "--local", "localalias")
        actual = actual.stdout.decode()
        assert "localalias = status" in actual

    def test_set_alias_locally(self, temp_repo):
        temp_repo.invoke_extras_command("alias", "--local", "localalias", "diff")
        actual = temp_repo.invoke_extras_command("alias")
        actual = actual.stdout.decode()
        assert "localalias = diff" in actual

    def test_remove_one_alias_local(self, temp_repo):
        """--remove removes one alias; respects --local."""
        temp_repo.invoke_extras_command("alias", "--local", "toberemoved", "status")
        actual = temp_repo.invoke_extras_command("alias", "--local")
        actual = actual.stdout.decode()
        assert "toberemoved = status" in actual
        result = temp_repo.invoke_extras_command("alias", "--local", "--remove", "toberemoved")
        assert result.returncode == 0
        actual = temp_repo.invoke_extras_command("alias", "--local")
        actual = actual.stdout.decode()
        assert "toberemoved" not in actual

    def test_remove_one_alias_short_flag(self, temp_repo):
        """-r is shorthand for --remove."""
        temp_repo.invoke_extras_command("alias", "--local", "shortr", "log")
        result = temp_repo.invoke_extras_command("alias", "--local", "-r", "shortr")
        assert result.returncode == 0
        actual = temp_repo.invoke_extras_command("alias", "--local")
        actual = actual.stdout.decode()
        assert "shortr" not in actual

    def test_remove_nonexistent_alias_exits_with_error(self, temp_repo):
        """Removing a non-existent alias exits non-zero and prints to stderr."""
        result = temp_repo.invoke_extras_command("alias", "--local", "--remove", "nonexistent999")
        assert result.returncode != 0
        err = result.stderr.decode()
        assert "does not exist" in err
        assert "nonexistent999" in err

    def test_remove_requires_name(self, temp_repo):
        """--remove with no alias name exits with error."""
        result = temp_repo.invoke_extras_command("alias", "--remove")
        assert result.returncode != 0
        err = result.stderr.decode()
        assert "requires" in err or "error" in err.lower()

    def test_remove_all_local(self, temp_repo_clean):
        """--remove-all removes every alias in the current scope (--local)."""
        temp_repo_clean.switch_cwd_under_repo()
        temp_repo_clean.invoke_extras_command("alias", "--local", "a1", "status")
        temp_repo_clean.invoke_extras_command("alias", "--local", "a2", "log")
        actual = temp_repo_clean.invoke_extras_command("alias", "--local")
        actual = actual.stdout.decode()
        assert "a1" in actual and "a2" in actual
        result = temp_repo_clean.invoke_extras_command("alias", "--local", "--remove-all")
        assert result.returncode == 0
        actual = temp_repo_clean.invoke_extras_command("alias", "--local")
        actual = actual.stdout.decode()
        assert "a1" not in actual and "a2" not in actual

    def test_remove_all_clear_flag(self, temp_repo_clean):
        """--clear is synonym for --remove-all."""
        temp_repo_clean.switch_cwd_under_repo()
        temp_repo_clean.invoke_extras_command("alias", "--local", "c1", "status")
        result = temp_repo_clean.invoke_extras_command("alias", "--local", "--clear")
        assert result.returncode == 0
        actual = temp_repo_clean.invoke_extras_command("alias", "--local")
        actual = actual.stdout.decode()
        assert "c1" not in actual

    def test_teardown(self, temp_repo):
        git = temp_repo.get_repo_git()
        git.config("--global", "--unset", "alias.globalalias")
        git.config("--global", "--unset", "alias.x")
        git.config("--local", "--unset", "alias.localalias")
        git.config("--local", "--unset", "alias.y")
