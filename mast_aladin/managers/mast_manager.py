from .app_manager import AppManager
from .sidecar_manager import AppSidecarManager
from .plugin_manager import PluginManager


class MastManager():
    def __init__(self):
        self._app_manager = AppManager()
        self._plugin_manager = PluginManager(self._app_manager)
        self._sidecar_manager = AppSidecarManager(self._app_manager, self._plugin_manager)

    @property
    def AppManager(self):
        return self._app_manager

    @property
    def apps(self):
        return self._app_manager.apps

    @property
    def UiManager(self):
        return self._ui_manager

    @property
    def SidecarManager(self):
        return self._sidecar_manager

    @property
    def PluginManager(self):
        return self._plugin_manager

    @property
    def plugins(self):
        return self._plugin_manager.plugins

    def register_app(self, app, idx):
        self._app_manager.register_app(app, idx)

    def open_sidecar(self):
        self._sidecar_manager.open()

    def open_plugins(self):
        self._plugin_manager.display_all_plugins()

    def open(self):
        self.open_sidecar()
        self.open_plugins()