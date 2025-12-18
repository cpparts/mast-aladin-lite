from abc import ABC, abstractmethod
from datetime import datetime

class ViewportOverlayAdapter(ABC):
    """
    This class needs to know how to do the following operations

    - get the current viewport: in order to overlay the viewport onto another 
      app, you need to know the viewport

    - attach a listener to the app: in order to update the overlay in real time,
      we need to attach a listener to any changes on the viewport

    - add the viewport overlay: we need to take in a viewport and add it as an overlay
      to the application

    - clear the viewport overlay: we need to clear the viewport overlay if its no longer desired
    """

    @property
    @abstractmethod
    def viewport(self):
        pass

    @property
    @abstractmethod
    def app_name(self):
        pass

    @property
    @abstractmethod
    def overlay(self):
        pass
    
    @abstractmethod
    def clear_overlay(self):
        raise NotImplementedError

    @abstractmethod
    def add_overlay_from(self, source):
        raise NotImplementedError

    @abstractmethod
    def remove_overlay(self):
        raise NotImplementedError

    @abstractmethod
    def add_callback(self, func):
        raise NotImplementedError

    @abstractmethod
    def remove_callback(self, func):
        raise NotImplementedError

    def _viewport_label(self, app_name=None):
        """
        Generate a label for the viewport outline overlay layers.
        """
        # hours, minutes, seconds:
        time = datetime.now().time().strftime('%H:%M:%S')
        return (
            ('' if app_name is None else f"{app_name} @ ") + time
        )
    
class AladinViewportOverlayAdapter(ViewportOverlayAdapter):
    def __init__(self, viewer=None):
        self.viewer = viewer if viewer else gca()

        self._overlay = None
        self.overlay_color = '#ff0000'
        self.overlay_width = 4

    @property
    def viewport(self):
        return self.viewer.get_viewport_region()

    @property
    def app_name(self):
        # todo: replace this with a custom name from the viewer
        return "Mast Aladin"

    @property
    def overlay(self):
        return self._overlay

    def _callback_method(self, caller):
        self.clear_overlay()
        self._overlay = self.viewer.add_graphic_overlay_from_region(
            region=self.source.viewport,
            name=self._viewport_label(app_name=self.source.app_name),
            color=self.overlay_color,
            lineWidth=self.overlay_width,
        )

    def add_overlay_from(self, source):
        self.source = source
        self._callback_method(None)
        self.source.add_callback(self._callback_method)

    def clear_overlay(self):
        """
        Clear the latest viewport overlay drawn in aladin.
        """
        if self.overlay is not None:
            overlay_label = self.overlay['options']['name']
            if overlay_label in self.viewer._overlays:
                self.viewer.remove_overlay(self.overlay)
            self._overlay = None

    def remove_overlay(self):
        self.source.remove_callback(self._callback_method)
        self.clear_overlay()
        self.source = None

    def add_callback(self, func):
        self.viewer.observe(func, names=["_fov", "_target", "_rotation"])

    def remove_callback(self, func):
        self.clear_overlay()
        self.viewer.unobserve(func, names=["_fov", "_target", "_rotation"])
        self.source = None


class ImvizViewportOverlayAdapter(ViewportOverlayAdapter):
    def __init__(self, viewer=None):
        # todo: assert the type of the viewer is jdaviz/imviz
        from jdaviz.configs.imviz.helper import _current_app
        self.app = viewer if viewer else _current_app
        self.viewer = self.app.default_viewer
        self.glue_viewer = self.viewer._obj.glue_viewer

        self._overlay = None
        self.overlay_color = '#ff0000'
        self.overlay_width = 4

    @property
    def viewport(self):
        return self.viewer.get_viewport_region()

    @property
    def app_name(self):
        # todo: replace this with a custom name from the viewer
        return "Imviz"

    @property
    def overlay(self):
        return self._overlay

    def _callback_method(self, caller):
        self.clear_overlay()
        self._overlay = dict(
            region=self.source.viewport,
            region_label=self._viewport_label(app_name=self.source.app_name),
            colors=[self.overlay_color],
            stroke_width=self.overlay_width,
        )

        self.glue_viewer._add_region_overlay(**self._overlay)

    def add_overlay_from(self, source):
        self.source = source
        self._callback_method(None)
        self.source.add_callback(self._callback_method)

    def remove_overlay(self):
        self.source.remove_callback(self._callback_method)
        self.source = None

    def clear_overlay(self):
        """
        Clear the latest viewport overlay drawn in imviz.
        """
        if self._overlay is not None:
            overlay_label = self.overlay['region_label']
            if overlay_label in self.glue_viewer._get_region_overlay_labels():
                self.glue_viewer._remove_region_overlay(overlay_label)
            self._overlay = None

    def add_callback(self, func):
        self.glue_viewer.state.add_callback('x_min', func)

    def remove_callback(self, func):
        self.clear_overlay()
        self.glue_viewer.state.remove_callback('x_min', func)
        self.source = None
