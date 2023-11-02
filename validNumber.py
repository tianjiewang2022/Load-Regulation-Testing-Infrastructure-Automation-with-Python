# TODO: In practically all automation scenarios as we perform measurements of Device under Test (DUT), we query equipment (instruments) for different values (center frequency, voltage, current and so on). In general the queries can be even to a service that return some number as a string.
# Assume that as a result of your query you get a string that represents a number.
# For example, it could be “5” for 5 Volts measured by a multimeter.
# Please, help me to write a function that checks if a given string as a valid number.
import re


def isNumber(str):
    pattern = r'^[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?$'
    return re.match(pattern, str) is not None


def isNumber(str):
    return str.isdigit()


def isNumber(str):
    try:
        float(str)
        return True
    except ValueError:
        return False
