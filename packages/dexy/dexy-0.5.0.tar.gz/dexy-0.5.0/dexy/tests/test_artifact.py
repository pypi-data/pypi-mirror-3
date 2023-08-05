from dexy.artifact import Artifact
from dexy.artifacts.file_system_json_artifact import FileSystemJsonArtifact
from dexy.tests.utils import tempdir
import dexy.utils
import os

def is_empty_dict(d):
    return isinstance(d, dict) and not d

def test_empty_dict():
    x = {}
    assert is_empty_dict(x)
    x['a'] = 5
    assert not is_empty_dict(x)

def test_artifact_init():
    artifact = Artifact()
    assert artifact.state == 'new'

def test_artifact_filenames_simple_key():
    artifact = Artifact()
    artifact.key = 'abc'
    artifact.ext = '.out'
    assert artifact.canonical_filename() == 'abc.out'
    assert artifact.long_canonical_filename() == 'abc.out'

def test_artifact_filenames_file_key():
    artifact = Artifact()
    artifact.key = 'abc.txt'
    artifact.ext = '.out'
    assert artifact.canonical_filename() == 'abc.out'
    assert artifact.long_canonical_filename() == 'abc.txt.out'

def test_artifact_filenames_file_key_with_filters():
    artifact = Artifact()
    artifact.key = 'abc.txt|def|ghi'
    artifact.ext = '.out'
    assert artifact.canonical_filename() == 'abc.out'
    assert artifact.long_canonical_filename() == 'abc.txt-def-ghi.out'

def test_add_additional_artifact():
    db = dexy.utils.get_db(logsdir=None, dbfile=None)
    hashstring = "abcdef123"
    artifact = Artifact()
    artifact.db = db
    artifact.key = 'abc.txt'
    artifact.artifacts_dir = 'artifactsx'
    artifact.hashstring = hashstring

    new_artifact = artifact.add_additional_artifact('def.txt', '.txt')

    assert is_empty_dict(new_artifact._inputs)
    assert new_artifact.args.keys() == ["globals"]
    assert is_empty_dict(new_artifact.args['globals'])
    assert new_artifact.additional
    assert new_artifact.artifact_class_source
    assert new_artifact.artifacts_dir == 'artifactsx'
    assert new_artifact.final
    assert new_artifact.key in artifact.inputs()
    assert new_artifact.state == 'new'
    assert new_artifact.inode == hashstring

    assert db.artifact_row(new_artifact)['key'] == new_artifact.key

def test_simple_metadata():
    with tempdir():
        os.mkdir('artifacts')

        HASHSTRING = 'abc123'
        a1 = FileSystemJsonArtifact()
        a1.hashstring = HASHSTRING
        a1.key = 'xyz'
        a1.save_meta()

        a2 = FileSystemJsonArtifact()
        a2.hashstring = HASHSTRING
        assert not a2.key
        a2.load_meta()
        assert a2.key == 'xyz'

