# UofT-CSC148-Canadian-Weather-Data

Introduction
The internet is full of interesting data that you can explore. In this assignment, you will be developing Python code that can read in historical weather data from files, store that data in appropriate data structures, and then compute some meaningful statistics based on the data.

The program
The code consists of three Python classes:

An instance of DailyWeather is a record of weather facts for a single day (temperature and precipitation).
An instance of HistoricalWeather is a record of weather information on various dates, for a fixed place on Earth.
An instance of Country is a record of weather information on various dates, for various locations in a country.
There are also two top-level functions, that is, functions that are defined outside of any class.

The interface to the functions and to the classes have been designed, and we have decided how data will be represented, but most of the method bodies need to be written.

Input to the program
The input to the program is real weather data, from a Government of Canada website: https://climate.weather.gc.ca/historical_data/search_historic_data_e.html.

The data stored is in csv (comma-separated values) files. In a csv file, each line contains values separated by commas. Open the example weather files in PyCharm, or a text editor of your choice, to see the format. If you open these files instead in excel, they will be displayed as a spreadsheet. But remember what’s really in the file! For instance, there may be double quotes around the values in the csv files. You’ll need to strip these off to get at the content you are interested in.

The data files record, among other things, rainfall, snowfall, and precipitation. You might imagine that precipitation is the sum of rainfall plus snowfall, but the relationship is more complicated than that (and in fact doesn’t matter to this assignment).

Near the top of weather.py, there is a list of CONSTANTS corresponding to what is stored in each column of a weather data file. You must use these constants in your program rather than “hard coded” values. For instance, the maximum temperature is always stored in column 9, but to extract it from a row you must use the constant MAX_TEMP rather than the number 19. (Why do you think this is important?)

Here are some things your program can assume will be true for any data file it is asked to read:

A weather data file will always contain a header row, which specifies what data each column in the file corresponds to.
Every data file will always have the same columns in the same order as you see in our sample data files.
The header row will be followed by zero or more rows of weather data.
The weather data will be in order from oldest dates to most recent dates.
Missing or ill-formed data
Part of working with real data is dealing with incomplete or ill-formed information. In this assignment, if a row in a weather data file is missing one or more of these values:

Longitude, Latitude
Station Name
Year, Month, Day
Max Temp, Min Temp, Mean Temp
Total Rain, Total Snow, Total Precip
then that entire row should not be included in the historical weather data. Similarly, if any piece of data is of the wrong sort, then the entire row should not be included. For instance, if we find “boo!” in the Month column, we should ignore that row.

The columns “Total Rain Flag”, “Total Snow Flag”, and “Total Precip Flag” should either be empty or contain the value “T”. (“T” indicates that there were “trace amounts”.) If you encounter any value aside from these, it should be considered ill-formed and the entire row should not be included.

About testing
We have provided several things to help you test your code:

the doctests in the starter code,
unit tests, written using pytest, in a0_starter_tests.py, and
a slightly larger set of tests that you can run via MarkUs.
However, we have further hidden tests that we will use to assess your code. Your assignment grade will be based on the autotesting that we do, and you can be sure we’ll try to break your code as hard as we can, so you should also! To test your own code thoroughly, add more tests to a0_starter_tests.py.

The most efficient way to produce code that works is to create and run your test cases as early as possible, and to re-run them after every change to your code. A very disciplined approach is to design and implement your unit tests for a method before you write the method. (This is called “test-driven development”.) You can do this one method at a time, getting each one working before moving on to the next. Don’t forget that each method has doctests that you can run – even if you have written the code before writing its unit tests.

Note: We will not directly test any helper methods that you define. (Think about why this wouldn’t be possible.)
