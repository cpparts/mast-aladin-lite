import ipywidgets as widgets
from IPython.display import display
from mast_aladin.aida import AIDA_aspects
from .viewer_sync_adapters import get_adapter, JdavizSyncAdapter


class ViewerSyncPlugin():
    def __init__(self, app_manager):
        self.app_manager = app_manager

        # register plugin to update adapters as registered apps change
        self._adapters = {}
        self.app_manager.observe(self._on_apps_changed, names=["_apps_changed"])

        self.sync_manager = ViewerSyncManager()
        self.aspects = self.sync_manager.aspects
        self._pause_updates = False

        self.source_dropdown = widgets.Dropdown(
            options=['', *self._adapters.keys()],
            value='',
            description='Source:',
            disabled=False
        )

        self.destination_dropdown = widgets.Dropdown(
            options=['', *self._adapters.keys()],
            value='',
            description='Destination:',
            disabled=False
        )

        self.sync_button = widgets.Button(
            description='Sync',
            disabled=False,
            button_style='success',
            tooltip='Sync source to destination',
        )

        self.clear_button = widgets.Button(
            description='Clear',
            disabled=False,
            button_style='success',
            tooltip='Clear sync',
        )

        self.sync_button.on_click(self._sync_button_on_click)
        self.clear_button.on_click(self._clear_button_on_click)
        self.source_dropdown.observe(self._on_source_destination_change, names="value")
        self.destination_dropdown.observe(self._on_source_destination_change, names="value")

        common_togglebutton_args = {
            "value": True,
            "disabled": False,
            "button_style": "",
            "layout": widgets.Layout(width="24%")
        }

        for aspect in self.aspects:
            _attr = f"{aspect}_button"
            _togglebutton_args = {"description": aspect, "tooltip": f"Sync {aspect}"}
            setattr(
                self,
                _attr,
                widgets.ToggleButton(**common_togglebutton_args, **_togglebutton_args)
            )
            getattr(self, _attr).observe(self._sync_button_on_click, names="value")

    @property
    def ui(self):
        header_style = (
            "font-size: 12px; "
            "font-weight: 600; "
        )

        viewer_source_label = widgets.HTML(
            f"<div style='{header_style}'>Source Widget</div>"
        )

        viewer_dest_label = widgets.HTML(
            f"<div style='{header_style}'>Destination Widget</div>"
        )

        sync_properties_label = widgets.HTML(
            f"<div style='{header_style}'>Properties</div>"
        )

        properties_row_1 = widgets.HBox([
            self.center_button,
            self.fov_button
        ], layout=widgets.Layout(width="100%", gap="12px", margin="0"))

        properties_row_2 = widgets.HBox([
            self.rotation_button,
            self.projection_button
        ], layout=widgets.Layout(width="100%", gap="12px", margin="0"))

        contents = [
            viewer_source_label,
            self.source_dropdown,
            viewer_dest_label,
            self.destination_dropdown,
            sync_properties_label,
            properties_row_1,
            properties_row_2,
            self.sync_button,
            self.clear_button,
        ]
        container = widgets.VBox(
            contents,
            layout=widgets.Layout(
                width="100%",
                padding="20px",
            )
        )

        return container

    def _sync_button_on_click(self, btn):
        if self._pause_updates:
            return

        source = self.source_dropdown.value
        destination = self.destination_dropdown.value

        if source == destination:
            raise ValueError("Cannot sync a widget to itself.")

        if '' in [source, destination]:
            raise ValueError("Please choose a value for both source and destination.")

        source_adapter = self._adapters[source]
        dest_adapter = self._adapters[destination]

        self._update_projection_button_state()

        aspects = self._get_active_aspects()
        self.sync_manager.start_real_time_sync(
            source=source_adapter,
            destination=dest_adapter,
            aspects=aspects
        )

    def _clear_button_on_click(self, btn):
        self.sync_manager.stop_real_time_sync()

    def _get_active_aspects(self):
        return [
            aspect for aspect in self.aspects
            if getattr(
                getattr(self, f"{aspect}_button", None),
                "value",
                False
            )
        ]

    def _on_apps_changed(self, change):
        self._refresh_adapters()
        self._refresh_dropdowns()
        self._update_projection_button_state()

    def _on_source_destination_change(self, change):
        self._update_projection_button_state()

    def _update_projection_button_state(self):
        """
        TODO: Remove this method once projection is supported by jdaviz
        https://github.com/spacetelescope/jdaviz/pull/4076
        """
        source_adapter = self._adapters.get(self.source_dropdown.value)
        destination_adapter = self._adapters.get(self.destination_dropdown.value)

        disable_projection = any([
            isinstance(source_adapter, JdavizSyncAdapter),
            isinstance(destination_adapter, JdavizSyncAdapter)
        ])

        self.projection_button.disabled = disable_projection
        if disable_projection and self.projection_button.value:
            try:
                # updating projection causes a callback to be triggered to the
                # _sync_button_on_click method which can cause and error if source
                # and destination are not set, so we pause updates while we update
                # the projection button value.
                self._pause_updates = True
                self.projection_button.value = False
            finally:
                self._pause_updates = False

    def _refresh_dropdowns(self):
        new_options = ['', *self._adapters.keys()]
        self.source_dropdown.options = new_options
        self.destination_dropdown.options = new_options

    def _refresh_adapters(self):
        for idx, app in self.app_manager.apps.items():
            if idx in self._adapters:
                pass

            adapter = get_adapter(app)
            if adapter is None:
                pass

            self._adapters[idx] = adapter(app)

    def display(self):
        display(self.ui)


class ViewerSyncManager():
    def __init__(self):
        self.source = None
        self.destination = None
        self.aspects = (
            AIDA_aspects.CENTER,
            AIDA_aspects.FOV,
            AIDA_aspects.ROTATION,
            AIDA_aspects.PROJECTION
        )

    def _callback(self, caller):
        self.destination.sync_to(self.source, self.aspects)

    def start_real_time_sync(self, source, destination, aspects):
        # ensure we stop any previously configured real time sync
        self.stop_real_time_sync()

        self.source = source
        self.destination = destination
        self.aspects = aspects

        # call the sync method once manually to align the views
        self.destination.sync_to(self.source, self.aspects)

        # add a callback to the source to update the destination when the view changes
        self.source.add_callback(self._callback)

    def stop_real_time_sync(self):
        prev_source = self.source
        self.source = None
        self.destination = None
        self.aspects = []

        if prev_source:
            prev_source.remove_callback(self._callback)
