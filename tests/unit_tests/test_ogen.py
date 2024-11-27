from datetime import datetime
from unittest import TestCase

from pynwb.device import Device
from pynwb.file import NWBFile
from pynwb.ogen import OptogeneticSeries

from nwbinspector.checks import check_optogenetic_stimulus_site_has_optogenetic_series


class TestCheckOptogeneticStimulusSiteHasOptogeneticSeries(TestCase):
    def setUp(self) -> None:
        self.nwbfile = NWBFile(
            session_description="session_description", identifier="identifier", session_start_time=datetime.now()
        )

        device = Device(name="device_name")
        self.ogen_site = self.nwbfile.create_ogen_site(
            name="ogen_stim_site_name",
            device=device,
            description="description",
            excitation_lambda=550.0,
            location="location",
        )

    def test_check_pass(self):
        ogen_series = OptogeneticSeries(
            name="ogen_series_name",
            data=[1.0, 2.0, 3.0],
            site=self.ogen_site,
            rate=30.0,
        )

        ogen_module = self.nwbfile.create_processing_module("ogen", "ogen")
        ogen_module.add(ogen_series)

        assert check_optogenetic_stimulus_site_has_optogenetic_series(self.ogen_site) is None

    def test_check_triggered(self):
        assert (
            check_optogenetic_stimulus_site_has_optogenetic_series(self.ogen_site).message
            == "OptogeneticStimulusSite is not referenced by any OptogeneticSeries."
        )
