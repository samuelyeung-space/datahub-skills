#!/usr/bin/env python3
"""Install a pinned public Xiaobai skill in a supported local coding-agent workspace.

This installer never executes code from the archive, never uses credentials,
and refuses to overwrite an existing different skill.
"""

import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import stat
import sys
import tempfile
import urllib.request
import zipfile

SKILL_NAME = "ai-handout-skill"
COMMIT = "6306b08398c75b48891e993ef9969e5de5eb094f"
ARCHIVE_URL = (
    "https://raw.githubusercontent.com/samuelyeung-space/datahub-skills/"
    + COMMIT + "/international-stem-members/ai-handout-skill.zip"
)
ARCHIVE_SHA256 = "7d9f15cf4706ee546b7591b5703310d45f7dda9f5222a7150838cfca9d3391ca"
MEMBERS = {
    "SKILL.md",
    "README.md",
    "references/catalog.md",
    "references/book-quality.md",
    "scripts/read_bank.py",
    "tests/test_reader.py",
}
MAX_ARCHIVE_BYTES = 250_000
MAX_UNPACKED_BYTES = 1_000_000


class SafeRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        if newurl != ARCHIVE_URL:
            raise ValueError("Unexpected archive redirect; no installation performed")
        return super().redirect_request(request, fp, code, msg, headers, newurl)


def fetch_archive():
    opener = urllib.request.build_opener(SafeRedirect)
    with opener.open(urllib.request.Request(
        ARCHIVE_URL, headers={"User-Agent": "XiaobaiSkillInstaller/1.0"}), timeout=25
    ) as reply:
        archive = reply.read(MAX_ARCHIVE_BYTES + 1)
    if len(archive) > MAX_ARCHIVE_BYTES:
        raise ValueError("Archive exceeds size limit")
    if hashlib.sha256(archive).hexdigest() != ARCHIVE_SHA256:
        raise ValueError("Archive checksum mismatch; no installation performed")
    return archive


def validate_archive(archive):
    payload = {}
    with zipfile.ZipFile(io.BytesIO(archive)) as z:
        names = set()
        total = 0
        for info in z.infolist():
            name = info.filename
            if info.is_dir():
                continue
            prefix = SKILL_NAME + "/"
            if not name.startswith(prefix):
                raise ValueError("Unexpected directory in archive")
            relative = name[len(prefix):]
            if relative not in MEMBERS or relative in names:
                raise ValueError("Unexpected or duplicate file in archive")
            mode = info.external_attr >> 16
            if stat.S_IFMT(mode) == stat.S_IFLNK:
                raise ValueError("Archive contains a symlink")
            if info.file_size > MAX_UNPACKED_BYTES:
                raise ValueError("File exceeds size limit")
            total += info.file_size
            if total > MAX_UNPACKED_BYTES:
                raise ValueError("Expanded archive exceeds size limit")
            data = z.read(info)
            data.decode("utf-8")
            payload[relative] = data
            names.add(relative)
    if set(payload) != MEMBERS:
        raise ValueError("Skill archive is incomplete")
    if not payload["SKILL.md"].startswith(b"---\nname: ai-handout-skill\n"):
        raise ValueError("SKILL.md manifest does not match expected name")
    return payload


def target_path(client, scope, workspace):
    if scope == "project":
        root = Path(workspace).expanduser().resolve()
        if not root.is_dir():
            raise ValueError("Project workspace directory does not exist")
        parent = root / (".agents/skills" if client == "codex" else ".claude/skills")
    elif client == "codex":
        parent = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))).expanduser() / "skills"
    else:
        parent = Path.home() / ".claude" / "skills"
    return parent / SKILL_NAME


def install_payload(payload, target, dry_run=False):
    if target.is_symlink():
        raise ValueError("Refusing to modify a symlink")
    if target.exists():
        if not target.is_dir():
            raise FileExistsError("Target is not a skill directory")
        existing = {
            p.relative_to(target).as_posix(): p.read_bytes()
            for p in target.rglob("*") if p.is_file() and not p.is_symlink()
        }
        if existing == payload:
            return "already-installed"
        raise FileExistsError("A different skill already exists at target; not overwritten")
    if dry_run:
        return "verified-not-installed"
    if target.parent.is_symlink():
        raise ValueError("Refusing to write through a symlink")
    target.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=".xiaobai-", dir=target.parent))
    try:
        output = stage / SKILL_NAME
        for rel, content in payload.items():
            file_path = output / rel
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_bytes(content)
        if target.exists() or target.is_symlink():
            raise FileExistsError("Target changed while preparing; no files overwritten")
        output.rename(target)
    finally:
        shutil.rmtree(stage, ignore_errors=True)
    if not (target / "SKILL.md").is_file() or (target / "SKILL.md").read_bytes() != payload["SKILL.md"]:
        raise RuntimeError("Installation verification failed")
    return "installed-to-filesystem"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--client", choices=("codex", "claude-code"), required=True)
    parser.add_argument("--scope", choices=("project", "user"), default="project")
    parser.add_argument("--workspace", default=".")
    parser.add_argument("--dry-run", action="store_true", help="Verify download and archive without writing")
    args = parser.parse_args(argv)
    try:
        payload = validate_archive(fetch_archive())
        target = target_path(args.client, args.scope, args.workspace)
        status = install_payload(payload, target, dry_run=args.dry_run)
        result = {
            "status": status,
            "client": args.client,
            "scope": args.scope,
            "path": str(target),
            "skill_md_verified": status != "verified-not-installed",
            "account_skill_installed": False,
            "runtime_activation_verified": False,
            "note": "This installs filesystem-based project/user skills, not a consumer chat account skill. Confirm discovery in your coding-agent client.",
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, RuntimeError, zipfile.BadZipFile, UnicodeError) as error:
        print(json.dumps({"status":"ERROR", "reason":str(error)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
