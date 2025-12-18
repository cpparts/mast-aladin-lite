from traitlets import HasTraits, Dict, observe, Int


class AppManager(HasTraits):
    _apps = Dict(default_value={}).tag(sync=True)
    _temp = Int().tag(sync=True)

    def __init__(self):
        pass

    @property
    def apps(self):
        return self._apps

    def register_app(self, app, idx):
        if idx in self._apps:
            raise ValueError(f"id: {idx} already registered to an application. Please use a different, unique, identifier")

        self._apps[idx] = app
        self._temp = len(self._apps)
    