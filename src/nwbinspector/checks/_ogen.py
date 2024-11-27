from typing import Optional

from pynwb.ogen import OptogeneticSeries, OptogeneticStimulusSite

from .._registration import Importance, InspectorMessage, register_check


@register_check(importance=Importance.BEST_PRACTICE_VIOLATION, neurodata_type=OptogeneticStimulusSite)
def check_optogenetic_stimulus_site_has_optogenetic_series(
    ogen_site: OptogeneticStimulusSite,
) -> Optional[InspectorMessage]:
    """Check if an optogenetic stimulus site has an optogenetic series linked to it."""
    nwbfile = ogen_site.get_ancestor("NWBFile")
    for obj in nwbfile.objects.values():
        if isinstance(obj, OptogeneticSeries):
            if obj.site == ogen_site:
                return None

    return InspectorMessage(message="OptogeneticStimulusSite is not referenced by any OptogeneticSeries.")
