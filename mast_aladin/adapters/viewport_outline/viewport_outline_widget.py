import ipywidgets as widgets
from IPython.display import display

from .viewport_outline_adapter import ImvizViewportOverlayAdapter, AladinViewportOverlayAdapter
from mast_aladin import MastAladin
from jdaviz import Imviz


ADAPTERS = {
    MastAladin: AladinViewportOverlayAdapter,
    Imviz: ImvizViewportOverlayAdapter,
}

class ViewportOutlinePlugin():
    def __init__(self, app_manager):
        self.app_manager = app_manager

        # register all of the app adapters
        self._adapters = {}
        self._links = {}
        self._links_ui = []
        self.register_adapters()

        self._generate_ui()

    def _generate_ui(self):
        self.title = widgets.Label(value="Viewer Outline Plugin")

        self.source_dropdown = widgets.Dropdown(
            options = ['', *self._adapters.keys()],
            value='',
            description='Source:',
            disabled=False
        )

        self.destination_dropdown = widgets.Dropdown(
            options = ['', 'All', *self._adapters.keys()],
            value='',
            description='Destination:',
            disabled=False
        )

        self.draw_button = widgets.Button(
            description="Draw",
            disabled=False,
            button_style='success',
            tooltip='Draw viewport of source on destination',
        )

        self.draw_button.on_click(self._draw_button_on_click)

        self.link_controls = widgets.VBox([])

        self.ui = widgets.VBox([
            self.title,
            widgets.HBox([
                self.source_dropdown, self.destination_dropdown, self.draw_button
            ]),
            self.link_controls
        ])

    def _draw_button_on_click(self, btn):
        source = self.source_dropdown.value
        destination = self.destination_dropdown.value

        if source == destination:
            raise ValueError("Cannot draw a widgets viewport on itself.")

        if '' in [source, destination]:
            raise ValueError("Please choose a value for both source and destination.")

        if destination == 'All':
            for idx in self._adapters.keys():
                if idx != source:
                    self._create_new_link(source, idx)
        else:
            self._create_new_link(source, destination)

    def _create_new_link(self, source, destination):
        new_link = ViewportOutlineLink(self._adapters[source], self._adapters[destination])

        if new_link in self._links:
            raise ValueError(f"Link already exists: {new_link}")

        new_link.enable()
        self._links[str(new_link)] = new_link

        tog = widgets.ToggleButtons(
            options=['Enable', 'Disable'],
            description=str(new_link),
            disabled=False,
            button_style=''
        )
        tog.observe(new_link.toggle, names="value")

        self._links_ui.append(
            widgets.HBox(
               [tog]
            )
        )
        self.link_controls.children = self._links_ui

    def register_adapters(self):
        for idx, app in self.app_manager.apps.items():
            for app_type, adapter_cls in ADAPTERS.items():
                if isinstance(app, app_type) and idx not in self._adapters:
                    self._adapters[idx] = adapter_cls(app)
                    break
                else:
                    raise ValueError(f"Unsupported app type: {type(app)}")

    def display(self):
        display(self.ui)


class ViewportOutlineLink():
    def __init__(self, source, destination):
        self.source = source
        self.destination = destination

    def toggle(self, change):
        command = change['new']

        if command == 'Enable':
            self.enable()

        if command == 'Disable':
            self.disable()

    def enable(self):
        self.destination.add_overlay_from(self.source)

    def disable(self):
        self.destination.remove_overlay()

    def __repr__(self):
        return f"Viewport outline link from {self.source.app_name} -> {self.destination.app_name}"
