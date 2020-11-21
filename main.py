VALID_ATTRIBUTES = ("Customers.Name", "Customers.Age", "Orders.CustomerName", "Orders.Product", "Orders.Price")
STRING_QUOTES = ('"', "'", "`")
NUMBER_SIGN = ('+', '-')
DIGIT_NUMBER = ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9')
REL_OPT = ('<', '>', '<=', '>=', '<>', '=')
BOOLEAN_ALGEBRA = {"AND": 3, "OR": 2}

def isDigitValid(toCheck):
    return toCheck in DIGIT_NUMBER

def isUnsigned_NumberValid(toCheck):
    if(str.__len__(toCheck) == 1):
        return isDigitValid(toCheck)

    return isDigitValid(toCheck[0]) and isUnsigned_NumberValid(toCheck[1:])

def isNumberValid(toCheck):
    if toCheck[0] in NUMBER_SIGN:
        toCheck = toCheck[1:]

    return isUnsigned_NumberValid(toCheck)

def isStringValid(toCheck):
    lenOftoCheck = str.__len__(toCheck) - 1

    if toCheck[0] in STRING_QUOTES:
        if toCheck[lenOftoCheck] in STRING_QUOTES:
            if(toCheck[0] == toCheck[lenOftoCheck]):
                if(str.count(toCheck, toCheck[0]) == 2):
                    return True

    return False


def isAttributeValid(toCheck):
    return toCheck in VALID_ATTRIBUTES

def isConstantValid(toCheck):
    return isNumberValid(toCheck) or isStringValid(toCheck) or isAttributeValid(toCheck)

def isRel_OpValid(toCheck):
    return toCheck in REL_OPT

def isSimple_CondValid(toCheck):
    for op in REL_OPT:
            if(op in toCheck):
                indexOfOp = toCheck.index(op)
                splitedCond = str.split(toCheck, op, 1)
                if list.__len__(splitedCond) == 2:
                    firstCondition = splitedCond[0]
                    secondCondition = splitedCond[1]
                    return isConstantValid(firstCondition) and isConstantValid(secondCondition)

    return False

def isCondANDcondValid(toCheck):
        if ("AND" in toCheck):
            splitedCond = str.split(toCheck, " AND ", 1)
            if list.__len__(splitedCond) == 2:
                firstCondition = splitedCond[0]
                secondCondition = splitedCond[1]
                return isConditionValid(firstCondition) and isConditionValid(secondCondition)

        return False

def isCondORcondValid(toCheck):
    if ("OR" in toCheck):
        splitedCond = str.split(toCheck, " OR ", 1)
        if list.__len__(splitedCond) == 2:
            firstCondition = splitedCond[0]
            secondCondition = splitedCond[1]
            return isConditionValid(firstCondition) or isConditionValid(secondCondition)

    return False

def isPartCONDValid(toCheck):
    lenOftoCheck = str.__len__(toCheck) - 1

    if(toCheck[0] == '('):
        if(toCheck[lenOftoCheck] == ')'):
            return isConditionValid(toCheck[1:lenOftoCheck-1])

def isConditionValid(toCheck):
    if(isSimple_CondValid(toCheck) or isCondANDcondValid(toCheck) or
            isCondORcondValid(toCheck) or isPartCONDValid(toCheck)):
        return True

    return False

def isWhereSClauseValid(toCheck):
    if(isConditionValid(toCheck)):
        print("Hiade bibi")
        return True
    else:
        print("Parsing <condition> failed")
        return False


if __name__ == '__main__':
    while(True):
        query = input("Please enter your query: ")
        isWhereSClauseValid(query)


"""
#**********SELECT*******************
def isQueryValid(query):

def isSelectStatementValid(selectStatement):

def isOptional_DistinctValid():

   def isAttribute_ListValid():    
    if ()
    return True
    
    else
    ThrowExp ("Parsing <attribute_list> failed");
    
def isAtt_ListValid():

#**********FROM****************

def isFromStatementValid(fromStatement):

def isTable_ListValid():

def isTableValid(): #aa

"""







