import pandas as pd
"""
GENERAL INSTRUCTIONS
--------------------


The idea shortly:
-----------------

Complete the bodies of the functions of this file
so that they behave as described and submit this code
file (retaining its original name) as your solution to
the respective assignment submission area in Moodle.


Use of external libraries:
--------------------------

For this exercise, you can assume the pandas library is
available for data manipulation.
Install it for yourself, possibly in a virtual environment
(pip install pandas). No other assumptions should be made
about the availability of external libraries not included
in the standard Python distribution.


Reporting AI usage:
-------------------

Report HERE whether and how you have used AI tools, and which
ones, if any. If you have not used AI tools, write
"No AI tools used". (Failure to report AI usage will lead
to an XP penalty or, in some cases, possibly even suspicion
of academic fraud.)

No AI tools used.


Further requirements, instructions, and info in more detail:
------------------------------------------------------------

- Test code will import and call your functions (expecting that
  the names and parameters are exactly as defined).
  Therefore:
  * Do not change the names of the functions or their parameters.
  * Do not add parameters or alter the parameterization in any way.
  * Make sure that the functions return the correct values.
  * Do not call the functions automatically within this code file.
    (It is unnecessary and may lead to unwanted output.)
    Naturally, you probably want to test your functions by calling
    them yourself while developing your solution, but make sure to
    remove such test calls before submitting your solution!

- Also, do not rename the code file. (The test code and possibly other
  scripts expect the file to have its original name.)

- Moreover, do not hardcode any solutions – the code should produce
the correct results for all valid inputs.

- The submitted code must not produce any output (prints) when
imported or when the functions are called, unless the function
description specifically requires printing as part of the
functionality.

- If you need/want, you may define and use additional helper
functions within this code file, if your solution uses them.
However, only the functions defined below will be tested
and graded. If they call any helper functions you have defined,
these helper functions must be defined within this same
code file, and the rule of not producing any extra output
applies to them as well. That is, they must not print anything
either, except for the possible prints required by the instructions.
"""
###################################


"""
Function merge_stuff (max 2 XP)
-------------------------------

The function...

¤ reads the data from the CSV files pointed out by the
file names/paths given as the parameters data1_csv and
data2_csv*, into pandas data frames (one DataFrame for
each file),

¤ creates a new data frame that combines data from the original
data frames based on the values in the time and location columns,
so that rows with matching values in these columns are considered
to correspond to each other for the other columns as well**,

¤ sorts the data so that the primary sorting criterion is the
value of the temperature_C column and the secondary criterion
is the value of the air_pressure_hPa column (in ascending order),
and the order of the columns from left to right is time, location,
CO2_ppm, temperature_C, air_pressure_hPa, and humidity_rel_perc,

¤ removes all the data rows missing a value for humidity_rel_perc,

¤ writes the resulting data to a CSV file named output.csv,
including the column header, in the same directory, and

¤ returns the arithmetic mean of the CO2_ppm values for the
result data.

The file output.csv should not contain any columns other than
those listed. (For example, there should not be a row index
column created by pandas.)

*) When coding, you can use the files data1.csv and data2.csv
found on Moodle. These files illustrate the structure of the
actual files to be used for testing.

**) In the new data frame, the number of data rows does not
increase, but it will have more columns than either of the
original data frames. There should, however, be only one time
column and one location column in the combined structure;
duplicate columns are not allowed.
"""

def merge_stuff(data1_csv: str, data2_csv: str) -> float:
    df1 = pd.read_csv(data1_csv)
    df2 = pd.read_csv(data2_csv)

    combined_df = pd.merge(df1, df2, on=["time", "location"], how="inner")

    columns_order = [
        "time",
        "location",
        "CO2_ppm",
        "temperature_C",
        "air_pressure_hPa",
        "humidity_rel_perc"
    ]

    combined_df = combined_df[columns_order]

    combined_df = combined_df.dropna(subset=["humidity_rel_perc"])

    combined_df = combined_df.sort_values(
        by=["temperature_C", "air_pressure_hPa"],
        ascending=[True, True]
    )

    combined_df.to_csv("output.csv", index=False)

    return combined_df["CO2_ppm"].mean()
