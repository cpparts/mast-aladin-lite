import pytest
from unittest.mock import Mock, MagicMock, patch
from mast_aladin.managers.mast_manager import MastManager


class TestMastManager:
    """Test suite for MastManager class."""

    @pytest.fixture
    def mock_mast_manager(self):
        """Create a mock MastManager instance."""
        return MastManager()

    def test_initialization(self):
        """Test that MastManager initializes correctly."""
        mast_manager = MastManager()
        assert mast_manager._app_manager is not None

    @patch("mast_aladin.managers.mast_manager.PluginManager")
    def test_register_app(self, mock_plugin_manager):
        """Test registering an app through MastManager."""
        mock_app = Mock()

        mast_manager = MastManager()
        mast_manager.register_app(mock_app, "test_app")

        assert "test_app" in mast_manager.apps
        assert mast_manager.apps["test_app"] is mock_app

    @patch("mast_aladin.managers.mast_manager.PluginManager")
    def test_register_app_multiple(self, mock_plugin_manager):
        """Test registering multiple mock app objects."""
        # Mock different app types
        mock_aladin = MagicMock(name="aladin")
        mock_imviz = MagicMock(name="imviz")
        mock_custom = MagicMock(name="custom_app")

        mast_manager = MastManager()
        mast_manager.register_app(mock_aladin, "aladin")
        mast_manager.register_app(mock_imviz, "imviz")
        mast_manager.register_app(mock_custom, "custom")

        assert len(mast_manager.apps) == 3
        assert mast_manager.apps["aladin"] is mock_aladin
        assert mast_manager.apps["imviz"] is mock_imviz
        assert mast_manager.apps["custom"] is mock_custom

    @patch("mast_aladin.managers.mast_manager.PluginManager")
    def test_register_app_duplicate_id_raises_error(self, mock_plugin_manager):
        """Test that registering with duplicate ID raises ValueError."""
        mock_app1 = Mock()
        mock_app2 = Mock()

        mast_manager = MastManager()
        mast_manager.register_app(mock_app1, "duplicate")

        with pytest.raises(ValueError) as exc_info:
            mast_manager.register_app(mock_app2, "duplicate")

        assert "duplicate" in str(exc_info.value)
