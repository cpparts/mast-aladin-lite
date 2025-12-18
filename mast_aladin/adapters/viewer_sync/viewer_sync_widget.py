import ipywidgets as widgets
from IPython.display import display

from .viewer_sync_adapter import ImvizSyncAdapter, AladinSyncAdapter
from mast_aladin import MastAladin
from jdaviz import Imviz


ADAPTERS = {
    MastAladin: AladinSyncAdapter,
    Imviz: ImvizSyncAdapter,
}


class ViewerSyncPlugin():
    def __init__(self, app_manager):
        self.app_manager = app_manager
        self.viewer_sync_manager = ViewerSyncManager()

        # register all of the app adapters
        self._adapters = {}
        self.app_manager.observe(self._on_apps_changed, names=["_temp"])

        self._generate_ui()

    def _generate_ui(self):
        self.title = widgets.Label(value="Viewer Sync Plugin")

        self.source_dropdown = widgets.Dropdown(
            options = ['', *self._adapters.keys()],
            value='',
            description='Source:',
            disabled=False
        )

        self.destination_dropdown = widgets.Dropdown(
            options = ['', *self._adapters.keys()],
            value='',
            description='Destination:',
            disabled=False
        )

        self.sync_button = widgets.Button(
            description="Sync",
            disabled=False,
            button_style='success',
            tooltip='Sync source to destination',
        )

        self.sync_button.on_click(self._sync_button_on_click)

        self.ui = widgets.VBox([
            self.title,
            widgets.HBox([
                self.source_dropdown, self.destination_dropdown, self.sync_button
            ])
        ])

    def _sync_button_on_click(self, btn):
        source = self.source_dropdown.value
        destination = self.destination_dropdown.value

        if source == destination:
            raise ValueError("Cannot sync a widget to itself.")

        if '' in [source, destination]:
            raise ValueError("Please choose a value for both source and destination.")

        self.viewer_sync_manager.start_real_time_sync(self._adapters[source], self._adapters[destination])

    def _on_apps_changed(self, change):
        self._refresh_adapters()
        self._refresh_dropdowns()

    def _refresh_adapters(self):
        for idx, app in self.app_manager.apps.items():
            if idx in self._adapters:
                pass
            for app_type, adapter_cls in ADAPTERS.items():
                if isinstance(app, app_type):
                    self._adapters[idx] = adapter_cls(app)
                    break
                else:
                    raise ValueError(f"Unsupported app type: {type(app)}")

    def _refresh_dropdowns(self):
        new_options = ['', *self._adapters.keys()]
        self.source_dropdown.options = new_options
        self.destination_dropdown.options = new_options

    def display(self):
        display(self.ui)


class ViewerSyncManager():
    def __init__(self):
        self.source = None
        self.destination = None

    def _callback(self, caller):
        self.destination.sync_to(self.source)

    def start_real_time_sync(self, source, destination):
        # ensure we stop any previously configured real time sync
        self.stop_real_time_sync()

        self.source = source
        self.destination = destination

        # call the sync method once manually to align the views
        self.destination.sync_to(self.source)

        # add a callback to the source to update the destination when the view changes
        self.source.add_callback(self._callback)

    def stop_real_time_sync(self):
        prev_source = self.source
        self.source = None
        self.destination = None

        if prev_source:
            prev_source.remove_callback(self._callback)
