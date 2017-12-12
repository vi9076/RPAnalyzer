RecoverPoint Long-Term-Stats analyzer
==========================================

Description
--------------
Script to analyze RecoverPoint long term statistics files into a multipage PDF of graphs for each metric.  There is no need to extract the .tar.gz, as the script will extract it to a temporary location for you and process all the data located within.


Requirements
--------------
numpy
pandas
matplotlib

Usage
--------------
RPAnalyzer.py <long_term_stat_file.tar.gz>

This will generate an outputfile named long_term_stat_file.pdf which includes all the charts.

