from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import time
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any, Iterable


class SerKnowledgeError(RuntimeError):
    pass


class SerKnowledgeManager:
    """Builds a searchable SER knowledge corpus from a SER source ZIP/directory.

    Important: this module only updates *knowledge*. It never changes the runtime
    allowlist used by the game-server SER sandbox.
    """

    MAX_SOURCE_FILES = 10_000
    MAX_SINGLE_SOURCE_FILE_BYTES = 4 * 1024 * 1024
    MAX_TOTAL_UNCOMPRESSED_BYTES = 128 * 1024 * 1024

    _DESCRIPTION_RE = re.compile(
        r"public\s+override\s+string\s+Description\s*=>\s*(.*?);",
        re.IGNORECASE | re.DOTALL,
    )
    _ARG_RE = re.compile(
        r"new\s+([A-Za-z_][A-Za-z0-9_]*Argument(?:<[^>]+>)?)\s*\(\s*\"((?:\\.|[^\"\\])*)\"",
        re.DOTALL,
    )
    _CLASS_RE = re.compile(
        r"\bclass\s+([A-Za-z_][A-Za-z0-9_]*)Method\b",
        re.MULTILINE,
    )
    _ALIAS_BLOCK_RE = re.compile(
        r"Aliases\s*(?:=>|\{)\s*(.*?)(?:;|\n\s*\})",
        re.IGNORECASE | re.DOTALL,
    )
    _STRING_RE = re.compile(r'\"((?:\\.|[^\"\\])*)\"')

    def __init__(self, knowledge_dir: str | os.PathLike[str]) -> None:
        self.knowledge_dir = Path(knowledge_dir).expanduser().resolve()
        self.ser_dir = self.knowledge_dir / "ser"
        self.generated_dir = self.ser_dir / "generated"
        self.manifest_path = self.generated_dir / "ser_manifest.json"
        self.ser_dir.mkdir(parents=True, exist_ok=True)
        self.generated_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _decode_csharp_string(value: str) -> str:
        try:
            return bytes(value, "utf-8").decode("unicode_escape")
        except Exception:
            return value.replace(r'\"', '"').replace(r"\\", "\\")

    @classmethod
    def _join_csharp_strings(cls, expression: str) -> str:
        values = [cls._decode_csharp_string(match) for match in cls._STRING_RE.findall(expression)]
        return " ".join(part.strip() for part in values if part.strip()).strip()

    @staticmethod
    def _method_name_from_class(class_name: str) -> str:
        return class_name.replace("_", ".")

    @staticmethod
    def _safe_text(raw: bytes) -> str:
        return raw.decode("utf-8-sig", errors="replace")

    @staticmethod
    def _sha256_bytes(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def _normalize_archive_name(name: str) -> str:
        path = PurePosixPath(name)
        if path.is_absolute() or ".." in path.parts:
            raise SerKnowledgeError(f"Unsicherer ZIP-Pfad: {name}")
        return str(path)

    def _read_zip(self, path: Path) -> tuple[dict[str, bytes], str]:
        if not path.is_file():
            raise SerKnowledgeError(f"SER-ZIP nicht gefunden: {path}")
        raw_archive = path.read_bytes()
        digest = self._sha256_bytes(raw_archive)
        result: dict[str, bytes] = {}
        try:
            with zipfile.ZipFile(path) as archive:
                files = [info for info in archive.infolist() if not info.is_dir()]
                if len(files) > self.MAX_SOURCE_FILES:
                    raise SerKnowledgeError(
                        f"SER-ZIP enthält zu viele Dateien ({len(files)}/{self.MAX_SOURCE_FILES})."
                    )
                total_uncompressed = sum(max(0, int(info.file_size)) for info in files)
                if total_uncompressed > self.MAX_TOTAL_UNCOMPRESSED_BYTES:
                    raise SerKnowledgeError(
                        "SER-ZIP ist entpackt zu groß "
                        f"({total_uncompressed}/{self.MAX_TOTAL_UNCOMPRESSED_BYTES} Bytes)."
                    )
                for info in files:
                    name = self._normalize_archive_name(info.filename)
                    if info.file_size > self.MAX_SINGLE_SOURCE_FILE_BYTES:
                        continue
                    result[name] = archive.read(info)
        except (zipfile.BadZipFile, OSError) as exc:
            raise SerKnowledgeError(f"Ungültiges SER-ZIP: {exc}") from exc
        return result, digest

    def _read_directory(self, path: Path) -> tuple[dict[str, bytes], str]:
        if not path.is_dir():
            raise SerKnowledgeError(f"SER-Quellordner nicht gefunden: {path}")
        result: dict[str, bytes] = {}
        hasher = hashlib.sha256()
        total = 0
        count = 0
        for file_path in sorted(path.rglob("*")):
            if not file_path.is_file():
                continue
            size = file_path.stat().st_size
            if size > self.MAX_SINGLE_SOURCE_FILE_BYTES:
                continue
            count += 1
            total += max(0, int(size))
            if count > self.MAX_SOURCE_FILES or total > self.MAX_TOTAL_UNCOMPRESSED_BYTES:
                raise SerKnowledgeError("SER-Quellordner überschreitet sichere Importlimits.")
            rel = file_path.relative_to(path).as_posix()
            raw = file_path.read_bytes()
            result[rel] = raw
            hasher.update(rel.encode("utf-8"))
            hasher.update(b"\0")
            hasher.update(raw)
        return result, hasher.hexdigest()

    @staticmethod
    def _strip_single_root(files: dict[str, bytes]) -> dict[str, bytes]:
        if not files:
            return files
        first_parts = {PurePosixPath(name).parts[0] for name in files if PurePosixPath(name).parts}
        if len(first_parts) != 1:
            return files
        root = next(iter(first_parts))
        prefix = root.rstrip("/") + "/"
        return {name[len(prefix):]: raw for name, raw in files.items() if name.startswith(prefix)}

    @classmethod
    def _extract_method(cls, path: str, raw: bytes) -> dict[str, Any] | None:
        text = cls._safe_text(raw)
        class_match = cls._CLASS_RE.search(text)
        if not class_match:
            return None

        class_name = class_match.group(1)
        method_name = cls._method_name_from_class(class_name)
        description_match = cls._DESCRIPTION_RE.search(text)
        description = cls._join_csharp_strings(description_match.group(1)) if description_match else ""

        args: list[dict[str, str]] = []
        seen: set[tuple[str, str]] = set()
        for arg_type, arg_name in cls._ARG_RE.findall(text):
            key = (arg_name, arg_type)
            if key in seen:
                continue
            seen.add(key)
            if "<" in arg_type and arg_type.endswith(">"):
                base, generic = arg_type.split("<", 1)
                normalized_type = f"{base.removesuffix('Argument')}<{generic}"
            else:
                normalized_type = arg_type.removesuffix("Argument")
            args.append({
                "name": cls._decode_csharp_string(arg_name),
                "type": normalized_type,
            })

        aliases: list[str] = []
        alias_match = cls._ALIAS_BLOCK_RE.search(text)
        if alias_match:
            aliases = [cls._decode_csharp_string(value) for value in cls._STRING_RE.findall(alias_match.group(1))]

        parts = PurePosixPath(path).parts
        subgroup = "Unknown"
        if "Methods" in parts:
            index = parts.index("Methods")
            if index + 1 < len(parts) - 1:
                subgroup = parts[index + 1].removesuffix("Methods").replace("_", " ")

        return {
            "name": method_name,
            "description": description,
            "arguments": args,
            "aliases": aliases,
            "subgroup": subgroup,
            "source": path,
            "runtime_permission": "DENY_BY_DEFAULT",
        }

    @staticmethod
    def _write_text(path: Path, text: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text.rstrip() + "\n", encoding="utf-8")

    def _clear_generated(self) -> None:
        if self.generated_dir.exists():
            shutil.rmtree(self.generated_dir)
        self.generated_dir.mkdir(parents=True, exist_ok=True)

    def import_source(self, source: str | os.PathLike[str]) -> dict[str, Any]:
        source_path = Path(source).expanduser().resolve()
        if source_path.is_dir():
            files, digest = self._read_directory(source_path)
            source_type = "directory"
        else:
            files, digest = self._read_zip(source_path)
            source_type = "zip"
        files = self._strip_single_root(files)

        methods: list[dict[str, Any]] = []
        for name, raw in files.items():
            if name.startswith("Code/MethodSystem/Methods/") and name.endswith("Method.cs"):
                entry = self._extract_method(name, raw)
                if entry:
                    methods.append(entry)
        methods.sort(key=lambda item: (item["subgroup"].lower(), item["name"].lower()))

        self._clear_generated()

        copied_docs = 0
        for source_name, target_name in (
            ("language_specification.md", "language_specification.md"),
            ("README.md", "README_SER.md"),
            ("PROJECT_GUIDE.md", "PROJECT_GUIDE.md"),
        ):
            raw = files.get(source_name)
            if raw is not None:
                self._write_text(self.generated_dir / target_name, self._safe_text(raw))
                copied_docs += 1

        examples_written = 0
        for name, raw in files.items():
            if not name.startswith("Example Scripts/") or not name.lower().endswith(".ser"):
                continue
            target = self.generated_dir / "examples" / Path(name).name
            self._write_text(target, self._safe_text(raw))
            examples_written += 1

        grouped: dict[str, list[dict[str, Any]]] = {}
        for method in methods:
            grouped.setdefault(method["subgroup"], []).append(method)

        for subgroup, entries in grouped.items():
            safe_group = re.sub(r"[^A-Za-z0-9_.-]+", "_", subgroup).strip("_") or "Unknown"
            lines = [
                f"# SER Methoden — {subgroup}",
                "",
                "> Wissenseinträge beschreiben Fähigkeiten. Sie erteilen KEINE Runtime-Berechtigung. Neue Methoden bleiben DEFAULT-DENY.",
                "",
            ]
            for item in entries:
                args = ", ".join(f"{arg['name']}: {arg['type']}" for arg in item["arguments"]) or "keine"
                aliases = ", ".join(item["aliases"]) or "keine"
                lines.extend([
                    f"## {item['name']}",
                    f"- Beschreibung: {item['description'] or 'Keine Beschreibung extrahiert.'}",
                    f"- Argumente: {args}",
                    f"- Aliases: {aliases}",
                    f"- Quelle: `{item['source']}`",
                    "- AI-Sandbox: **DENY_BY_DEFAULT**, bis serverseitig explizit freigegeben.",
                    "",
                ])
            self._write_text(self.generated_dir / f"methods_{safe_group}.md", "\n".join(lines))

        method_index = {
            "generated_at": time.time(),
            "source_sha256": digest,
            "method_count": len(methods),
            "methods": methods,
        }
        self._write_text(
            self.generated_dir / "ser_methods.json",
            json.dumps(method_index, ensure_ascii=False, indent=2),
        )

        manifest = {
            "status": "ok",
            "generated_at": time.time(),
            "source": source_path.name,
            "source_type": source_type,
            "source_sha256": digest,
            "methods": len(methods),
            "groups": len(grouped),
            "examples": examples_written,
            "docs": copied_docs,
            "runtime_allowlist_changed": False,
        }
        self._write_text(self.manifest_path, json.dumps(manifest, ensure_ascii=False, indent=2))
        return manifest

    def status(self) -> dict[str, Any]:
        if not self.manifest_path.is_file():
            return {
                "status": "empty",
                "methods": 0,
                "groups": 0,
                "examples": 0,
                "runtime_allowlist_changed": False,
            }
        try:
            payload = json.loads(self.manifest_path.read_text(encoding="utf-8"))
            if isinstance(payload, dict):
                return payload
        except (OSError, json.JSONDecodeError):
            pass
        return {"status": "invalid_manifest", "runtime_allowlist_changed": False}


def _main() -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="SCP-1356: dynamische Scripted Events Reloaded Wissensbasis"
    )
    parser.add_argument(
        "--knowledge-dir",
        default=str(Path(__file__).resolve().parent / "knowledge"),
        help="Knowledge-Verzeichnis der AI-App (Standard: ./knowledge)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    import_cmd = sub.add_parser("import", help="SER Source-ZIP oder Source-Ordner importieren")
    import_cmd.add_argument("source", help="Pfad zum SER ZIP/Quellordner")
    sub.add_parser("status", help="Aktuellen SER Knowledge-Manifeststatus anzeigen")

    args = parser.parse_args()
    manager = SerKnowledgeManager(args.knowledge_dir)
    try:
        if args.command == "import":
            result = manager.import_source(args.source)
        else:
            result = manager.status()
    except SerKnowledgeError as exc:
        parser.error(str(exc))
        return 2

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
