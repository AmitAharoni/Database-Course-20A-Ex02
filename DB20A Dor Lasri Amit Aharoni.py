VALID_TABLES = ("Customers", "Orders")
VALID_ATTRIBUTES = ("Customers.Name", "Customers.Age", "Orders.CustomerName", "Orders.Product", "Orders.Price")
STRING_QUOTES = ('"', "'", "`", "’")
NUMBER_SIGN = ('+', '-')
DIGIT_NUMBER = ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9')
REL_OPT = ('<=', '>=', '<>', '<', '>', '=')
valid_queries = [
        "SELECT Customers.Name    FROM Customers     WHERE Customers.Age=25    ;",
        "   SELECT Customers.Name FROM Customers WHERE Customers.Name=’Mike’;",
        "SELECT DISTINCT Customers.Name FROM Customers WHERE     Customers.Age=25;   ",
        "SELECT Customers.Name,Orders.Price FROM Customers,Orders WHERE Customers.Name=Orders.CustomerName   ;",
        "SELECT    Customers.Name,Orders.Price FROM Customers,Orders WHERE (Customers.Name=Orders.CustomerName )   AND Orders.Price>1000;",
        "SELECT Customers.Name   ,Orders.Price FROM  Customers,     Orders WHERE ( (Customers.Name=Orders.CustomerName) AND Customers.Name=’Mike’) OR (Orders.Price>59);",
        "SELECT Customers.Name,Orders.Price FROM Customers,Orders WHERE ((((Customers.Name=Orders.CustomerName) AND((Orders.Price > 59)) OR (Customers.Age=25))));",
        "SELECT Customers.Name,Orders.Price FROM Customers,Orders    WHERE ((   (Customers.Name=Orders.CustomerName) AND Customers.Name=’Mike’) OR (Orders.Price>59));",
        "SELECT      Customers.Name ,Orders.Price FROM       Customers,Orders WHERE (((((Customers.Name    =Orders.CustomerName    )  )     AND Customers.Name=’Mike’) OR ((Orders.Price>59) AND (((Orders.Product='Sony Playstation 5'))))));",
        "SELECT *      FROM Orders,Customers WHERE Customers.Age =25 OR Customers.Age <=25;",
        "SELECT Customers.Name,Orders.Price    FROM Customers,Orders WHERE (   Customers.Name=Orders.CustomerName OR Orders.Price>1000) AND Customers.Name=’Mike’; ",
        "SELECT Customers.Name,Orders.Price FROM Customers,Orders WHERE (Customers.Name=Orders.CustomerName OR (Orders.Price>1000) AND Customers.Name=’Mike’); ",
        "SELECT Customers.Name,Orders.Price FROM Customers,Orders WHERE (Customers.Name=Orders.CustomerName OR (Orders.Price>1000 AND Customers.Name=’Mike’)); ",
        "SELECT Customers.Name,    Orders.Price FROM Customers,Orders WHERE     ((( (Customers.Name=Orders.CustomerName) OR ((Orders.Price>1000)) AND (Customers.Name=’Mike’)))); ",
        "SELECT DISTINCT  * FROM Customers WHERE Customers.Name=’Mike’   ;",
        "SELECT Customers.Name FROM Customers WHERE Customers.Age=25;",
        "SELECT Customers.Name FROM Customers WHERE Customers.Name=’Mike’;",
        "SELECT Customers.Name,Orders.Price FROM Customers,Orders WHERE Customers.Name=Orders.CustomerName;",
        "SELECT Customers.Name,Orders.Price FROM Customers,Orders WHERE Customers.Name=Orders.CustomerName AND Orders.Price>1000;",
        "SELECT Customers.Name,Orders.Price FROM Customers,Orders WHERE (Customers.Name=Orders.CustomerName) AND Orders.Price>1000;",
        "SELECT Customers.Name,Orders.Price FROM Customers,Orders WHERE (Customers.Name=Orders.CustomerName) OR (Orders.Price>59);",
]

invalid_queries = [
        "SELECT Customers.Name,Orders.Price FROM Customers,Orders WHERE (Customers.Name=Orders.CustomerName) OR (Orders.Price>1000;",
        "SELECT Customers.Color,Orders.Price FROM Customers,Orders WHERE (Customers.Name=Orders.CustomerName) OR (Orders.Price>1000;",
        "SELECT Customers.Name,Orders.Price FROM Customers,Orders WHERE (Customers.Name=Orders.CustomerName) AND OR (Orders.Price>59);",
        "SELECT Customers.Name,,,,,,, DISTINCT Orders.Price FROM Customers,Orders WHERE Customers.Name=Orders.CustomerName AND Orders.Price>1000;",
        "SELECT Customers.Name,,asdd,,,, DISTINCT Orders.Price FROM Customers,Orders WHERE (Customers.Name=Orders.CustomerName AND) Orders.Price>1000;"
        "SELECT Customers.Name, DISTINCT Orders.Price FROM Customers,Orders WHERE (Customers.Name=Orders.CustomerName AND) Orders.Price>1000;",
        "SELECT * FROM Orders,Customers WHERE Customers.Age =25 OR;",
        "SELECT * FROM Orders,Customers WHERE Customers.Age =25 OR ;",
        "SELECT * FROM Orders,Customers WHERE Customers.Age =25 OR Customers.Age < =25;",
        "SELECT Customers.Name,Orders.Price FROM Customers,Orders WHERE (Customers.Name=Orders.CustomerName OR (Orders.Price>1000) AND Customers.Name=’Mike’; ",
        "SELECT Customers.Name,Orders.Price FROM Customers,Orders WHERE (Customers.Name=Orders.CustomerName( OR (Orders.Price>1000) AND Customers.Name=’Mike’; ",
        "SELECT Customers.Name,Orders.Price FROM Customers,Orders WHERE (Customers.Name=Orders.CustomerName) OR (Orders.Price>1000) AND Customers.Name=’Mike’(; ",
        "SELECT Customers.Name,Orders.Price FROM Customers,Orders WHERE (((Customers.Name=Orders.CustomerName OR (Orders.Price>1000)) AND Customers.Name=’Mike’); "
]

def isDigitValid(toCheck):
    return toCheck in DIGIT_NUMBER

def isUnsigned_NumberValid(toCheck):
    if (str.__len__(toCheck) == 1):
        return isDigitValid(toCheck)

    return isDigitValid(toCheck[0]) and isUnsigned_NumberValid(toCheck[1:])

def isNumberValid(toCheck):
    if toCheck[0] in NUMBER_SIGN:
        toCheck = toCheck[1:]

    return isUnsigned_NumberValid(toCheck)

def isStringValid(toCheck):
    lastIndex = str.__len__(toCheck) - 1

    if toCheck[0] in STRING_QUOTES:
        if toCheck[lastIndex] in STRING_QUOTES:
            if (toCheck[0] == toCheck[lastIndex]):
                if (str.count(toCheck, toCheck[0]) == 2):
                    return True

    return False

def isAttributeValid(toCheck):
    return toCheck in VALID_ATTRIBUTES

def isConstantValid(toCheck):
    return isNumberValid(toCheck) or isStringValid(toCheck) or isAttributeValid(toCheck)

def isRel_OpValid(toCheck):
    return toCheck in REL_OPT

def isCondOnStringAttribute(toCheck):
    return (toCheck == "Customers.Name" or toCheck == "Orders.CustomerName" or toCheck == "Orders.Product")

def isCondOnIntgerAttribute(toCheck):
    return (toCheck == "Customers.Age" or toCheck == "Orders.Price")

def isSameType(firstCond, secondCond):
    if (isCondOnStringAttribute(firstCond)):
        return isCondOnStringAttribute(secondCond) or isStringValid(secondCond)
    else:            #isCondOnIntgerAttribute == true
        return isCondOnIntgerAttribute(secondCond) or isNumberValid(secondCond)

def isSimple_CondValid(toCheck):
    for op in REL_OPT:
        indexOfOp = str.find(toCheck, op)
        if (indexOfOp != -1):
            splited = str.split(toCheck, op, 1)
            firstCond = cleanSpaces(splited[0])
            secondCond = cleanSpaces(splited[1])
            return isConstantValid(firstCond) and isConstantValid(secondCond) and isSameType(firstCond, secondCond)

    return False

def isCondANDcondValid(toCheck):
    if ("AND" in toCheck):
        splited = str.split(toCheck, "AND", 1)
        return isConditionValid(cleanSpaces(splited[0])) and isConditionValid(cleanSpaces(splited[1]))

    return False

def isCondORcondValid(toCheck):
    if ("OR" in toCheck):
        splited = str.split(toCheck, "OR", 1)
        return isConditionValid(cleanSpaces(splited[0])) and isConditionValid(cleanSpaces(splited[1]))

    return False

def isPartCONDValid(toCheck):
    lastindex = str.__len__(toCheck) - 1

    if(lastindex != -1):    #for "" AND X case!
        if (toCheck[0] == '('):
            if (toCheck[lastindex] == ')'):
                updatedCond = cleanSpaces(toCheck[1:lastindex])
                return isConditionValid(updatedCond)

    return False

def isConditionValid(toCheck):
    return (isSimple_CondValid(toCheck) or isCondANDcondValid(toCheck)
            or isCondORcondValid(toCheck) or isPartCONDValid(toCheck))

def endOfQuerySignHandler(whereStatement):
    lastIndex = (str.__len__(whereStatement) - 1)

    if(whereStatement[lastIndex] == ";"):
        whereStatement = cleanSpaces(whereStatement[:lastIndex])

    return whereStatement

def isWhereValid(whereStatement):
    whereStatement = endOfQuerySignHandler(whereStatement)

    if (isConditionValid(whereStatement)):
            return True

    print("Invalid. \nParsing <condition> failed")
    return False

def isTableValid(toCheck):
    return toCheck in VALID_TABLES

def isMultiTablesValid(toCheck):
    indexOfOp = str.find(toCheck, ",")
    if (indexOfOp != -1):
        return isTable_ListValid(cleanSpaces(toCheck[:indexOfOp])) and isTable_ListValid(cleanSpaces(toCheck[indexOfOp+1:]))

    return False

def isTable_ListValid(toCheck):
    return isTableValid(toCheck) or isMultiTablesValid(toCheck)

def isFromValid(fromStatement):
    if (isTable_ListValid(fromStatement)):
        return True
    else:
        print("Invalid. \nParsing <table_list> failed")
        return False

def isOptional_DistinctValid(toCheck):
    if(toCheck[0:9] == "DISTINCT "):
        toCheck = toCheck[9:]

    return True, toCheck

def isMultiAttributsValid(toCheck):
    indexOfOp = str.find(toCheck, ",")
    if (indexOfOp != -1):
        return isAtt_ListValid(cleanSpaces(toCheck[:indexOfOp])) and isAtt_ListValid(cleanSpaces(toCheck[indexOfOp+1:]))

    return False

def isAtt_ListValid(toCheck):
    return isAttributeValid(toCheck) or isMultiAttributsValid(toCheck)

def isAttribute_ListValid(toCheck):
    return isAttributeIsAll(toCheck) or isAtt_ListValid(toCheck)

def isAttributeIsAll(toCheck):
    return toCheck == "*"

def isSelectValid(selectStatement):
    afterDistinctCheck, updatedSelectStatement = isOptional_DistinctValid(selectStatement)

    if afterDistinctCheck and isAttribute_ListValid(updatedSelectStatement):
        return True
    else:
        print("Invalid. \nParsing <attribute_list> failed")
        return False

def getSelectStatement(query):
    afterSelectIndex = 7
    fromIndex = query.find("FROM") - 1
    return query[afterSelectIndex:fromIndex]

def getFromStatement(query):
    afterfromIndex = query.find("FROM") + 5
    whereIndex = query.find("WHERE") - 1
    return query[afterfromIndex:whereIndex]

def getWhereStatement(query):
    afterWhereIndex = query.find("WHERE") + 6
    lastIndex = (str.__len__(query) - 1)
    return query[afterWhereIndex:]

def cleanSpaces(query):
    return (' '.join(query.split()))

def isAttributeCompatibleWithTable(selectStatement, fromStatement):
    if(isAttributeIsAll(selectStatement) or  isAttributeListCompatibleWithTable(selectStatement, fromStatement)):
        return True

    print("Invalid. \nParsing <attribute_list> failed")
    return False

def isAttributeListCompatibleWithTable(selectStatement, fromStatement):
    isSelectContainCustomers = selectStatement.__contains__("Customers")
    isSelectContainOrders = selectStatement.__contains__("Orders")

    isFromContainCustomers = fromStatement.__contains__("Customers")
    isFromContainOrders = fromStatement.__contains__("Orders")

    if((isSelectContainCustomers and not isFromContainCustomers)
            or (isSelectContainOrders and not isFromContainOrders)):
        return False

    return True

def isQueryValid(query):
    cleanQuery = cleanSpaces(query)
    selectStatement = getSelectStatement(cleanQuery)
    fromStatement = getFromStatement(cleanQuery)
    whereStatement = getWhereStatement(cleanQuery)

    if(isSelectValid(selectStatement) and isFromValid(fromStatement) and isWhereValid(whereStatement)
            and isAttributeCompatibleWithTable(selectStatement, fromStatement)):
            print("valid")

if __name__ == '__main__':
    print("=====valid====")
    for valid_query in valid_queries:
        isQueryValid(valid_query)
    print("=====invalid====")
    for invalid_query in invalid_queries:
        isQueryValid(invalid_query)
    print("=============")

    while(True):
        query = input("Please enter your query (must contain SELECT, FROM, WHERE):\n")
        isQueryValid(query)