from pynwb.device import Device
from pynwb.icephys import IntracellularElectrode

from nwbinspector import Importance, InspectorMessage
from nwbinspector.checks import check_intracellular_electrode_cell_id_exists


def test_pass_check_intracellular_electrode_cell_id_exists():
    device = Device(name="device")
    ielec = IntracellularElectrode(name="ielec", cell_id="123", device=device, description="an intracellular electrode")
    assert check_intracellular_electrode_cell_id_exists(ielec) is None


def test_fail_check_intracellular_electrode_cell_id_exists():
    device = Device(name="device")
    ielec = IntracellularElectrode(name="ielec", device=device, description="an intracellular electrode")
    assert check_intracellular_electrode_cell_id_exists(ielec) == InspectorMessage(
        message="Please include a unique cell_id associated with this IntracellularElectrode.",
        importance=Importance.BEST_PRACTICE_VIOLATION,
        check_function_name="check_intracellular_electrode_cell_id_exists",
        object_type="IntracellularElectrode",
        object_name="ielec",
        location="/",
    )
