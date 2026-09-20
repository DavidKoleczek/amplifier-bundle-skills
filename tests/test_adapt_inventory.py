"""Real source-package inventory, including cached versions and unsafe links."""
import importlib.util
from pathlib import Path
import hashlib

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / 'skills/adapt-skill/scripts/inspect_source.py'
spec = importlib.util.spec_from_file_location('inspect_source', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def make_skill(root, version='1.0'):
    folder = root / 'cache/openai-primary-runtime/example' / version / 'skills/demo'
    folder.mkdir(parents=True)
    (folder / 'SKILL.md').write_text('---\nname: demo\ndescription: Example\n---\nRead references/data.md\n')
    return folder


def test_whole_package_hashes_resources_and_flags_runtime(tmp_path):
    folder = make_skill(tmp_path)
    (folder / 'references').mkdir()
    data = b'Use @oai/artifact-tool with load_workspace_dependencies.'
    (folder / 'references/data.md').write_bytes(data)
    (folder / 'LICENSE.txt').write_text('Source notice')
    (folder / 'node_modules').mkdir()
    (folder / 'node_modules/secret.js').write_text('excluded')
    result = module.inventory(tmp_path)
    assert len(result['skills']) == 1
    row = result['skills'][0]
    assert row['source'].endswith('/1.0/skills/demo/SKILL.md')
    files = {f['path']: f for f in row['files']}
    assert files['references/data.md']['sha256'] == hashlib.sha256(data).hexdigest()
    assert not any('node_modules' in path for path in files)
    assert row['notices'] == ['LICENSE.txt']
    assert row['dependency_signals']['artifact-tool'] == ['references/data.md']
    assert row['dependency_signals']['codex-runtime'] == ['references/data.md']


def test_versions_are_reported_as_collisions_not_implicitly_selected(tmp_path):
    make_skill(tmp_path, '9.0')
    make_skill(tmp_path, '10.0')
    result = module.inventory(tmp_path)
    assert len(result['skills']) == 2
    assert len(result['duplicate_names']['demo']) == 2


def test_symlink_file_and_directory_contents_are_never_read(tmp_path):
    source = tmp_path / 'source'
    folder = make_skill(source)
    external = tmp_path / 'outside'
    external.mkdir()
    (external / 'SKILL.md').write_text('must not become a skill')
    (folder / 'escape.md').symlink_to(external / 'SKILL.md')
    (folder / 'linked').symlink_to(external, target_is_directory=True)
    result = module.inventory(source)
    assert len(result['skills']) == 1
    assert len(result['skills'][0]['warnings']) == 2
    assert [f['path'] for f in result['skills'][0]['files']] == ['SKILL.md']


def test_single_file_input_and_empty_or_invalid_sources(tmp_path):
    folder = make_skill(tmp_path)
    assert len(module.inventory(folder / 'SKILL.md')['skills']) == 1
    empty = tmp_path / 'empty'
    empty.mkdir()
    assert module.inventory(empty)['warnings'] == ['No skills found']
    invalid = tmp_path / 'file.txt'
    invalid.write_text('not a skill')
    with pytest.raises(ValueError):
        module.inventory(invalid)


def test_plugin_metadata_is_included_without_loading_it(tmp_path):
    folder = make_skill(tmp_path)
    plugin = folder.parent.parent / '.codex-plugin'
    plugin.mkdir()
    (plugin / 'plugin.json').write_text('{"name":"example","version":"1.0","license":"Proprietary","other":"not exported"}')
    row = module.inventory(tmp_path)['skills'][0]
    assert len(row['sidecars']) == 1
    assert row['sidecars'][0]['path'].endswith('.codex-plugin/plugin.json')
    assert row['sidecars'][0]['plugin'] == {'name': 'example', 'version': '1.0', 'license': 'Proprietary'}
