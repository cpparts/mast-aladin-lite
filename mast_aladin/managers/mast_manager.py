from .app_manager import AppManager
from .plugin_manager import PluginManager


class MastManager():
    """
    Coordinates interactions and overall workflow between components of the MAST Aladin ecosystem
    Ensures seamless integration and communication between applications, plugins, and sidecars.
    """
    def __init__(self):
        self._app_manager = AppManager(self)
        self._plugin_manager = PluginManager(self)
        # todo: add the other managers here
        # - sidecar manager: responsible for managing sidecar windows.abs

    @property
    def AppManager(self):
        return self._app_manager

    @property
    def apps(self):
        return self._app_manager.apps

    @property
    def PluginManager(self):
        return self._plugin_manager

    @property
    def plugins(self):
        return self._plugin_manager.plugins

    def register_app(self, app, id):
        """
        This is a passthrough method that allows users to register an app to the AppManager
        directly from the MastManager.This is the recommended way to register apps, as it
        allows the MastManager to keep track of all registered applications and facilitate
        communication between them as needed.

        Parameters
        ----------
        app : object
            The application instance to be registered.

        id : str
            A unique identifier for the application.
        """
        self._app_manager.register_app(app, id)
        # communicate this change to other managers as needed (e.g. plugin manager, sidecar manager)

    def display_plugin(self, plugin_id):
        self._plugin_manager.display_plugin(plugin_id)

    def display_plugins(self):
        self._plugin_manager.display()
