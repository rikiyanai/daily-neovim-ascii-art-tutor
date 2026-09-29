#!/usr/bin/env python3
"""Regression tests for the read-only new-user Neovim setup check."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parent.parent
CHECKER = ROOT / "bin" / "vim-daily-setup-check"


def run_check(files: dict[str, str]) -> str:
    with tempfile.TemporaryDirectory(prefix="vim-daily-setup-") as temp:
        config_home = Path(temp) / "config"
        nvim = config_home / "nvim"
        for relative, content in files.items():
            path = nvim / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        before = {
            path.relative_to(config_home): path.read_bytes()
            for path in config_home.rglob("*") if path.is_file()
        }
        env = dict(os.environ, XDG_CONFIG_HOME=str(config_home), HOME=str(Path(temp) / "home"))
        result = subprocess.run(
            [str(CHECKER)], env=env, text=True, capture_output=True, check=True
        )
        after = {
            path.relative_to(config_home): path.read_bytes()
            for path in config_home.rglob("*") if path.is_file()
        }
        assert before == after, "setup check modified the Neovim config"
        return result.stdout


def test_installer() -> None:
    with tempfile.TemporaryDirectory(prefix="vim-daily-install-") as temp:
        home = Path(temp) / "home"
        config_home = Path(temp) / "config"
        data_home = Path(temp) / "data"
        home.mkdir()
        env = dict(
            os.environ,
            HOME=str(home),
            XDG_CONFIG_HOME=str(config_home),
            XDG_DATA_HOME=str(data_home),
            VIM_DAILY_INSTALL_NO_LAUNCHD="1",
        )
        first = subprocess.run(
            [str(ROOT / "install.sh")], env=env, text=True,
            capture_output=True, check=True,
        )
        second = subprocess.run(
            [str(ROOT / "install.sh")], env=env, text=True,
            capture_output=True, check=True,
        )
        assert "[missing] Hardtime" in first.stdout
        assert "[missing] Hardtime" in second.stdout
        assert (home / ".local/bin/vim-daily-gate").resolve() == ROOT / "bin/vim-daily-gate"
        assert (home / ".local/bin/vim-daily-setup-check").resolve() == CHECKER
        assert (data_home / "vim-daily").resolve() == ROOT / "share"
        assert not (config_home / "nvim").exists(), "installer created a Neovim config"


def main() -> None:
    fresh = run_check({})
    for item in ("Hardtime", "WhichKey", "lualine", "configured color theme", "relative line numbers"):
        assert f"[missing] {item}" in fresh, fresh
    assert "vim-daily did not modify your Neovim config" in fresh
    assert "https://github.com/m4xshen/hardtime.nvim" in fresh

    partial = run_check({
        "lua/plugins/learning.lua": 'return {{ "m4xshen/hardtime.nvim" }}',
        "lua/config/options.lua": "vim.opt.relativenumber = true",
    })
    assert "[found]   Hardtime" in partial
    assert "[found]   relative line numbers" in partial
    assert "[missing] WhichKey" in partial

    lazyvim = run_check({
        "init.lua": 'require("config.lazy")',
        "lua/config/lazy.lua": 'spec = {{ "LazyVim/LazyVim", import = "lazyvim.plugins" }}',
        "lua/plugins/learning.lua": '''return {
          { "m4xshen/hardtime.nvim" },
          { "folke/which-key.nvim" },
          { "nvim-lualine/lualine.nvim" },
          { "folke/tokyonight.nvim", config = function() vim.cmd.colorscheme("tokyonight") end },
        }''',
    })
    assert "[found]   Hardtime" in lazyvim
    assert "[found]   WhichKey" in lazyvim
    assert "[found]   lualine" in lazyvim
    assert "[found]   configured color theme" in lazyvim
    assert "[verify]  relative line numbers (normally inherited from LazyVim)" in lazyvim
    assert "[missing]" not in lazyvim

    install_text = (ROOT / "install.sh").read_text(encoding="utf-8")
    assert '"$repo/bin/vim-daily-setup-check"' in install_text
    assert "~/.config/nvim" not in install_text
    test_installer()
    print("PASS setup check: fresh, partial, LazyVim, read-only, and idempotent installer fixtures")


if __name__ == "__main__":
    main()
