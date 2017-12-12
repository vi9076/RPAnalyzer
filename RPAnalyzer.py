import os
from os.path import isfile, join
import sys
import shutil
import logging
import tarfile
import tempfile
import numpy as np
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

logging.basicConfig(level=logging.DEBUG)


def extract_rp_data(filename, temp_path):
    """ Extract the rp data to a temporary directory,
        returning a list of the files extracted """

    # We need to extract the drive component or tarfile doesn't seem
    # to work extracting to temp directory
    drive, path = os.path.splitdrive(temp_path)

    logging.debug("Extracting TAR file to %s" % (path, ))
    tar = tarfile.open(filename, "r:gz")
    tar.extractall(path)

    # Fix the path separator
    path = path.replace(os.path.sep, '/')
    data_files = ["%s/%s" % (path, f) for f in os.listdir(path) if isfile(join(path, f))]

    for f in data_files:
        logging.debug("Found File: %s" % (f, ))

    return(data_files)


def import_data(data_files):
    """ import the data into a pandas dataframe, returning that frame """
    files_read = 1
    rp_data = None
    for statfile in data_files:
        print "Reading %d/%d - %s" % (files_read, len(data_files), statfile)
        if files_read == 1:
            rp_data = pd.read_csv(statfile, usecols=range(13),
                                  parse_dates=[0, 1])
            files_read += 1
        else:
            rp_data = rp_data.append(pd.read_csv(statfile,
                                                 usecols=range(13),
                                                 parse_dates=[0, 1]))
            files_read += 1
    return rp_data


def generate_cluster_plot(rp_data, site, statistic, pdf):
    plt.style.use('ggplot')
    plot_data = rp_data[(rp_data["site"] == site) &
                        (rp_data["peak"].isnull()) &
                        (rp_data["box"].isnull()) &
                        (rp_data["stat"] == statistic)]

    plot_data.set_index(['time from'], inplace=True)
    plot_unit = plot_data["unit"].unique()[0]

    plot_data["value"].plot(figsize=(10, 7), title="%s\n%s" % (site, statistic.strip()))
    plt.style.use('ggplot')
    plt.ylabel(plot_unit)
    plt.xlabel("Date")
    plt.ylim(ymin=0)
    pdf.savefig(orientation='landscape')
    plt.close()


def generate_rpa_plot(rp_data, site, rpa, statistic, pdf):
    plt.style.use('ggplot')
    plot_data = rp_data[(rp_data["site"] == site) &
                        (rp_data["peak"].isnull()) &
                        (rp_data["box"] == rpa) &
                        (rp_data["stat"] == statistic)]

    plot_data.set_index(['time from'], inplace=True)
    plot_unit = plot_data["unit"].unique()[0]

    plot_data["value"].plot(figsize=(10, 7), title="%s - %s\n%s" % (site, rpa, statistic.strip()))
    plt.ylabel(plot_unit)
    plt.xlabel("Date")
    plt.ylim(ymin=0)
    pdf.savefig(orientation='landscape')
    plt.close()


def generate_group_plot(rp_data, site, rpa, group, statistic, pdf):
    plt.style.use('ggplot')
    plot_data = rp_data[(rp_data["site"] == site) &
                        (rp_data["peak"].isnull()) &
                        (rp_data["box"] == rpa) &
                        (rp_data["group"] == group) &
                        (rp_data["stat"] == statistic)]

    plot_data.set_index(['time from'], inplace=True)
    plot_unit = plot_data["unit"].unique()[0]

    title = "%s - %s\nGroup: %s\n %s" % (site, rpa, group, statistic.strip())
    plot_data["value"].plot(figsize=(10, 7), title=title)
    plt.ylabel(plot_unit)
    plt.xlabel("Date")
    plt.ylim(ymin=0)
    pdf.savefig(orientation='landscape')
    plt.close()


def title_page(text, pdf):
    plt.figure()
    plt.axis('off')
    plt.text(0.5, 0.5, text, ha='center', va='center')
    pdf.savefig()
    plt.close()


def cleanup(temp_path):
    """ Delete the temporary data we created """
    shutil.rmtree(temp_path)


def main():

    temp_path = tempfile.mkdtemp()
    logging.info("Created temp path at: %s" % (temp_path,))

    if sys.argv[1]:
        filename = sys.argv[1]
        logging.info("Data filename: %s" % (filename, ))
        data_files = extract_rp_data(filename, temp_path)

        output_file = filename.replace(".tar.gz", ".pdf")
        rp_data = import_data(data_files)

        # Some basic data we'll need
        site_names = rp_data["site"].unique()
        first_data = rp_data["time from"].min()
        last_data = rp_data["time from"].max()

        with PdfPages(output_file) as pdf:

            title_page("RecoverPoint Analysis", pdf)

            for site in site_names:
                site_data = rp_data[(rp_data["site"] == site) &
                                    (rp_data["box"].isnull())]

                print site
                print "- Generating Site Statistics"
                title_page("Cluster Graphs - Site: %s" % (site,), pdf)
                for statistic in site_data["stat"].unique():
                    generate_cluster_plot(rp_data, site, statistic, pdf)

                print "- Generating RPA Statistics"
                title_page("RPA Graphs - Site: %s" % (site,), pdf)

                rpa_stats = rp_data[(rp_data["site"] == site) &
                                    (~rp_data["box"].isnull()) &
                                    (rp_data["peak"].isnull()) &
                                    (rp_data["group"].isnull())]

                for index, row in rpa_stats[["box", "stat"]].drop_duplicates().iterrows():
                    generate_rpa_plot(rp_data, site, row["box"],
                                      row["stat"], pdf)

                print "- Generating Group Statistics"
                title_page("CG Graphs - Site: %s" % (site,), pdf)

                group_stats = rp_data[(rp_data["site"] == site) &
                                      (~rp_data["group"].isnull())
                                      ]
                for index, row in group_stats[["box", "group", "stat"]].drop_duplicates().iterrows():
                    generate_group_plot(rp_data, site, row["box"],
                                        row["group"], row["stat"], pdf)

                print "Done!\n"

    if os.path.isdir(temp_path):
        logging.info("Cleaning up path at: %s" % (temp_path,))
        cleanup(temp_path)


if __name__ == "__main__":
    main()
