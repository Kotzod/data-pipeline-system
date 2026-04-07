import requests
import statistics
import sys
import json
import sqlite3

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

For this exercise, you can assume the libraries requests
and httpx are available for making HTTP requests,
in addition to the libraries included in the standard 
Python distribution. Install them – or at least one of 
them – for yourself, possibly in a virtual environment 
(pip install requests httpx). 
No other assumptions should be made about the availability
of external libraries not included in the standard Python
distribution.


Reporting AI usage:
-------------------

Report HERE whether and how you have used AI tools, and 
ones, if any. If not, write "No AI tools used". (Failure to
report AI usage will lead to an XP penalty or, in some cases, 
possibly even suspicion of academic fraud.)

No AI tools used


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
Function csv_value_count (max 2 XP)
-----------------------------------

The function uses a CSV file as its data source. The name of the file is 
provided as the parameter "file_name". It can be expected that the file 
can be found without any specific path information in the testing environment,
so the file is to be referred to by its name alone in this task.
(Run the code in the same directory where your test CSV file is located.)  
You can assume that the CSV file uses UTF8 character encoding and a comma 
as the delimiter. Also, the first row of the file being a header row 
containing the column names can and should be assumed.

The function returns the number of occurrences of the value specified by the 
parameter "search_value" in the column whose name is given by the parameter 
"column_name".

The data in the file is naturally text, but some values can be interpreted 
as integers or floating-point numbers. The code should be able to perform 
the necessary conversions based on the type of the value of search_value 
and handle potential error situations to ensure that the code works correctly.
(Hint: you can use type() to check the type of search_value.)

To test the functionality of your solution, you can use, for example, 
the file classroom_measurements.csv available in Moodle and try what your code
returns with, e.g., these calls:
csv_value_count('classroom_measurements.csv', 'id', 56269)
csv_value_count('classroom_measurements.csv', 'value', 23.5)
csv_value_count('classroom_measurements.csv', 'time', '09:11:44.407707')
However, it is advisable to test more comprehensively.
"""

def csv_value_count(file_name: str, column_name: str, search_value: any) -> int:
    count = 0
    with open(file_name, 'r', encoding='utf-8') as file:
        header = file.readline().strip().split(',')
        if column_name not in header:
            return 0
        col_index = header.index(column_name)
        for line in file:
            columns = line.strip().split(',')
            if len(columns) <= col_index:
                continue
            cell_value = columns[col_index]
            try:
                if isinstance(search_value, int):
                    cell_value = int(cell_value)
                elif isinstance(search_value, float):
                    cell_value = float(cell_value)
            except ValueError:
                continue
            if cell_value == search_value:
                count += 1
    return count



"""
Function analyze_json_from_api (max 2 XP)
-----------------------------------------

The function reads JSON content from the address 
https://www.freetogame.com/api/games (the source of the data: 
FreeToGame.com) with a normal GET request. (Hardcoding the address 
in the function is perfectly OK in this case.) 
Restrict the considerations of this task to the PC games in the 
dataset, only. (You can limit the request to PC games only 
by using query parameters – see https://www.freetogame.com/api-doc).

Based on the data received, the function answers the following
questions:
1. How many different game genres (according to exact spellings)
does the material contain? (I.e., from how many different genres
are there games in the dataset?)
2. What is the third largest game genre in the dataset 
(measured by the number of games representing it)?
3. What is the average number of games per genre in the dataset?
4. What is the median number of games per genre in the dataset?

The function returns the answers as a list in the order of the 
questions. (The zeroth element of the list is the answer to the 
first question, and so on). The answer to question 1 is an integer
(int), the answer to question 2 is a string (str), and the other 
answers are included in the list as floating-point numbers (float).
Ensure returning the list with the values of correct types.
"""

def analyze_json_from_api() -> list:
    url = "https://www.freetogame.com/api/games?platform=pc"
    response = requests.get(url)
    data = response.json()

    genre_dict = {}

    for game in data:
        genre = game.get("genre")
        if genre:
            genre_dict[genre] = genre_dict.get(genre, 0) + 1

    genre_counts = len(genre_dict)

    sorted_genres = sorted(genre_dict.items(), key=lambda x: x[1], reverse=True)
    third_largest_genre = sorted_genres[2][0] if len(sorted_genres) >= 3 else ""

    average_games_per_genre = float(sum(genre_dict.values()) / genre_counts)

    median_games_per_genre = float(statistics.median(genre_dict.values()))

    return [genre_counts, third_largest_genre, average_games_per_genre, median_games_per_genre]

"""
Function data_from_db (max 2 XP)
--------------------------------

The function reads data from a file-based SQLite database. 
The name of the database file is provided as the parameter 
'db_file'. (The database file can be assumed to be found 
without any specific path information in the testing 
environment – put the database file in the same directory 
where you run the code.) 

The database is a simple one-table database with the following
structure:
- Table name: measurements
- Columns: id (INTEGER), date (TEXT), time (TEXT), type (TEXT),
           source (TEXT), value (REAL)

In order to see example values that the table 'measurements'
could contain, consult the file 'classroom_measurements.csv'.
(Also a database file 'classroom_measurements.db' is available
in Moodle. The test database will be comparable to that – the
structure is the same, but the number of rows and the actual
values may differ. There are always at least some rows, though.)

Based on the data in the database, the function answers the 
following questions:
1. What is the minimum value of the humidity measurements
from the source 'z-02'? Answer as a float.
2. What is the average temperature? (Consider all the values
related to type 'temperature'.) Answer as a float.
3. How many rows of data are there in the table 'measurements'? 
Answer as an int.
4. How many measurements of type 'pressure' were made before 
10:43:00 (only consider the time, not the date)? Answer as an int.

The function returns the answers as a list in the order of the 
questions. (The zeroth element of the list is the answer to the 
first question, and so on). Ensure that the types of the
elements of the list are as instructed.
"""

def data_from_db(db_file: str) -> list:
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    cursor.execute('''SELECT MIN(value) FROM measurements WHERE source = 'z-02' AND type = 'humidity' ''')
    min_hum = cursor.fetchone()[0]

    cursor.execute('''SELECT AVG(value) FROM measurements WHERE type = 'temperature' ''')
    avg_temp = cursor.fetchone()[0]
    avg_temp = float(avg_temp) if avg_temp is not None else 0.0

    cursor.execute('''SELECT COUNT(*) FROM measurements ''')
    total_rows = cursor.fetchone()[0]
    total_rows = int(total_rows) if total_rows is not None else 0
    
    cursor.execute('''SELECT COUNT(*) FROM measurements WHERE type = 'pressure' AND time < '10:43:00' ''')
    pressure_count = cursor.fetchone()[0]
    pressure_count = int(pressure_count) if pressure_count is not None else 0

    conn.close()

    return [float(min_hum), float(avg_temp), int(total_rows), int(pressure_count)]

