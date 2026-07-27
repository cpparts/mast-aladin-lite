from abc import ABC, abstractmethod
from mast_aladin.aida import AIDA_aspects


class ViewerSyncAdapter(ABC):
    def sync_to(self, sync_viewer, aspects):
        source_viewer = sync_viewer.viewer

        # TODO (2026-07-22): the jdaviz glue viewer attribute `aid`
        # will be removed in a PR coming soon, the line below will
        # need to be updated.
        if hasattr(source_viewer, '_obj'):
            source_viewer = source_viewer._obj.glue_viewer.aid

        source_viewport = source_viewer.get_viewport(sky_or_pixel="sky")

        new_viewport = source_viewer.get_viewport(sky_or_pixel="sky").copy()
        for aspect in set(aspects) & {*AIDA_aspects}:
            new_viewport[aspect] = source_viewport[aspect]

        # TODO (2026-07-22): the jdaviz glue viewer attribute `aid`
        # will be removed in a PR coming soon, the line below will
        # need to be updated.
        if hasattr(self.viewer, '_obj'):
            self.viewer._obj.glue_viewer.aid.set_viewport(**new_viewport)
        else:
            self.viewer.set_viewport(**new_viewport)

    @abstractmethod
    def add_callback(self, func):
        raise NotImplementedError

    @abstractmethod
    def remove_callback(self, func):
        raise NotImplementedError

    @abstractmethod
    def show(self):
        raise NotImplementedError
