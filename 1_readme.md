# get GDP Access score

## Intro

 Since most rankings of passports are dogshit, I have created a ranking based on the relevance ( based on GDP )of the countries that each country's civilian passport grants easy access to.

## How it works

 The python script makes calculations based on data from wikipedia accessed through an API call.

 Score_for_country= summation_of ( GDP * weight_based_on_visa_requirement ) over_all_countries.

 The script runs offline after first run through all countries by reusing saved data

## Requirements

* A python interpreter
* *matplotlib*  and  *pandas*  for the `plot` argument
* a UNIX based terminal for `show` argument

## How to use

 Open terminal, `cd`  into the directory and type `python 1_genPassportScore.py` to generate a CSV file with all scores.

 type `python 1_genPassportScore.py country` to find GDP access score for the country input as `country`
 eg: `python 1_genPassportScore.py China`

 type `python 1_genPassportScore.py list` to get a list of valid countries

 type `python 1_genPassportScore.py show` to open up the created csv file

 type `python3 1_genPassportScore.py plot` to plot the top and bottom  countries on a bar graph

 type `log` just after `1_genPassportScore.py` to get all actions performed, output to the terminal
 eg: `python 1_genPassportScore.py log` or `python 1_genPassportScore.py log China`

 you can modify the weights in the a1_weightsTable.py and the program will use those weights ; else it will use the hardcoded weights

 a1_weightsTable.py is generated after the first run