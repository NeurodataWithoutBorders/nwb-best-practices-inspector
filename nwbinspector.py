import sys
from pathlib import Path
import pynwb
import numpy as np
import hdmf
import hdmf.backends.hdf5.h5_utils


def main():

    in_path = sys.argv[1]
    in_path = Path(in_path)
    if in_path.is_dir():
        files = list(in_path.glob('*.nwb'))
    elif in_path.is_file():
        files = [in_path]
    else:
        raise Exception('%s should be a directory or an NWB file' % in_path)

    num_exceptions = 0
    for fi, filename in enumerate(files):
        print('%d/%d %s' % (fi + 1, len(files), filename))

        try:
            with pynwb.NWBHDF5IO(str(filename), 'r', load_namespaces=True) as io:
                errors = pynwb.validate(io)
                if errors:
                    for e in errors:
                        print('Validator Error:', e)
                    num_exceptions += 1
                else:
                    print('Validation OK!')

                # inspect NWBFile object
                nwbfile = io.read()
                check_general(nwbfile)
                check_timeseries(nwbfile)
                check_tables(nwbfile)
                check_icephys(nwbfile)
                check_opto(nwbfile)
                check_ecephys(nwbfile)

        except Exception as ex:
            num_exceptions += 1
            print(ex)
        print()

    if num_exceptions:
        print('%d/%d files had errors.' % (num_exceptions, len(files)))
    else:
        print('All %d files validate!' % len(files))


def check_general(nwbfile):
    if not nwbfile.experimenter:
        error_code = 'A101'
        print("%s: /general/experimenter is missing" % error_code)
    if not nwbfile.experiment_description:
        error_code = 'A101'
        print("%s: /general/experiment_description is missing" % error_code)
    if not nwbfile.institution:
        error_code = 'A101'
        print("%s: /general/institution is missing" % error_code)
    if not nwbfile.keywords:
        error_code = 'A101'
        print("%s: /general/keywords is missing" % error_code)
    if nwbfile.related_publications is not None:
        for pub in nwbfile.related_publications:
            # TODO use regex matching, maybe even do doi lookup
            if not (pub.startswith('doi:')
                    or pub.startswith('http://dx.doi.org/')
                    or pub.startswith('https://doi.org/')):
                error_code = 'A101'
                print("%s: /general/related_publications does not include 'doi': %s" % (error_code, pub))
    if nwbfile.subject:
        if not nwbfile.subject.sex:
            error_code = 'A101'
            print("%s: /general/subject/sex is missing" % error_code)
        if not nwbfile.subject.subject_id:
            error_code = 'A101'
            print("%s: /general/subject/subject_id is missing" % error_code)
        if not nwbfile.subject.species:
            error_code = 'A101'
            print("%s: /general/subject/species is missing" % error_code)
    else:
        error_code = 'A101'
        print("%s: /general/subject is missing" % error_code)


def check_timeseries(nwbfile):
    """Check dataset values in TimeSeries objects"""
    for ts in all_of_type(nwbfile, pynwb.TimeSeries):
        if ts.data is None:
            error_code = 'A101'
            print("%s: '%s' %s data is None" % (error_code, ts.name, type(ts).__name__))
            continue

        uniq = np.unique(ts.data)
        if len(uniq) == 1:
            error_code = 'A101'
            print("%s: '%s' %s data has all values = %s" % (error_code, ts.name, type(ts).__name__, uniq[0]))
        elif np.array_equal(uniq, [0., 1.]):
            if ts.data.dtype != bool:
                error_code = 'A101'
                print("%s: '%s' %s data should be type boolean instead of %s"
                      % (error_code, ts.name, type(ts).__name__, ts.data.dtype))
        elif len(uniq) == 2:
            error_code = 'A101'
            print("%s: '%s' %s data has only unique values %s. Consider storing the data as boolean."
                  % (error_code, ts.name, type(ts).__name__, uniq))
        elif len(uniq) <= 4:
            print("NOTE: '%s' %s data has only unique values %s" % (ts.name, type(ts).__name__, uniq))

        # check whether rate should be used instead of timestamps
        if ts.timestamps:
            time_tol_decimals = 9
            uniq_diff_ts = np.unique(np.diff(ts.timestamps).round(decimals=time_tol_decimals))
            if len(uniq_diff_ts) == 1:
                error_code = 'A101'
                print("%s: '%s' %s timestamps should use starting_time %f and rate %f"
                      % (error_code, ts.name, type(ts).__name__, ts.timestamps[0], uniq_diff_ts[0]))

        if ts.resolution == 0 or (ts.resolution < 0 and ts.resolution != -1.0):
            error_code = 'A101'
            print("%s: '%s' %s data attribute 'resolution' should use -1.0 or NaN for unknown instead of %f"
                  % (error_code, ts.name, type(ts).__name__, ts.resolution))

        if not ts.unit:
            error_code = 'A101'
            print("%s: '%s' %s data is missing text for attribute 'unit'" % (error_code, ts.name, type(ts).__name__))


def check_tables(nwbfile):
    """Check column values in DynamicTable objects"""
    for tab in all_of_type(nwbfile, pynwb.core.DynamicTable):
        for col in tab.columns:
            if isinstance(col, hdmf.common.table.DynamicTableRegion):
                continue

            if col.data is None:
                error_code = 'A101'
                print("%s: '%s' %s column '%s' data is None" % (error_code, tab.name, type(tab).__name__, col.name))
                continue

            if col.name.endswith('index'):  # skip index columns
                continue

            if isinstance(col.data, hdmf.backends.hdf5.h5_utils.DatasetOfReferences):  # TODO find a better way?
                continue

            uniq = np.unique(col.data)
            # TODO only do this for optional columns
            if len(uniq) == 1:
                error_code = 'A101'
                print("%s: '%s' %s column '%s' data has all values = %s"
                      % (error_code, tab.name, type(tab).__name__, col.name, uniq[0]))
            elif np.array_equal(uniq, [0., 1.]):
                if col.data.dtype.type != np.bool_:
                    error_code = 'A101'
                    print("%s: '%s' %s column '%s' data should be type boolean instead of %s"
                          % (error_code, tab.name, type(tab).__name__, col.name, col.data.dtype))
            elif len(uniq) == 2:
                error_code = 'A101'
                print(("%s: '%s' %s column '%s' data has only unique values %s. Consider storing the data "
                      "as boolean.") % (error_code, tab.name, type(tab).__name__, col.name, uniq))
            elif len(uniq) <= 4:
                print("NOTE: '%s' %s column '%s' data has only unique values %s"
                      % (tab.name, type(tab).__name__, col.name, uniq))


def check_icephys(nwbfile):
    for elec in all_of_type(nwbfile, pynwb.icephys.IntracellularElectrode):
        if not elec.description:
            error_code = 'A101'
            print("%s: '%s' %s is missing text for attribute 'description'"
                  % (error_code, elec.name, type(elec).__name__))
        if not elec.filtering:
            error_code = 'A101'
            print("%s: '%s' %s is missing text for attribute 'filtering'"
                  % (error_code, elec.name, type(elec).__name__))
        if not elec.location:
            error_code = 'A101'
            print("%s: '%s' %s is missing text for attribute 'location'"
                  % (error_code, elec.name, type(elec).__name__))


def check_opto(nwbfile):
    opto_sites = list(all_of_type(nwbfile, pynwb.ogen.OptogeneticStimulusSite))
    opto_series = list(all_of_type(nwbfile, pynwb.ogen.OptogeneticSeries))
    for site in opto_sites:
        if not site.description:
            error_code = 'A101'
            print("%s: '%s' %s is missing text for attribute 'description'"
                  % (error_code, site.name, type(site).__name__))
        if not site.location:
            error_code = 'A101'
            print("%s: '%s' %s is missing text for attribute 'location'"
                  % (error_code, site.name, type(site).__name__))
    if opto_sites and not opto_series:
        error_code = 'A101'
        print("%s: OptogeneticStimulusSite object(s) exists without an OptogeneticSeries" % error_code)


def check_ecephys(nwbfile):
    if nwbfile.units is not None:
        if nwbfile.units.get_min_spike_time() < 0:
            error_code = 'A101'
            print("%s: the units table contains negative spike times." % error_code)


def all_of_type(nwbfile, type):
    for obj in nwbfile.objects.values():
        if isinstance(obj, type):
            yield obj


if __name__ == '__main__':
    """
    Usage: python nwbinspect.py dir_name
    """
    main(sys.argv[1])
