from abc import ABC, abstractmethod
from mast_aladin.adapters.aida_constants import AIDA_aspects


class ViewerSyncAdapter(ABC):
    def sync_to(self, sync_viewer, aspects):
        source_viewport = sync_viewer.aid.get_viewport(sky_or_pixel="sky")

        new_viewport = self.aid.get_viewport(sky_or_pixel="sky").copy()
        for aspect in set(aspects) & set(AIDA_aspects.get_viewport_sync_list()):
            new_viewport[aspect] = source_viewport[aspect]

        self.aid.set_viewport(**new_viewport)

    @abstractmethod
    def add_callback(self, func):
        raise NotImplementedError

    @abstractmethod
    def remove_callback(self, func):
        raise NotImplementedError

    @abstractmethod
    def show(self):
        raise NotImplementedError
