ISI
========

ISI processes data for a research project assessing the effects of enzymatic injection on ligament elongation. This project calculates percent elongation for injection and control groups depending on pressure level (10-210mmHg) and location (distal, middle, proximal), and performs statistical analyses. 

Features
--------

- Multi-indexing using Pandas dataframes
- Basic math calculations and statistical tests, such as 2-way ANOVA and Tukey's Test

Dependencies
--------

- Pandas
- NumPy

Usage
--------

main.py calculates the mean and standard deviation for percent elongation of each group and outputs the results as an Excel spreadsheet. calc_stats.py compares groups by 2-way ANOVA and Tukey's Test. "20221209 Data" contains 3D position data of markers adhered to the transverse carpal ligament of a cadaveric hand, and was collected using a Vicon motion capture system. 