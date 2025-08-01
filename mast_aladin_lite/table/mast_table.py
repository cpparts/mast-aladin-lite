
import os
import json
import warnings
from collections import defaultdict

from traitlets import List, Unicode, Bool, Int, Any, observe
from ipypopout import PopoutButton
from ipyvuetify import VuetifyTemplate
from ipywidgets.widgets import widget_serialization

import numpy as np
import astropy.units as u
from astropy.coordinates import SkyCoord


# locations for metadata from MissionMAST:
missions = ['jwst', 'roman', 'hst']
table_data_dir = os.path.join(os.path.dirname(__file__), 'data')
unique_column_path = os.path.join(table_data_dir, 'unique_columns_per_mission.json')
column_descriptions_path = os.path.join(table_data_dir, 'column_descriptions.json')

# register loaded table widgets as they're initialized
_table_widgets = dict()


def serialize(table):
    """
    Convert an astropy table to a list of dictionaries
    containing each column as a list of pure Python objects.
    """
    return [
        {
            k: v.tolist()
            for k, v in dict(row).items()
        } for row in table
    ]


known_unique_mast_table_cols = [
    'fileSetName',  # data products from Missions Mast
    'source_id',    # Gaia
    'MatchID',      # Hubble Source Catalog
    'objID',        # PanSTARRS,
]


class MastTable(VuetifyTemplate):
    """
    Table widget for observation queries from Mission MAST.
    """
    template_file = __file__, "mast_table.vue"

    items = List().tag(sync=True)
    headers_visible = List().tag(sync=True)
    headers_avail = List().tag(sync=True)
    show_if_empty = Bool(True).tag(sync=True)
    show_rowselect = Bool(True).tag(sync=True)
    selected_rows = List().tag(sync=True)
    column_descriptions = List().tag(sync=True)
    multiselect = Bool(True).tag(sync=True)
    items_per_page = Int(5).tag(sync=True)
    show_tooltips = Bool(False).tag(sync=True)
    menu_open = Bool(False).tag(sync=True)
    clear_btn_lbl = Unicode('Clear Table').tag(sync=True)
    popout_button = Any().tag(sync=True, **widget_serialization)

    # item_key is a column of the table with unique values
    # for each row, enabling selection of the row by lookup
    item_key = Unicode().tag(sync=True)

    table = None
    row_select_callbacks = []

    def __init__(self, table, app=None, update_viewport=True, unique_column=None, **kwargs):
        """
        Parameters
        ----------
        table : `~astropy.table.Table`
            A table to load.

        app : `~mast_aladin_lite.app.MastAladin`
            An instance of the ``MastAladin`` app.

        update_viewport : bool (optional, default is `True`)
            If `True`, set the `~mast_aladin_lite.app.MastAladin`
            viewport center to the position of the item in the
            first row of the table on load.

        unique_column : str (optional, default is `None`)
            A column which contains unique values in each row.

            If no `unique_column` is given, ``MastTable`` will look for a
            column known to have unique values for each row in common MAST
            observation queries. If no known `unique_column` is found,
            search through the table to find a column with unique rows.

            For tables with many rows, unique column searches are inefficient
            and a warning will be raised..
        """

        super().__init__(**kwargs)
        self.popout_button = PopoutButton(self)

        self.table = table
        self.app = app

        self.items = serialize(table)
        mission = detect_mission(table)
        columns = table.colnames
        self.column_descriptions = get_column_descriptions(mission)

        self._set_item_key(columns, unique_column)

        self.headers_avail = list(columns)

        # by default, remove the `s_region`` column
        # from the visible columns in the widget:
        if 's_region' in columns:
            columns.remove('s_region')

        self.headers_visible = columns

        _table_widgets[len(_table_widgets)] = self

        if update_viewport and self.app is not None:
            ra_column, dec_column = 'ra', 'dec'

            if ra_column not in table.colnames:
                ra_column, dec_column = 'targ_ra', 'targ_dec'

            center_coord = SkyCoord(
                ra=table[ra_column][0] * u.deg,
                dec=table[dec_column][0] * u.deg,
                unit=u.deg
            )

            # change the coordinate frame to match the coordinates in the MAST table:
            self.app.target = f"{center_coord.ra.degree} {center_coord.dec.degree}"

    def _set_item_key(self, table_columns, item_key, n_rows_slow=10e6):
        """
        `item_key` should be set to the name of a table column that contains
        unique values in each row, which can be used for selection.

        If no `unique_column` is given at construction, look for a column known to have
        unique values for each row in MAST catalog and observation queries. If no known
        columns are found, search through the table to find a column with unique rows.

        Unique row searches are inefficient for tables with more than `n_rows_slow` rows,
        and a warning will be raised. The default `n_rows_slow = 10e6` takes about 100
        milliseconds per table column.
        """
        if item_key is None:
            # check for known unique columns:
            for column in known_unique_mast_table_cols:
                if column in table_columns:
                    self.item_key = column
                    break

            # warn the user if unique row search will be inefficient:
            if len(self.table) > n_rows_slow:
                warnings.warn(
                    "No `unique_column` was given, so all columns will be checked "
                    f"for unique entries. This table has {len(self.table)} rows, so "
                    "the search for unique rows may be slow. To avoid this in the future,"
                    "use the `unique_column` keyword argument when calling "
                    "`MastAladin.load_table`.", UserWarning
                )

            # search for columns with unique rows:
            for column in table_columns:
                n_unique_values = np.unique(self.table[column]).size
                if n_unique_values == len(self.table):
                    self.item_key = column
                    break
            else:
                raise ValueError(
                    "No `unique_column` specified, and no unique columns were found."
                )

        elif item_key in table_columns:
            self.item_key = item_key

        else:
            raise ValueError(
                f"item_key '{item_key}' not found in table columns: {table_columns}"
            )

    @observe('selected_rows')
    def _on_row_selection(self, msg={}):
        for func in self.row_select_callbacks:
            func(msg)


def get_current_table():
    """
    Return the last instantiated table widget.
    """
    latest_table_index = list(_table_widgets.keys())[-1]
    return _table_widgets[latest_table_index]


def update_mast_column_lists(update_column_descriptions=True, update_unique_columns=True):
    """
    Return a dictionary of columns in observation query
    results from astroqery.mast.missions.MastMissions
    that are unique to each mission.
    """
    from astroquery.mast.missions import MastMissions

    mast = MastMissions()

    columns_available = dict()
    unique_columns = dict()
    column_descriptions = defaultdict(list)

    for mission in missions:
        mast.mission = mission
        column_list = mast.get_column_list()

        for row in column_list.iterrows():
            column_descriptions[mission].append(
                {k: str(v).strip() for k, v in zip(column_list.colnames, row)}
            )

        column_names = column_list['name'].tolist()
        columns_available[mission] = set(column_names)

    if update_column_descriptions:
        json_file = open(column_descriptions_path, 'w')
        json.dump(column_descriptions, json_file)

    for mission in missions:
        mast.mission = mission
        column_names = mast.get_column_list()['name']

        other_missions = list(missions)
        other_missions.remove(mission)
        other_mission_columns = columns_available[other_missions[0]].union(
            columns_available[other_missions[1]]
        )
        unique_columns[mission] = list(
            columns_available[mission].difference(
                other_mission_columns
            )
        )

    if update_unique_columns:
        json_file = open(unique_column_path, 'w')
        json.dump(unique_columns, json_file, indent=4)

    return unique_columns


def detect_mission(table):
    """
    Detect which mission was queried by the results from an astroquery.mast.missions
    query by looking for unique columns in the `astropy.table.Table`.
    """
    unique_columns = json.load(open(unique_column_path, 'r'))
    columns = table.colnames

    for mission in missions:
        if any(name in unique_columns[mission] for name in columns):
            return mission


def get_column_descriptions(mission):
    column_descriptions = json.load(open(column_descriptions_path, 'r'))
    return column_descriptions[mission]
