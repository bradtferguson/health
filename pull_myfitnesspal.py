import myfitnesspal
import datetime
import pandas as pd
import collections
from typing import Dict, List

import csv, sys, os
from datetime import datetime

# Get account info
client = myfitnesspal.Client('bradtferguson', password='Iluvet@k4ev')
startYear = "2021"
# Get limits
beginningDate = datetime.strptime(startYear, "%Y").date()
beginningYear = beginningDate.year
daysInMonth = {1:31, 2:28, 3:31, 4:30, 5:31, 6:30, 7:31, 8:31, 9:30, 10:31, 11:30, 12:31}
emptyNutrition = [None, None, None, None, None, None]

print("")
print("################################################")
print("# Scraping MyFitnessPal                        #")
print("# Make sure your account is set to public      #")
print("# and your username and pass are in keychain   #")
print("################################################")
print("")

today = datetime.now().date()
currentYear = today.year

print("")
print("################################################")
print("# Get nutrition and weight information         #")
print("################################################")
print("")

for yearIndex in range(beginningYear, currentYear + 1):

    # Create a file name based on this year's data
    thisFileName = "healthData_%s.csv" % yearIndex

    # Open CSV as read and write.
    # If file exists, open for read / write
    #   else, create file, write only.
    try:
        f = open(thisFileName, "r+")  # Check to see if file is complete,
        row_count = sum(1 for row in f)  # else, overwrite the file
        if (row_count != 366):  # A year of rows plus headers, and an empty line at end.
            f = open(thisFileName, "w+")
            row_count = 0
    except EnvironmentError:
        f = open(thisFileName, "w+")  # If file does not exist, create it.
        row_count = 0

    writer = csv.writer(f)

    # Check number of lines. If the year wasn't captured, start over.
    if (row_count < 365):
        # Write headers for totals
        writer.writerow(
            ["Date", "Calories", "Carbohydrates", "Fat", "Protein", "Sodium", "Sugar", "Weight", "Body Fat %"])
        sys.stdout.write(str(yearIndex) + ": ")  # Print has a linefeed.
        sys.stdout.flush()
        for monthIndex in range(1, 12 + 1):

            beginningOfMonthStr = "%s-%s-%s" % (yearIndex, monthIndex, 1)
            endOfMonthStr = "%s-%s-%s" % (yearIndex, monthIndex, daysInMonth[monthIndex])

            beginningOfMonth = datetime.strptime(beginningOfMonthStr, "%Y-%m-%d").date()
            endOfMonth = datetime.strptime(endOfMonthStr, "%Y-%m-%d").date()

            thisMonthsWeights = dict(client.get_measurements('Weight', beginningOfMonth, endOfMonth))
            thisMonthsBodyfats = dict(client.get_measurements('Body Fat %', beginningOfMonth, endOfMonth))

            for dayIndex in range(1, daysInMonth[monthIndex] + 1):

                fullDateIndex = "%s-%s-%s" % (yearIndex, monthIndex, dayIndex)
                thisDate = datetime.strptime(fullDateIndex, "%Y-%m-%d").date()
                if (thisDate > today):
                    break;

                thisDaysNutritionData = client.get_date(yearIndex, monthIndex, dayIndex)
                thisDaysNutritionDataDict = thisDaysNutritionData.totals
                thisDaysNutritionValues = thisDaysNutritionDataDict.values()

                thisDaysWeight = [(thisMonthsWeights.get(thisDate))]
                thisDaysBodyfat = [(thisMonthsBodyfats.get(thisDate))]

                if (len(thisDaysNutritionValues) < 6):
                    thisDaysNutritionValues = emptyNutrition
                print(fullDateIndex)

                dataRow = [fullDateIndex] + list(thisDaysNutritionValues) + thisDaysWeight + thisDaysBodyfat
                if dataRow:
                    writer.writerow(dataRow)

            sys.stdout.write("#")
            sys.stdout.flush()
        print(" -- Done.")
        f.close()
    else:
        print((str(yearIndex) + ": Exists and is complete."))

data = pd.read_csv('healthData_2021.csv')
data['Date'] = pd.to_datetime(data['Date'], format='%Y-%m-%d')
data = data.dropna().reset_index(drop=True)
data['Macro_calories'] = data['Carbohydrates']*4 + data['Protein']*4 + data['Fat']*9
for col in data.columns[1:]:
    data[f'{col}_MA'] = data.loc[:,col].rolling(window=7, min_periods=1).mean()
data = data.sort_values(by='Date', ascending=False)
data.to_csv('healthData_2021.csv')