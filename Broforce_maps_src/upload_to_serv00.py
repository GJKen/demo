#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Manage local SSH profiles and sync Broforce files to a remote host over SFTP."""

from __future__ import annotations

import argparse
import getpass
import hashlib
import json
import os
import posixpath
import shlex
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import BinaryIO

try:
    import paramiko
except ImportError:
    print("缺少 paramiko，请先运行：python -m pip install paramiko", file=sys.stderr)
    raise SystemExit(1)


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
DEFAULT_CONFIG = SCRIPT_DIR / "upload_hosts.local.json"
DEFAULT_HOST = "s13.serv00.com"
DEFAULT_PORT = 22
DEFAULT_REMOTE_ROOT = "~/broforce_maps"
CONFIG_VERSION = 1
CHUNK_SIZE = 1024 * 1024
REMOTE_SERVER_RELATIVE = "Broforce_maps_src/server.py"
HEALTH_URL = "http://127.0.0.1:13333/api/health"

SCOPE_LABELS = {
    "frontend": "前端页面",
    "backend": "后端程序",
    "data": "地图数据",
    "all": "前端 + 后端 + 地图数据",
}
DATA_MODE_LABELS = {
    "merge": "合并（远程独有保留，本地同 ID 优先）",
    "overwrite": "覆盖（本地完整替换远程）",
}


@dataclass(frozen=True)
class SyncFile:
    local_path: Path
    remote_relative: str
    category: str


@dataclass
class FileState:
    item: SyncFile
    local_size: int
    local_hash: str
    remote_path: str
    remote_size: int | None
    remote_hash: str | None

    @property
    def changed(self) -> bool:
        return self.local_hash != self.remote_hash


def ask(prompt: str, default: str | None = None) -> str:
    suffix = f" [{default}]" if default else ""
    value = input(f"{prompt}{suffix}: ").strip()
    return value or (default or "")


def ask_yes_no(prompt: str, default: bool = False) -> bool:
    hint = "Y/n" if default else "y/N"
    value = input(f"{prompt} [{hint}]: ").strip().lower()
    if not value:
        return default
    return value in {"y", "yes", "是"}


def load_config(path: Path) -> dict:
    if not path.exists():
        return {"version": CONFIG_VERSION, "default_profile": "", "profiles": {}}
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"无法读取配置文件：{exc}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"配置文件不是有效 JSON：{exc}") from exc
    if not isinstance(config, dict) or not isinstance(config.get("profiles"), dict):
        raise ValueError("配置文件格式错误：profiles 必须是对象")
    config.setdefault("version", CONFIG_VERSION)
    config.setdefault("default_profile", "")
    return config


def save_config(path: Path, config: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(config, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)
    try:
        path.chmod(0o600)
    except OSError:
        pass


def validate_profile(name: str, profile: object) -> dict:
    if not isinstance(profile, dict):
        raise ValueError(f"主机配置 {name!r} 格式错误")
    host = str(profile.get("host", "")).strip()
    username = str(profile.get("username", "")).strip()
    password = str(profile.get("password", ""))
    backend_token = str(profile.get("backend_token", ""))
    remote_root = str(profile.get("remote_root", DEFAULT_REMOTE_ROOT)).strip()
    try:
        port = int(profile.get("port", DEFAULT_PORT))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"主机配置 {name!r} 的端口无效") from exc
    if not host or not username:
        raise ValueError(f"主机配置 {name!r} 缺少 host 或 username")
    if not 1 <= port <= 65535:
        raise ValueError(f"主机配置 {name!r} 的端口不在 1-65535 范围内")
    if not remote_root or remote_root in {"/", "~"}:
        raise ValueError(f"主机配置 {name!r} 的 remote_root 不能是根目录或主目录")
    if "\x00" in remote_root or ".." in remote_root.replace("\\", "/").split("/"):
        raise ValueError(f"主机配置 {name!r} 的 remote_root 不能包含 .. 或空字符")
    return {
        "host": host,
        "port": port,
        "username": username,
        "password": password,
        "backend_token": backend_token,
        "remote_root": remote_root,
    }


def configure_profile(config_path: Path, config: dict, requested_name: str = "") -> str:
    profiles = config["profiles"]
    name = ask("配置名称", requested_name or config.get("default_profile") or "serv00-main")
    if not name:
        raise ValueError("配置名称不能为空")
    current = profiles.get(name, {}) if isinstance(profiles.get(name), dict) else {}
    host = ask("SSH 主机", str(current.get("host") or DEFAULT_HOST))
    port_text = ask("SSH 端口", str(current.get("port") or DEFAULT_PORT))
    username = ask("SSH 用户名", str(current.get("username") or ""))
    current_password = str(current.get("password") or "")
    password_prompt = "SSH 密码（输入时不会显示"
    password_prompt += "，直接回车保留已保存密码" if current_password else ""
    password = getpass.getpass(password_prompt + "）：") or current_password
    if not password:
        raise ValueError("SSH 密码不能为空")
    backend_token = str(current.get("backend_token") or "")
    remote_root = ask("远程项目根目录", str(current.get("remote_root") or DEFAULT_REMOTE_ROOT))
    profile = validate_profile(
        name,
        {
            "host": host,
            "port": port_text,
            "username": username,
            "password": password,
            "backend_token": backend_token,
            "remote_root": remote_root,
        },
    )
    profiles[name] = profile
    config["default_profile"] = name
    save_config(config_path, config)
    print(f"配置已保存：{config_path}")
    print("账号密码已保存到本地配置；主机列表和日志不会显示密码。")
    return name


def select_profile(config_path: Path, config: dict, requested_name: str = "") -> tuple[str, dict]:
    profiles = config["profiles"]
    if requested_name:
        if requested_name not in profiles:
            raise ValueError(f"没有名为 {requested_name!r} 的主机配置")
        return requested_name, validate_profile(requested_name, profiles[requested_name])

    if not profiles:
        print("尚未保存主机配置，请先创建。")
        name = configure_profile(config_path, config)
        return name, validate_profile(name, config["profiles"][name])

    while True:
        names = list(profiles)
        default_name = str(config.get("default_profile") or "")
        print("\n可用主机：")
        for index, name in enumerate(names, start=1):
            profile = validate_profile(name, profiles[name])
            default_mark = " *" if name == default_name else ""
            print(
                f"  {index}. {name}{default_mark}  "
                f"{profile['username']}@{profile['host']}:{profile['port']}  "
                f"{profile['remote_root']}  "
                f"[SSH密码{'已保存' if profile['password'] else '未保存'}] "
                f"[重启Token{'已保存' if profile.get('backend_token') else '未保存'}]"
            )
        print("  N. 新增主机")
        print("  E. 编辑主机")
        default_index = names.index(default_name) + 1 if default_name in names else 1
        choice = ask("选择主机", str(default_index)).lower()
        if choice == "n":
            suggested_name = "new-host"
            suffix = 2
            while suggested_name in profiles:
                suggested_name = f"new-host-{suffix}"
                suffix += 1
            configure_profile(config_path, config, suggested_name)
            profiles = config["profiles"]
            continue
        if choice == "e":
            edit_name = ask("要编辑的配置名称", default_name or names[0])
            if edit_name not in profiles:
                print(f"没有名为 {edit_name!r} 的配置。")
                continue
            configure_profile(config_path, config, edit_name)
            profiles = config["profiles"]
            continue
        try:
            selected_index = int(choice)
        except (ValueError, IndexError):
            print("选择无效，请重新输入。")
            continue
        if not 1 <= selected_index <= len(names):
            print("选择无效，请重新输入。")
            continue
        selected_name = names[selected_index - 1]
        config["default_profile"] = selected_name
        save_config(config_path, config)
        return selected_name, validate_profile(selected_name, profiles[selected_name])


def select_action() -> str:
    print("\n操作：")
    print("  1. 同步文件")
    print("  2. 手动重启后端")
    while True:
        choice = ask("选择操作", "1")
        if choice == "1":
            return "sync"
        if choice == "2":
            return "restart"
        print("选择无效，请重新输入。")


def select_scope(requested_scope: str = "") -> str:
    if requested_scope:
        return requested_scope
    options = ["frontend", "backend", "data", "all"]
    print("\n同步范围：")
    for index, scope in enumerate(options, start=1):
        extra = "（maps.json + previews）" if scope == "data" else ""
        print(f"  {index}. {SCOPE_LABELS[scope]}{extra}")
    while True:
        choice = ask("选择同步范围", "1")
        try:
            selected_index = int(choice)
        except (ValueError, IndexError):
            print("选择无效，请重新输入。")
            continue
        if not 1 <= selected_index <= len(options):
            print("选择无效，请重新输入。")
            continue
        return options[selected_index - 1]


def select_data_mode(requested_mode: str = "") -> str:
    if requested_mode:
        return requested_mode
    options = ["merge", "overwrite"]
    print("\n地图数据同步方式：")
    print("  1. 合并（远程独有记录保留，本地同 ID 记录优先）")
    print("  2. 覆盖（使用本地 maps.json 完整替换远程）")
    while True:
        choice = ask("选择同步方式", "1")
        try:
            selected_index = int(choice)
        except ValueError:
            print("选择无效，请重新输入。")
            continue
        if 1 <= selected_index <= len(options):
            return options[selected_index - 1]
        print("选择无效，请重新输入。")


def load_map_records(raw: bytes, source: str) -> list[dict]:
    try:
        records = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"{source} 不是有效的 UTF-8 JSON：{exc}") from exc
    if not isinstance(records, list):
        raise ValueError(f"{source} 的根节点必须是数组")
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            raise ValueError(f"{source} 第 {index + 1} 项不是对象")
        if not str(record.get("map_id", "")).strip():
            raise ValueError(f"{source} 第 {index + 1} 项缺少 map_id")
    return records


def merge_map_records(local_raw: bytes, remote_raw: bytes) -> bytes:
    """Merge records by map_id; local records replace remote duplicates."""
    local_records = load_map_records(local_raw, "本地 maps.json")
    remote_records = load_map_records(remote_raw, "远程 maps.json")
    local_by_id = {str(record["map_id"]): record for record in local_records}
    merged: list[dict] = []
    added_ids: set[str] = set()

    for remote_record in remote_records:
        map_id = str(remote_record["map_id"])
        merged.append(local_by_id.get(map_id, remote_record))
        added_ids.add(map_id)
    for local_record in local_records:
        map_id = str(local_record["map_id"])
        if map_id not in added_ids:
            merged.append(local_record)
            added_ids.add(map_id)
    return (json.dumps(merged, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def expand_remote_path(path: str, remote_home: str) -> str:
    path = path.strip().replace("\\", "/")
    if path == "~":
        return remote_home
    if path.startswith("~/"):
        return posixpath.join(remote_home, path[2:])
    return posixpath.normpath(path)


def collect_sync_files(scope: str) -> list[SyncFile]:
    items: list[SyncFile] = []
    if scope in {"frontend", "all"}:
        items.append(
            SyncFile(
                REPO_ROOT / "static" / "Broforce地图记录.html",
                "static/Broforce地图记录.html",
                "frontend",
            )
        )
    if scope in {"backend", "all"}:
        items.append(
            SyncFile(
                SCRIPT_DIR / "server.py",
                REMOTE_SERVER_RELATIVE,
                "backend",
            )
        )
    if scope in {"data", "all"}:
        items.append(
            SyncFile(
                SCRIPT_DIR / "maps.json",
                "Broforce_maps_src/maps.json",
                "data",
            )
        )
        preview_dir = SCRIPT_DIR / "previews"
        if preview_dir.is_dir():
            for path in sorted(preview_dir.rglob("*")):
                if path.is_file():
                    relative = path.relative_to(preview_dir).as_posix()
                    items.append(
                        SyncFile(
                            path,
                            f"Broforce_maps_src/previews/{relative}",
                            "data",
                        )
                    )
    missing = [str(item.local_path) for item in items if not item.local_path.is_file()]
    if missing:
        raise ValueError("以下本地文件不存在：\n" + "\n".join(f"  - {path}" for path in missing))
    return items


def collect_single_file(local: Path, remote: str) -> list[SyncFile]:
    local_path = local if local.is_absolute() else Path.cwd() / local
    local_path = local_path.resolve()
    if not local_path.is_file():
        raise ValueError(f"本地文件不存在：{local_path}")
    remote_path = remote.strip().replace("\\", "/")
    if not remote_path:
        raise ValueError("使用 --local 时必须同时提供 --remote")
    if "\x00" in remote_path or ".." in remote_path.split("/"):
        raise ValueError("远程文件路径不能包含 .. 或空字符")
    if remote_path.endswith("/") or posixpath.basename(remote_path) in {"", ".", "~"}:
        raise ValueError("远程文件路径必须包含文件名")
    return [SyncFile(local_path, remote_path, "custom")]


def sha256_stream(stream: BinaryIO) -> tuple[int, str]:
    digest = hashlib.sha256()
    size = 0
    while True:
        chunk = stream.read(CHUNK_SIZE)
        if not chunk:
            break
        size += len(chunk)
        digest.update(chunk)
    return size, digest.hexdigest().upper()


def local_file_state(path: Path) -> tuple[int, str]:
    with path.open("rb") as stream:
        return sha256_stream(stream)


def remote_file_state(sftp: paramiko.SFTPClient, path: str) -> tuple[int | None, str | None]:
    try:
        with sftp.open(path, "rb") as stream:
            return sha256_stream(stream)
    except IOError as exc:
        if getattr(exc, "errno", None) == 2:
            return None, None
        raise


def remote_file_bytes(sftp: paramiko.SFTPClient, path: str) -> bytes | None:
    try:
        with sftp.open(path, "rb") as stream:
            return stream.read()
    except IOError as exc:
        if getattr(exc, "errno", None) == 2:
            return None
        raise


def ensure_remote_directory(sftp: paramiko.SFTPClient, path: str) -> None:
    normalized = posixpath.normpath(path)
    parts = normalized.split("/")
    current = "/" if normalized.startswith("/") else ""
    for part in parts:
        if not part:
            continue
        current = posixpath.join(current, part) if current else part
        try:
            sftp.stat(current)
        except IOError as exc:
            if getattr(exc, "errno", None) != 2:
                raise
            sftp.mkdir(current)


def copy_remote_file(sftp: paramiko.SFTPClient, source: str, destination: str) -> None:
    ensure_remote_directory(sftp, posixpath.dirname(destination))
    with sftp.open(source, "rb") as source_stream, sftp.open(destination, "wb") as destination_stream:
        while True:
            chunk = source_stream.read(CHUNK_SIZE)
            if not chunk:
                break
            destination_stream.write(chunk)


def inspect_files(
    sftp: paramiko.SFTPClient,
    items: list[SyncFile],
    remote_root: str,
) -> list[FileState]:
    states: list[FileState] = []
    for item in items:
        local_size, local_hash = local_file_state(item.local_path)
        if item.category == "custom" and item.remote_relative.startswith(("/", "~/")):
            remote_path = expand_remote_path(item.remote_relative, sftp.normalize("."))
        else:
            remote_path = posixpath.join(remote_root, item.remote_relative)
        remote_size, remote_hash = remote_file_state(sftp, remote_path)
        states.append(
            FileState(
                item=item,
                local_size=local_size,
                local_hash=local_hash,
                remote_path=remote_path,
                remote_size=remote_size,
                remote_hash=remote_hash,
            )
        )
    return states


def print_sync_plan(
    profile_name: str,
    profile: dict,
    scope: str,
    items: list[SyncFile],
    data_mode: str = "",
) -> None:
    print(f"主机配置：{profile_name}")
    print(f"远程主机：{profile['username']}@{profile['host']}:{profile['port']}")
    print(f"远程根目录：{profile['remote_root']}")
    print(f"同步范围：{SCOPE_LABELS.get(scope, '自定义文件')}")
    if scope in {"data", "all"} and data_mode:
        print(f"数据方式：{DATA_MODE_LABELS[data_mode]}")
    print("本地同步项：")
    for item in items:
        print(f"  - {item.local_path} -> {item.remote_relative}")


def atomic_upload(
    sftp: paramiko.SFTPClient,
    state: FileState,
    backup_root: str,
) -> None:
    remote_dir = posixpath.dirname(state.remote_path)
    ensure_remote_directory(sftp, remote_dir)
    temporary = f"{state.remote_path}.uploading"
    try:
        sftp.remove(temporary)
    except IOError:
        pass
    sftp.put(str(state.item.local_path), temporary)
    uploaded_size, uploaded_hash = remote_file_state(sftp, temporary)
    if uploaded_size != state.local_size or uploaded_hash != state.local_hash:
        try:
            sftp.remove(temporary)
        except IOError:
            pass
        raise IOError(f"临时文件校验失败：{state.remote_path}")

    if state.remote_hash is not None:
        if state.item.category == "custom":
            remote_key = hashlib.sha256(state.remote_path.encode("utf-8")).hexdigest()[:12]
            backup_relative = posixpath.join(
                "custom",
                remote_key,
                posixpath.basename(state.remote_path),
            )
        else:
            backup_relative = state.item.remote_relative.lstrip("/")
        backup_path = posixpath.join(backup_root, backup_relative)
        copy_remote_file(sftp, state.remote_path, backup_path)
        backup_size, backup_hash = remote_file_state(sftp, backup_path)
        if backup_size != state.remote_size or backup_hash != state.remote_hash:
            try:
                sftp.remove(temporary)
            except IOError:
                pass
            raise IOError(f"远程备份校验失败：{backup_path}")

    try:
        sftp.posix_rename(temporary, state.remote_path)
    except (AttributeError, IOError):
        try:
            sftp.remove(state.remote_path)
        except IOError:
            pass
        sftp.rename(temporary, state.remote_path)

    final_size, final_hash = remote_file_state(sftp, state.remote_path)
    if final_size != state.local_size or final_hash != state.local_hash:
        raise IOError(f"上传后校验失败：{state.remote_path}")


def connect(profile: dict, password: str) -> paramiko.SSHClient:
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.WarningPolicy())
    try:
        client.connect(
            hostname=profile["host"],
            port=profile["port"],
            username=profile["username"],
            password=password,
            look_for_keys=False,
            allow_agent=False,
            timeout=20,
            banner_timeout=20,
            auth_timeout=20,
        )
    except Exception:
        client.close()
        raise
    return client


def restart_remote_service(
    client: paramiko.SSHClient,
    remote_root: str,
    backend_token: str,
) -> str:
    """Restart server.py with the API token supplied over stdin, then verify health."""
    quoted_root = shlex.quote(remote_root)
    stop_command = (
        "set -eu\n"
        f"cd {quoted_root}\n"
        "pkill -f '[s]erver.py' >/dev/null 2>&1 || true\n"
        "sleep 1"
    )
    stop_stdin, stop_stdout, stop_stderr = client.exec_command(stop_command, timeout=20)
    stop_stdin.close()
    stop_stdout.read()
    stop_error = stop_stderr.read().decode("utf-8", errors="replace").strip()
    stop_exit_code = stop_stdout.channel.recv_exit_status()
    if stop_exit_code != 0:
        detail = stop_error or f"远程停止命令退出码 {stop_exit_code}"
        raise RuntimeError(f"远程后端停止失败：{detail}")

    start_command = (
        "set -eu\n"
        "IFS= read -r BROFORCE_API_TOKEN\n"
        "export BROFORCE_API_TOKEN\n"
        f"cd {quoted_root}\n"
        "nohup python3 Broforce_maps_src/server.py > server.log 2>&1 < /dev/null &\n"
        "for attempt in 1 2 3 4 5 6 7 8 9 10; do\n"
        f"  if curl -fsS --max-time 2 {shlex.quote(HEALTH_URL)}; then\n"
        "    exit 0\n"
        "  fi\n"
        "  sleep 1\n"
        "done\n"
        "exit 1"
    )
    stdin, stdout, stderr = client.exec_command(start_command, timeout=40)
    stdin.write(backend_token + "\n")
    stdin.flush()
    result = stdout.read().decode("utf-8", errors="replace").strip()
    error = stderr.read().decode("utf-8", errors="replace").strip()
    exit_code = stdout.channel.recv_exit_status()
    try:
        health = json.loads(result)
    except json.JSONDecodeError:
        health = {}
    if exit_code != 0 or not health.get("ok"):
        detail = error or result or f"远程命令退出码 {exit_code}"
        raise RuntimeError(f"远程后端重启失败：{detail}")
    return json.dumps(health, ensure_ascii=False)


def needs_service_restart(state: FileState, remote_root: str) -> bool:
    """Return whether the changed file contains the running backend program."""
    if state.item.category == "backend":
        return True
    service_path = posixpath.join(remote_root, REMOTE_SERVER_RELATIVE)
    return posixpath.normpath(state.remote_path) == posixpath.normpath(service_path)


def manual_restart(
    profile_name: str,
    profile: dict,
    config_path: Path | None = None,
    config: dict | None = None,
) -> int:
    """Restart the selected remote backend without uploading any files."""
    print(f"主机配置：{profile_name}")
    print(f"远程主机：{profile['username']}@{profile['host']}:{profile['port']}")
    print(f"远程根目录：{profile['remote_root']}")

    password = str(profile.get("password") or "")
    had_saved_password = bool(password)
    if not password:
        password_prompt = "SSH 密码（输入时不会显示"
        if config_path is not None and config is not None:
            password_prompt += "，认证成功后保存到本地配置"
        password = getpass.getpass(password_prompt + "）：")
    if not password:
        print("SSH 密码不能为空", file=sys.stderr)
        return 2

    try:
        client = connect(profile, password)
    except paramiko.AuthenticationException:
        if had_saved_password:
            print("已保存的 SSH 密码无效或远程密码已变更。")
        else:
            print("SSH 密码认证失败。")
        password = getpass.getpass("请重新输入 SSH 密码（认证成功后更新本地配置）：")
        if not password:
            print("SSH 密码不能为空", file=sys.stderr)
            return 2
        client = connect(profile, password)

    password_changed = password != str(profile.get("password") or "")
    if password_changed and config_path is not None and config is not None and profile_name in config.get("profiles", {}):
        config["profiles"][profile_name]["password"] = password
        save_config(config_path, config)
        profile["password"] = password
        print("SSH 密码已保存到本地配置。")

    try:
        saved_backend_token = str(profile.get("backend_token") or "")
        backend_token = saved_backend_token
        if not backend_token:
            backend_token = getpass.getpass(
                "后端 API Token（输入时不会显示，重启成功后保存）："
            )
        if not backend_token:
            print("未提供后端 API Token，已取消重启。")
            return 2

        sftp = client.open_sftp()
        try:
            remote_home = sftp.normalize(".")
            remote_root = expand_remote_path(profile["remote_root"], remote_home)
        finally:
            sftp.close()

        print("正在手动重启远程后端...")
        health = restart_remote_service(client, remote_root, backend_token)
        if backend_token != saved_backend_token and config_path is not None and config is not None and profile_name in config.get("profiles", {}):
            config["profiles"][profile_name]["backend_token"] = backend_token
            save_config(config_path, config)
            profile["backend_token"] = backend_token
        print(f"远程后端已重启并通过健康检查：{health}")
        return 0
    finally:
        client.close()


def sync_files(
    profile_name: str,
    profile: dict,
    scope: str,
    items: list[SyncFile],
    assume_yes: bool,
    data_mode: str = "merge",
    config_path: Path | None = None,
    config: dict | None = None,
) -> int:
    print_sync_plan(profile_name, profile, scope, items, data_mode)
    password = str(profile.get("password") or "")
    had_saved_password = bool(password)
    if not password:
        password_prompt = "SSH 密码（输入时不会显示"
        if config_path is not None and config is not None:
            password_prompt += "，认证成功后保存到本地配置"
        password = getpass.getpass(password_prompt + "）：")
    if not password:
        print("SSH 密码不能为空", file=sys.stderr)
        return 2
    try:
        client = connect(profile, password)
    except paramiko.AuthenticationException:
        if had_saved_password:
            print("已保存的 SSH 密码无效或远程密码已变更。")
        else:
            print("SSH 密码认证失败。")
        password = getpass.getpass("请重新输入 SSH 密码（认证成功后更新本地配置）：")
        if not password:
            print("SSH 密码不能为空", file=sys.stderr)
            return 2
        client = connect(profile, password)
    password_changed = password != str(profile.get("password") or "")
    if password_changed and config_path is not None and config is not None and profile_name in config.get("profiles", {}):
        config["profiles"][profile_name]["password"] = password
        save_config(config_path, config)
        profile["password"] = password
        print("SSH 密码已保存到本地配置。")
    sftp = None
    temporary_paths: list[Path] = []
    try:
        sftp = client.open_sftp()
        remote_home = sftp.normalize(".")
        remote_root = expand_remote_path(profile["remote_root"], remote_home)
        states = inspect_files(sftp, items, remote_root)
        if data_mode == "merge":
            map_index = next(
                (index for index, state in enumerate(states) if state.item.remote_relative == "Broforce_maps_src/maps.json"),
                None,
            )
            if map_index is not None and states[map_index].remote_hash is not None:
                map_state = states[map_index]
                remote_raw = remote_file_bytes(sftp, map_state.remote_path)
                if remote_raw is None:
                    raise IOError("读取远程 maps.json 失败")
                merged_raw = merge_map_records(map_state.item.local_path.read_bytes(), remote_raw)
                temporary_fd, temporary_name = tempfile.mkstemp(prefix="broforce-merged-", suffix=".json")
                os.close(temporary_fd)
                temporary = Path(temporary_name)
                temporary_paths.append(temporary)
                temporary.write_bytes(merged_raw)
                local_size, local_hash = local_file_state(temporary)
                states[map_index] = FileState(
                    item=SyncFile(temporary, map_state.item.remote_relative, map_state.item.category),
                    local_size=local_size,
                    local_hash=local_hash,
                    remote_path=map_state.remote_path,
                    remote_size=map_state.remote_size,
                    remote_hash=map_state.remote_hash,
                )
                print(
                    f"maps.json 合并完成：本地 {len(load_map_records(map_state.item.local_path.read_bytes(), '本地 maps.json'))} 条，"
                    f"远程 {len(load_map_records(remote_raw, '远程 maps.json'))} 条，"
                    f"结果 {len(load_map_records(merged_raw, '合并后的 maps.json'))} 条。"
                )
        changed = [state for state in states if state.changed]
        unchanged = [state for state in states if not state.changed]

        print("\n远程比较结果：")
        for state in states:
            if not state.changed:
                status = "相同，跳过"
            elif state.remote_hash is None:
                status = "远程不存在，将创建"
            else:
                status = f"有差异，本地 {state.local_size} B / 远程 {state.remote_size} B"
            print(f"  - {state.item.remote_relative}: {status}")

        if not changed:
            print("所有文件都已同步，无需上传。")
            return 0

        data_changes = [
            state
            for state in changed
            if state.item.category == "data" and state.remote_hash is not None
        ]
        if data_changes and not assume_yes:
            print("\n注意：以下远程数据将被本地版本覆盖：")
            for state in data_changes:
                print(f"  - {state.remote_path}")
            if not ask_yes_no("继续同步并先创建远程备份吗？"):
                print("已取消，没有修改远程文件。")
                return 0
        elif not assume_yes and not ask_yes_no(f"确认上传 {len(changed)} 个有差异的文件吗？"):
            print("已取消，没有修改远程文件。")
            return 0

        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_root = posixpath.join(remote_root, ".sync-backups", timestamp)
        print(f"\n开始上传；远程旧文件备份目录：{backup_root}")
        backend_changed = any(needs_service_restart(state, remote_root) for state in changed)
        for index, state in enumerate(changed, start=1):
            print(f"[{index}/{len(changed)}] {state.item.remote_relative}")
            atomic_upload(sftp, state, backup_root)
            print(f"  SHA-256 校验通过：{state.local_hash}")

        print(f"同步完成：上传 {len(changed)} 个，跳过 {len(unchanged)} 个。")
        if backend_changed:
            saved_backend_token = str(profile.get("backend_token") or "")
            backend_token = saved_backend_token
            if not backend_token:
                backend_token = getpass.getpass(
                    "后端 API Token（用于自动重启 server.py，输入后保存）："
                )
            if backend_token:
                print("检测到 server.py 已更新，正在自动重启远程后端...")
                health = restart_remote_service(client, remote_root, backend_token)
                if backend_token != saved_backend_token and config_path is not None and config is not None and profile_name in config.get("profiles", {}):
                    config["profiles"][profile_name]["backend_token"] = backend_token
                    save_config(config_path, config)
                    profile["backend_token"] = backend_token
                print(f"远程后端已重启并通过健康检查：{health}")
            else:
                print("未提供后端 API Token，文件已同步，但远程后端未重启。")
        return 0
    finally:
        for temporary in temporary_paths:
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                pass
        if sftp is not None:
            sftp.close()
        client.close()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="选择本地主机配置并通过 SFTP 同步 Broforce 文件")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG, help="本地主机配置文件路径")
    parser.add_argument("--profile", help="直接使用指定配置，跳过主机选择菜单")
    parser.add_argument("--configure", nargs="?", const="", metavar="NAME", help="新增或编辑主机配置后退出")
    parser.add_argument("--list-profiles", action="store_true", help="列出本地主机配置后退出")
    parser.add_argument("--scope", choices=tuple(SCOPE_LABELS), help="同步范围，省略时显示选择菜单")
    parser.add_argument(
        "--data-mode",
        choices=tuple(DATA_MODE_LABELS),
        help="地图数据同步方式；默认合并，覆盖会用本地 maps.json 替换远程",
    )
    parser.add_argument("--plan", action="store_true", help="只显示本地同步计划，不连接远程主机")
    parser.add_argument("--restart", action="store_true", help="仅手动重启远程后端，不同步文件")
    parser.add_argument("-y", "--yes", action="store_true", help="跳过上传和覆盖确认")

    # Direct connection and single-file options keep the old command-line workflow usable.
    parser.add_argument("--host", help="不使用配置，直接指定 SSH 主机")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="直接连接的 SSH 端口")
    parser.add_argument("--username", help="不使用配置，直接指定 SSH 用户名")
    parser.add_argument("--remote-root", default=DEFAULT_REMOTE_ROOT, help="直接连接的远程项目根目录")
    parser.add_argument("--local", type=Path, help="仅同步一个本地文件")
    parser.add_argument("--remote", help="与 --local 配套的远程文件路径")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    config_path = args.config.resolve()
    try:
        config = load_config(config_path)
        if args.list_profiles:
            if not config["profiles"]:
                print(f"没有保存主机配置：{config_path}")
                return 0
            for name, raw_profile in config["profiles"].items():
                profile = validate_profile(name, raw_profile)
                print(
                    f"{name}: {profile['username']}@{profile['host']}:{profile['port']} "
                    f"{profile['remote_root']}"
                )
            return 0

        if args.configure is not None:
            configure_profile(config_path, config, args.configure)
            return 0

        if args.host or args.username:
            profile_name = "命令行"
            profile = validate_profile(
                profile_name,
                {
                    "host": args.host,
                    "port": args.port,
                    "username": args.username,
                    "password": "",
                    "remote_root": args.remote_root,
                },
            )
        else:
            profile_name, profile = select_profile(config_path, config, args.profile or "")

        if args.restart:
            if args.plan or args.local or args.remote or args.scope or args.data_mode:
                raise ValueError("--restart 不能与 --plan、--local、--remote、--scope 或 --data-mode 一起使用")
            uses_saved_profile = profile_name != "命令行"
            return manual_restart(
                profile_name,
                profile,
                config_path if uses_saved_profile else None,
                config if uses_saved_profile else None,
            )

        interactive_action = not any(
            (args.plan, args.local, args.remote, args.scope, args.data_mode)
        )
        if interactive_action and select_action() == "restart":
            uses_saved_profile = profile_name != "命令行"
            return manual_restart(
                profile_name,
                profile,
                config_path if uses_saved_profile else None,
                config if uses_saved_profile else None,
            )

        if args.local or args.remote:
            if not args.local or not args.remote:
                raise ValueError("--local 和 --remote 必须一起使用")
            scope = "custom"
            items = collect_single_file(args.local, args.remote)
        else:
            scope = select_scope(args.scope or "")
            items = collect_sync_files(scope)

        data_mode = ""
        if scope in {"data", "all"}:
            data_mode = select_data_mode(args.data_mode or "")

        if args.plan:
            print_sync_plan(profile_name, profile, scope, items, data_mode)
            print("计划模式：未连接远程主机，也没有上传文件。")
            return 0
        uses_saved_profile = profile_name != "命令行"
        return sync_files(
            profile_name,
            profile,
            scope,
            items,
            args.yes,
            data_mode or "merge",
            config_path if uses_saved_profile else None,
            config if uses_saved_profile else None,
        )
    except (ValueError, OSError, RuntimeError, paramiko.SSHException) as exc:
        print(f"同步失败：{exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
