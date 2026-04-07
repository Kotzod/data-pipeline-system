"""
Complete the bodies of the functions of this file 
so that the functions behave as described.

If yo need/want, you are free to import libraries included 
in the standard Python distribution, but do not use any 
third party libraries (or such) that may not be present 
in the environment in which your work is going to be tested.

Submit this code file (with its original name) as your solution
in Moodle.

N.B.
----
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
Function encode
---------------
Returns the string obtained by encoding the plaintext received as
the 'text' parameter as follows. 

Step 1) (max 1 XP): The value of the str parameter 'alphabet', 
consisting of ASCII characters, is used as the alphabet. 
Each letter of the plaintext is replaced by the character 
found by moving forward in the alphabet by the number of characters 
given by the integer parameter 'shift'.
(Naturally, if the shift (the value of the 'shift' parameter) is
negative, the movement is backwards in the alphabet (i.e., to the
left / from the end towards the beginning) by the absolute value
of the shift.) The alphabet is interpreted as circular, so that 
the character following the last character of the alphabet is 
considered to be the first character, and similarly, the last
character is considered to precede the first character. If the
boolean parameter 'simple' is True, the encoded string produced
by Step 1 is returned. Otherwise, proceed to Step 2.

Step 2) (max 1 XP, requires that Step 1 is implemented and OK):
The encoded text obtained in Step 1 is further scrambled by starting
from the beginning of the string, dividing it into distinct 
substrings of length defined by the integer parameter 'revlen', and
reversing each of these substrings. (That is, the order of the 
characters is reversed separately for each of these substring while 
maintaining their original mutual order.) It can be assumed that the 
value of the parameter 'revlen' is a natural number not larger than 
the length of the string to be scrambled. If the length of the string
to be scrambled is not divisible by the value of the parameter 
'revlen' and thus there are leftover characters at the end of the
string, these characters are retained as they are (without reversing 
them).
(For example, if the Step 2 functionality processes the string 
'ABCDEFGH' with the revlen value 3, the resulting string should be 
'CBAFEDGH'.)
The resulting string obtained by rearranging the character order 
as described is returned by the function.
"""

def encode(text, alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 ',
           shift=0, revlen=3, simple=False):
    step1_text = ''
    n = len(alphabet)

    for letter in text:
        idx = alphabet.find(letter)
        if idx == -1:
            step1_text += letter
        else:
            new_idx = (idx + shift) % n
            step1_text += alphabet[new_idx]

    if simple:
        return step1_text

    step2_text = ''
    i = 0
    while i + revlen <= len(step1_text):
        step2_text += step1_text[i:i + revlen][::-1]
        i += revlen
    step2_text += step1_text[i:]
    return step2_text

"""
Function neighbor_count_map
(max 2 XP)
--------------------------
The function takes, as a parameter, a list of tuples in 
(x, y) format. Each tuple represents the coordinates of 
an object in a world that can be represented as a map of 
19 * 9 characters. After reading the locations, the function 
prints a representation of the situation (the map) with 
ASCII characters. 

On the map, a tilde (~) represents an 
empty area where no objects are known to exist, and each 
object is marked with a number from 0 to 8 corresponding 
to the number of its neighboring objects. (Diagonal neighbors 
are also counted as neighbors.) The coordinate (0, 0) is in 
the top-left corner of the map, and the coordinate (18, 8) 
is in the bottom-right corner, meaning y-coordinates increase 
downwards and x-coordinates increase to the right.

Even if an object is pointed to the same place multiple times,
repetition does not alter the behavior – only one object can 
fit in one place that corresponds to one character on the map.
However, the program must not crash or malfunction if duplicate
coordinate points are given. (Duplicates should simply be ignored.)

In addition to printing the map, the program should return a 
dictionary (dict) where for every object there is an entry having
the tuple of the object coordinates (in (x, y) format) as the key 
and the number of the respective neighboring objects, as an integer, 
as the value. 

(The dict does not need to include information about the neighbors
of empty map locations.)

Example:

d = neighbor_count_map([(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), 
                        (5, 5), (6, 6), (7, 7), (8, 8), (2, 1),
                        (2, 0), (2, 3), (2, 4), (2, 2), (8, 4)]) 
...prints the map 
1~2~~~~~~~~~~~~~~~~
~43~~~~~~~~~~~~~~~~
~~4~~~~~~~~~~~~~~~~
~~34~~~~~~~~~~~~~~~
~~2~2~~~0~~~~~~~~~~
~~~~~2~~~~~~~~~~~~~
~~~~~~2~~~~~~~~~~~~
~~~~~~~2~~~~~~~~~~~
~~~~~~~~1~~~~~~~~~~

...and then, e.g., print(d[(2, 3)]) would print the value 3, because
the object at (2, 3) has 3 neighbors (that have 4, 4, and 2 neighbors 
themselves, as can be seen in the map above).

"""

def neighbor_count_map(object_locations):
    map_width = 19
    map_height = 9

    objects = set((x, y) for x, y in object_locations if 0 <= x < map_width and 0 <= y < map_height)

    map_grid = [['~' for _ in range(map_width)] for _ in range(map_height)]
    neighbor_counts = {}

    for (obj_x, obj_y) in objects:
        count = 0
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = obj_x + dx, obj_y + dy
                if (nx, ny) in objects:
                    count += 1
        neighbor_counts[(obj_x, obj_y)] = count

    for y in range(map_height):
        for x in range(map_width):
            if (x, y) in objects:
                map_grid[y][x] = str(neighbor_counts[(x, y)])

    for row in map_grid:
        print(''.join(row))

    return neighbor_counts

"""
Function ai_usage
(max 1 XP)
--------------------------
The function takes, as its only parameter, a string, and returns either a 
string stating what AI tools have been used in this work. If none, 
this must be told explicitly. 
- If the string starts with "for what", the function returns a string 
describing for what purposes AI tools have been used in this work. 
If such haven't been used for anything, this must be stated explicitly.
- If the string starts with "how", the function returns a string
describing how AI tools have been used in this work. If such haven't 
been used, this must be stated explicitly.
- Regarding all the three cases above, variations in capitalization 
must be allowed. That is, e.g., "What", "WHAT", "wHaT", etc. are all
considered equivalent with "what" and must be handled similarly.
- If the string cannot be recognized to correspond to any of the 
cases described, the function returns None.

If you do not implement this function, report the AI usage (what has 
been used, for  which purposes, and how) here, continuing this comment.
(In that case you do not get the XP for implementing the function, but 
you avoid possible penalties for unreported AI usage.)

"""

def ai_usage(query):
    q = query.lower().strip()
    
    if q.startswith("what"):
        return "No AI tools have been used in this work."
    elif q.startswith("for what"):
        return "AI tools have not been used for any purpose in this work."
    elif q.startswith("how"):
        return "AI tools have not been used in this work, so there is no method to describe."
    else:
        return None


