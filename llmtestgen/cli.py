# CLI entry point for llmtestgen
# RICHELET Arthur, Cedric DERACHE - 2025

from __future__ import annotations

import os
import platform
import shutil
import subprocess  # nosec linter, used safely
from pathlib import Path
from typing import Dict, List, Tuple


ROOT_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = ROOT_DIR / ".env"
DEFAULT_ENV_PATH = ROOT_DIR / "default.env"


def _ensure_env_file_exists() -> None:
    """Ensure the .env file exists, seeding from the default template when available."""

    if ENV_PATH.exists():
        return

    if DEFAULT_ENV_PATH.exists():
        shutil.copy(DEFAULT_ENV_PATH, ENV_PATH)
    else:
        ENV_PATH.touch()


def _parse_template_entries() -> Tuple[List[str], List[Tuple[str, str]]]:
    """Return template lines and (key, default) pairs from default.env."""

    if not DEFAULT_ENV_PATH.exists():
        raise FileNotFoundError(
            "default.env template not found. Please ensure it exists before running setup."
        )

    template_lines = DEFAULT_ENV_PATH.read_text().splitlines()
    entries: List[Tuple[str, str]] = []

    for line in template_lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in line:
            continue

        key, remainder = line.split("=", 1)
        key = key.strip()
        if not key:
            continue

        value_part = remainder.split("#", 1)[0].strip()
        entries.append((key, value_part))

    if not entries:
        raise ValueError("No key/value pairs found in default.env template.")

    return template_lines, entries


def _render_env_file(template_lines: List[str], values: Dict[str, str]) -> str:
    """Generate .env content by overlaying values onto the template lines."""

    rendered: List[str] = []
    for line in template_lines:
        stripped = line.strip()
        if "=" in line and not stripped.startswith("#"):
            key = line.split("=", 1)[0].strip()
            if key in values:
                comment = ""
                if "#" in line:
                    comment = line.split("#", 1)[1].strip()
                    comment = f"  # {comment}" if comment else ""

                rendered.append(f"{key}={values[key]}{comment}".rstrip())
                continue
        rendered.append(line)

    return "\n".join(rendered).rstrip() + "\n"


def open_env_file() -> None:
    """Open the project .env file in a best-effort text editor."""

    _ensure_env_file_exists()
    env_path = ENV_PATH

    system = platform.system().lower()
    editor_commands: list[list[str]] = []

    # finding a suitable text editor based on the OS
    if system == "windows":
        editor_commands.extend([["notepad.exe"], ["notepad"], ["code"], ["code.cmd"]])
    elif system == "darwin":  # macOS
        editor_commands.extend([["open", "-e"], ["nano"], ["code"]])
    else:  # assume Linux/Unix
        editor_commands.extend([["xdg-open"], ["nano"], ["vi"], ["code"]])

    for command in editor_commands:
        executable = command[0]

        # notepad.exe may not be discoverable through PATH, so use startfile when available
        if system == "windows" and executable.startswith("notepad"):
            try:
                os.startfile(str(env_path))  # nosec
                return
            except OSError:
                continue

        if shutil.which(executable):
            try:
                # Popen is insecure if command includes user input; here it's safe
                subprocess.Popen(command + [str(env_path)])  # nosec linter
                return
            except OSError:
                continue

    print(f"No supported text editor detected. Edit the file manually: {env_path}")


def main():
    """Entry point for `llmtestgen`."""
    if not ENV_PATH.exists():
        print("No .env configuration detected. Opening the settings file...")
        open_env_file()
        return

    print("llmtestgen CLI is under development.")


def settings() -> None:
    """Entry point for `llmtestgen-settings`."""
    print("Opening llmtestgen .env configuration file...")
    open_env_file()


def _clear_screen() -> None:
    """Clear the terminal screen on all platforms."""
    os.system("cls" if os.name == "nt" else "clear") # nosec linter, used safely


def setup() -> None:
    """Interactively populate .env using default.env as the template."""

    # --- Check overwrite ---
    if ENV_PATH.exists():
        _clear_screen()
        print(f"A .env file already exists at {ENV_PATH}.\n")
        print("Press Enter to overwrite it, or press Ctrl+C to cancel.")
        try:
            input()
        except KeyboardInterrupt:
            print("\nSetup cancelled.")
            return

    # --- Load template ---
    try:
        template_lines, entries = _parse_template_entries()
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc))
        return

    # --- Parse consecutive comment blocks above each KEY ---
    comments: Dict[str, str] = {}
    comment_block: list[str] = []

    for line in template_lines:
        stripped = line.strip()

        # Accumulate consecutive comment lines
        if stripped.startswith("#") and "=" not in stripped:
            comment_block.append(stripped.lstrip("#").strip())
            continue

        # When we hit a KEY=VALUE line
        if "=" in stripped and not stripped.startswith("#"):
            key = stripped.split("=", 1)[0].strip()
            comments[key] = "\n".join(comment_block)
            comment_block = []   # reset
            continue

        # Any other line resets comment block
        comment_block = []

    # --- Interactive setup ---
    responses: Dict[str, str] = {}
    index = 0

    while index < len(entries):
        key, default = entries[index]

        _clear_screen()
        usage_raw = comments.get(key, "")

        print("LLMTestGen configuration\n")
        print("Enter the value for the following key (blank to keep [default]):")
        print("Type '<' then enter to go back to the previous key.\n")

        if usage_raw:
            print(usage_raw + "\n")
        else:
            print(f"Value for {key} (blank to keep [default]):\n")

        prompt = f"{key} [{default}]: " if default else f"{key}: "

        try:
            value = input(prompt)
        except KeyboardInterrupt:
            print("\nSetup cancelled.")
            return

        value = value.strip()

        # Go back
        if value == "<":
            if index > 0:
                index -= 1
                continue
            print("\nAlready at the first entry. Cannot go back.")
            input("\nPress Enter to continue...")
            continue

        # Store value and continue
        responses[key] = value if value else default
        index += 1

    # --- Save final file ---
    _clear_screen()
    ENV_PATH.write_text(_render_env_file(template_lines, responses))
    print(f"Configuration saved to {ENV_PATH}.")