ISI
========

ISI processes data for a research project assessing the effects of enzymatic injection on ligament elongation. "20221209 Data" contains 3D position data of markers adhered to the transverse carpal ligament of a cadaveric hand. This project calculates mean percent elongation for injection and control groups depending on pressure level and location (distal, middle, proximal). 

Features
--------

- Multi-indexing using Pandas dataframes
- Basic math calculations and statistical tests, such as 2-way ANOVA and Tukey's Test

Dependencies
--------

The Pandas library is required for the programs to work
- http://pandas.org/releases.html

Usage
--------

main.py calculates the mean and standard deviation for percent elongation of each group and outputs the results as an Excel spreadsheet. calc_stats.py compares groups by 2-way ANOVA and Tukey's Test.