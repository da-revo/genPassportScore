# GDP Access score

## Intro

 Since most rankings of passports are dogshit, I have created a ranking system based on the relevance ( based on GDP ) of the countries that each country's civilian passport grants easy access to.

 *Does visa on arrival to China matter more to you than visa free access to Samoa, The Gambia and Liberia?*

 If yes, you've come to the right place !  
 If not, you can go suck a fat one. Tschüss. :)  

 Try it out here [get.passportrank.tk](http://get.passportrank.tk)

## How it works

 The python script makes calculations based on data from wikipedia accessed through an API calls.

 Score_for_country = summation_of ( GDP * weight_based_on_visa_requirement ) over_all_countries.

 The script runs offline after first run through all countries by reusing saved data

## Requirements

* A python interpreter
* **matplotlib**  and  **pandas**  for the `plot` argument
* a UNIX based terminal for the `show` argument

## How to use

 Open terminal, `cd`  into the directory and type `python genPassportScore.py` to generate a CSV file with all scores.

 type `python genPassportScore.py country` to find GDP access score for the country input as `country`  
 eg: `python genPassportScore.py China`

 type `python genPassportScore.py country1 vs country2` to get a detailed comparison of the access each of the passports ordered by the magnitude of difference  
 eg: `python genPassportScore.py United States vs Canada`

 type `python genPassportScore.py list` to get a list of valid countries

 type `python genPassportScore.py show` to open up the created csv file

 type `python3 genPassportScore.py plot` to plot the top and bottom  countries on a bar graph

 type `log` just after `1_genPassportScore.py` to get all actions performed, output to the terminal  
 eg: `python genPassportScore.py log` or `python genPassportScore.py log China`

 you can modify the weights in the *a1_weightsTable.py* and the program will use those weights ; else it will use the hardcoded weights

 *a1_weightsTable.py* is generated after the first run

 *Ranks* will be displayed after first execution without arguments 

## If something is broken

 just create a new folder with the files in this repo
