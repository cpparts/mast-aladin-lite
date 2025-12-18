from abc import ABC, abstractmethod
from IPython.display import display
from mast_aladin.app import gca


class ViewerSyncAdapter(ABC):
    @abstractmethod
    def sync_to(self, sync_viewer):
        raise NotImplementedError

    @abstractmethod
    def add_callback(self, func):
        raise NotImplementedError

    @abstractmethod
    def remove_callback(self, func):
        raise NotImplementedError


class AladinSyncAdapter(ViewerSyncAdapter):
    def __init__(self, viewer=None):
        self.viewer = viewer
        self.aid = self.viewer.aid

    def sync_to(self, sync_viewer):
        self.aid.set_viewport(
            **sync_viewer.aid.get_viewport(sky_or_pixel="sky")
        )

    def add_callback(self, func):
        self.viewer.observe(func, names=["_fov", "_target", "_rotation"])

    def remove_callback(self, func):
        self.viewer.unobserve(func, names=["_fov", "_target", "_rotation"])


class ImvizSyncAdapter(ViewerSyncAdapter):
    def __init__(self, viewer=None):
        self.app = viewer
        self.viewer = self.app.default_viewer
        self.aid = self.viewer._obj.glue_viewer.aid

    def sync_to(self, sync_viewer):
        self.aid.set_viewport(**sync_viewer.aid.get_viewport())

    def add_callback(self, func):
        self.viewer._obj.glue_viewer.state.add_callback('zoom_radius', func)

    def remove_callback(self, func):
        self.viewer._obj.glue_viewer.state.remove_callback('zoom_radius', func)
