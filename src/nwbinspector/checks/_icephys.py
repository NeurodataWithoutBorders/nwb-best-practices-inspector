"""Checks specific to intracellular electrophysiology neurodata types."""

from typing import Optional

from pynwb.icephys import IntracellularElectrode

from .._registration import Importance, InspectorMessage, register_check


@register_check(importance=Importance.BEST_PRACTICE_VIOLATION, neurodata_type=IntracellularElectrode)
def check_intracellular_electrode_cell_id_exists(
    intracellular_electrode: IntracellularElectrode,
) -> Optional[InspectorMessage]:
    """
    Check if the IntracellularElectrode contains a cell_id.

    Best Practice: TODO
    """
    if hasattr(intracellular_electrode, "cell_id") and intracellular_electrode.cell_id is None:
        return InspectorMessage(message="Please include a unique cell_id associated with this IntracellularElectrode.")

    return None
