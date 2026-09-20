#!/usr/bin/env python3
"""Read-only skill package inventory. Uses stdlib; never imports source code."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re

IGNORED = {'.git', 'node_modules', '__pycache__', '.venv'}
DEPENDENCIES = {
    'codex-runtime': r'load_workspace_dependencies|codex-runtimes|/home/oai|/mnt/data',
    'artifact-tool': r'@oai/artifact-tool|artifact_tool',
    'host-execution': r'functions\.exec|nodeRepl|\bcua\.',
    'openai-tools': r'mcp__codex|mcp__.*__|tools\.exec_command|list_document_sessions',
    'openai-presentation': r'window\.openai|codex-file-citation|codex-followup|\ue200visualize|artifact-template-card',
    'telemetry': r'mark_artifact_operation_started',
    'codex-paths': r'CODEX_HOME|\.codex/|plugin://|skill://',
}


def files_under(root):
    """Walk without following symlinks or managed dependency trees."""
    for parent, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in IGNORED)
        for d in dirs:
            path = Path(parent) / d
            if path.is_symlink():
                yield path
        for name in sorted(files):
            yield Path(parent) / name


def inventory(source):
    supplied = Path(source).expanduser()
    if supplied.is_symlink():
        raise ValueError('Source must not be a symlink')
    source = supplied.resolve(strict=True)
    if source.is_file() and source.name != 'SKILL.md':
        raise ValueError('Expected SKILL.md, a skill directory, or a plugin/cache directory')
    root = source.parent if source.is_file() else source
    skills = [source] if source.is_file() else sorted(
        p for p in files_under(root) if p.name == 'SKILL.md' and not p.is_symlink()
    )
    result = {'schema_version': 1, 'skills': [], 'duplicate_names': {}, 'warnings': []}
    names = {}
    for skill in skills:
        directory = skill.parent
        text = skill.read_text(encoding='utf-8')
        # Identity is advisory; destination validation uses its real YAML parser.
        front = re.match(r'\A---\s*\n(.*?)\n---(?:\s*\n|$)', text, re.S)
        name_match = re.search(r'^name:\s*([^\n]+)', front[1], re.M) if front else None
        name = name_match[1].strip().strip('\"\'') if name_match else directory.name
        row = {'name': name, 'source': str(skill.relative_to(root)), 'files': [],
               'dependency_signals': {}, 'notices': [], 'sidecars': [], 'warnings': []}
        if not name_match:
            row['warnings'].append('Missing or unsupported frontmatter name; validate with YAML parser')
        names.setdefault(name, []).append(row['source'])
        for path in sorted(files_under(directory)):
            rel = str(path.relative_to(directory))
            if path.is_symlink():
                row['warnings'].append(f'Symlink requires review; not read: {rel}')
                continue
            if not path.is_file():
                continue
            data = path.read_bytes()
            row['files'].append({'path': rel, 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()})
            if re.match(r'(?i)(license|notice|copying|copyright)', path.name):
                row['notices'].append(rel)
            if path.suffix.lower() in {'.md', '.py', '.js', '.mjs', '.json', '.yaml', '.yml', '.txt', '.html'}:
                content = data.decode('utf-8', errors='replace')
                for signal, pattern in DEPENDENCIES.items():
                    if re.search(pattern, content):
                        row['dependency_signals'].setdefault(signal, []).append(rel)
        # Inspect package metadata at ancestors bounded by the requested source.
        for parent in (directory, *directory.parents):
            if parent != root and root not in parent.parents:
                break
            for relative in ('plugin.json', '.codex-plugin/plugin.json', 'mcp.json', '.mcp.json', 'LICENSE', 'LICENSE.txt', 'NOTICE'):
                path = parent / relative
                if path.is_file() and not path.is_symlink() and not any(p.is_symlink() for p in path.parents if p != root and root in p.parents):
                    sidecar = {'path': str(path.relative_to(root)),
                               'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
                    if path.name == 'plugin.json':
                        try:
                            metadata = json.loads(path.read_text(encoding='utf-8'))
                            if isinstance(metadata, dict):
                                sidecar['plugin'] = {key: metadata[key] for key in ('name', 'version', 'license')
                                                     if isinstance(metadata.get(key), str)}
                        except (ValueError, UnicodeError):
                            row['warnings'].append(f'Invalid plugin JSON: {sidecar["path"]}')
                    row['sidecars'].append(sidecar)
            if parent == root:
                break
        result['skills'].append(row)
    result['duplicate_names'] = {name: paths for name, paths in names.items() if len(paths) > 1}
    if not skills:
        result['warnings'].append('No skills found')
    if result['duplicate_names']:
        result['warnings'].append('Select source versions or rename collisions explicitly; do not merge blindly')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source')
    args = parser.parse_args()
    try:
        result = inventory(args.source)
    except (OSError, ValueError) as error:
        parser.exit(2, f'{error}\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
