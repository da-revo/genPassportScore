# get GDP Access score

 Open terminal, `cd`  into the directory and type `python 1_genPassportScore.py` to generate a CSV file with all scores.

 type `python 1_genPassportScore.py country` to find GDP access score for the country input as `country`
 eg: `python 1_genPassportScore.py China`

 type `python 1_genPassportScore.py list` to get a list of valid countries

 type `log` just after `1_genPassportScore.py` to get all actions performed output to the terminal
 eg: `python 1_genPassportScore.py log` or `python 1_genPassportScore.py log China`

 you can modify the weights in the a1_weightsTable.py and the program will use those weights ; else it will use the hardcoded weights
