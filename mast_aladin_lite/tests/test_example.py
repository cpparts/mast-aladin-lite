from mast_aladin_lite import MastAladin


def test_instance_creation(MastAladin_app):
    assert isinstance(MastAladin_app, MastAladin)
