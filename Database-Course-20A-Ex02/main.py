from Cartesian import Cartesian
from NJoin import NJoin
from Pi import Pi
from Sigma import Sigma
from TableData import TableData
import random
import copy

VALID_TABLES = ("R", "S")
VALID_ATTRIBUTES = ("R.A", "R.B", "R.C", "R.D", "R.E", "S.D", "S.E", "S.F", "S.H", "S.I")
STRING_QUOTES = ('"', "'", "`", "’")
NUMBER_SIGN = ('+', '-')
DIGIT_NUMBER = ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9')
REL_OPT = ('<=', '>=', '<>', '<', '>', '=')

'''
 // run on example
SELECT R.C,S.F FROM S,R WHERE R.C=S.F; # run on example
SELECT R.C,S.F FROM S,R WHERE R.E=S.E; # go to cartesian attributes RE, RE
SELECT R.C,S.F FROM S,R WHERE (R.E=S.E AND R.C=S.F) AND (R.A = 2 AND 3=3);


SELECT R.A FROM R WHERE R.A=25;
SELECT R.B FROM R WHERE R.B=100;
SELECT DISTINCT R.B FROM R WHERE R.B=25;
SELECT R.B,S.D FROM R,S WHERE R.B=S.D;
SELECT R.C,S.F FROM S,R WHERE R.C=S.F AND S.F>1000;
SELECT R.C,S.F FROM R,S WHERE ((R.C=S.F) AND (S.F>1000)) AND (R.C=S.F);
SELECT      R.A ,R.A FROM       R,S WHERE (((R.A    =100  )     AND R.A=100) AND (R.A>59) AND (R.A= 5));
SELECT R.C,S.F FROM R,S WHERE (R.C=S.F) AND (R.C>59);
SELECT R.E,    S.H FROM R,S WHERE     ((( (R.E=S.H) OR ((S.H>1000)) AND (R.E=100))));
SELECT R.E,    S.H FROM R,S WHERE     ((( (R.E=S.H) AND ((S.H>1000)) OR (R.E=100))));
SELECT R.E,    S.H FROM R,S WHERE     (R.E=S.H AND S.H>1000) OR (R.E=100);
'''

def makeExpression(query):
    cleanQuery = cleanSpaces(query)
    selectStatement = getSelectStatement(cleanQuery)
    fromStatement = getFromStatement(cleanQuery)
    whereStatement = endOfQuerySignHandler(getWhereStatement(cleanQuery))

    return [Pi(selectStatement, None), Sigma(whereStatement, None), Cartesian(None, fromStatement)]

def printExpression(operatorsList):
    i = 0
    while i < operatorsList.__len__():
        if operatorsList[i].getDescription() is not None and operatorsList[i].getTables() is not None:
            print(operatorsList[i].getOperatorName() + "[" + operatorsList[i].getDescription() + "]" + "(" + operatorsList[i].getTables() + ")", end="")
        elif operatorsList[i].getDescription() is None and operatorsList[i].getTables() is not None:
            # Cartesian
            cartesianOrNjoin = operatorsList[i]

            if cartesianOrNjoin.isOperatorInFirst() and cartesianOrNjoin.isOperatorInSecond():
                firstSigma = operatorsList[i + 1]
                secondSigma = operatorsList[i + 2]
                print(cartesianOrNjoin.getOperatorName() + "(" + firstSigma.getOperatorName() + "[" + firstSigma.getDescription() + "]" + "(" + firstSigma.getTables() + ")",  ",",
                       secondSigma.getOperatorName() + "[" + secondSigma.getDescription() + "]" + "(" + secondSigma.getTables() + "))",  end="")
                i += 2
            elif cartesianOrNjoin.isOperatorInFirst() and not cartesianOrNjoin.isOperatorInSecond():
                firstSigma = operatorsList[i + 1]
                print(cartesianOrNjoin.getOperatorName() + "(" + firstSigma.getOperatorName() + "[" + firstSigma.getDescription() + "]" + "(" + firstSigma.getTables() + ")"
                       + cartesianOrNjoin.getTables() + ")", end = "")
                i += 1
            elif not cartesianOrNjoin.isOperatorInFirst() and cartesianOrNjoin.isOperatorInSecond():
                secondSigma = operatorsList[i + 1]
                print(cartesianOrNjoin.getOperatorName() + "(" + cartesianOrNjoin.getTables() + secondSigma.getOperatorName() + "[" + secondSigma.getDescription() + "]" + "(" + secondSigma.getTables() + "))" ,end = "")
                i += 1
            else:
                print(cartesianOrNjoin.getOperatorName() + "(" + operatorsList[i].getTables() + ")", end="")

        elif operatorsList[i].getDescription() is not None and operatorsList[i].getTables() is None:
            print(operatorsList[i].getOperatorName() + "[" + operatorsList[i].getDescription() + "]" + "(", end="")
        else:
            print(operatorsList[i].getOperatorName() + "(", end="")
        i += 1

    for i in range(operatorsList.__len__() - 1): #  operator.getDescription() is not None and operator.getTables() is not None close one paratensis
        if i == (operatorsList.__len__() - 2):
            print(")")
        else:
            print(")", end="")

def splitANDCond(toCheck):
    while (isSimple_CondValid(toCheck) or isCondANDcondValid(toCheck) or isCondORcondValid(toCheck) or isPartCONDValid(
            toCheck)) and isPartCONDValid(toCheck):
        toCheck = toCheck[1:toCheck.__len__() - 1]
    if (isSimple_CondValid(toCheck) or isCondANDcondValid(toCheck) or isCondORcondValid(toCheck) or isPartCONDValid(
            toCheck)) and isCondANDcondValid(toCheck):
        splited = str.split(toCheck, "AND")
        numOfIter = splited.__len__()
        index = 1

        while index != numOfIter:
            firstCond = ""
            secCond = ""
            i = 0
            while i != index:
                firstCond += splited[i]
                i += 1
                firstCond += "AND"
            firstCond = firstCond[:firstCond.__len__() - 3]
            while i != numOfIter:
                secCond += splited[i]
                i += 1
                secCond += "AND"
            secCond = secCond[:secCond.__len__() - 3]
            index += 1

            if isConditionValid(cleanSpaces(firstCond)) and isConditionValid(cleanSpaces(secCond)):
                return cleanSpaces(firstCond), cleanSpaces(secCond)

def isOperatorContainAND(operator):
    return operator.getDescription().__contains__(" AND ") and isConditionValid(operator.getDescription())

def notContainTheOtherTable(toCheck, table):
    if table == "R":
        otherTable = "S"
    else:
        otherTable = "R"

    return not toCheck.__contains__(otherTable)

def isANDMainAlgebraBoolean(operator):
    return (isSimple_CondValid(operator) or isCondANDcondValid(operator) or isCondORcondValid(
        operator) or isPartCONDValid(
        operator)) and not isCondORcondValid(operator)

def Rule4(operatorList):
    for operator in operatorList:
        if isinstance(operator, Sigma):
            if isOperatorContainAND(operator):
                if isANDMainAlgebraBoolean(operator.getDescription()):
                    indexToAdd = operatorList.index(operator) + 1
                    firstCond, secCond = splitANDCond(cleanSpaces(operator.getDescription()))
                    operator.setDescription(firstCond)
                    operatorList.insert(indexToAdd, (Sigma(secCond, None)))
                    break

def Rule4a(operatorList):
    for operator in operatorList:
        if isinstance(operator, Sigma):
            indexOfFirstSigma = operatorList.index(operator)
            if indexOfFirstSigma < operatorList.__len__() - 1:
                if isinstance(operatorList[indexOfFirstSigma + 1], Sigma):
                    temp = operatorList[indexOfFirstSigma]
                    operatorList[indexOfFirstSigma] = operatorList[indexOfFirstSigma + 1]
                    operatorList[indexOfFirstSigma + 1] = temp
                    break

def Rule6(operatorList):
    for operator in operatorList:
        if isinstance(operator, Sigma):
            indexOfSigma = operatorList.index(operator)
            if (indexOfSigma + 1 < operatorList.__len__()):
                indexOfSigma = operatorList.index(operator)
                if isinstance(operatorList[indexOfSigma + 1], Cartesian) or isinstance(operatorList[indexOfSigma + 1], NJoin):
                    cartesianOrNJoin = operatorList[indexOfSigma + 1]
                    tables = cartesianOrNJoin.getTables()
                    if not cartesianOrNJoin.isOperatorInFirst():
                        indexOfComma = tables.index(',')
                        firstTable = cleanSpaces(tables[0:indexOfComma])
                        cond = operator.getDescription()
                        if cond.__contains__(firstTable) and notContainTheOtherTable(cond, firstTable):
                            cartesianOrNJoin.setTables(tables[indexOfComma:])
                            if cartesianOrNJoin.getTables() == ",":
                                cartesianOrNJoin.setTables(None)
                            operator.setTables(firstTable)
                            temp = operatorList[indexOfSigma]
                            operatorList[indexOfSigma] = operatorList[indexOfSigma + 1]
                            operatorList[indexOfSigma + 1] = temp
                            break

def Rule6a(operatorList):
    for operator in operatorList:
        if isinstance(operator, Sigma):
            indexOfSigma = operatorList.index(operator)
            if (indexOfSigma + 1 < operatorList.__len__()):
                if isinstance(operatorList[indexOfSigma + 1], Cartesian) or isinstance(operatorList[indexOfSigma + 1],
                                                                                       NJoin):
                    cartesianOrNjoin = operatorList[indexOfSigma + 1]
                    tables = cartesianOrNjoin.getTables()
                    if not cartesianOrNjoin.isOperatorInSecond():
                        indexOfComma = tables.index(',')
                        secTable = cleanSpaces(tables[indexOfComma + 1:])  # chance for index +1  R,S
                        cond = operator.getDescription()
                        if cond.__contains__(secTable) and notContainTheOtherTable(cond, secTable):
                            cartesianOrNjoin.setTables(tables[:indexOfComma + 1])
                            if cartesianOrNjoin.getTables() == ",":
                                cartesianOrNjoin.setTables(None)
                            operator.setTables(secTable)
                            temp = operatorList[indexOfSigma]
                            operatorList[indexOfSigma] = operatorList[indexOfSigma + 1]
                            operatorList[indexOfSigma + 1] = temp
                            break

def Rule5a(operatorList):
    for operator in operatorList:
        if isinstance(operator, Pi):
            indexOfPi = operatorList.index(operator)
            if (indexOfPi + 1 < operatorList.__len__()):
                if isinstance(operatorList[indexOfPi + 1], Sigma):
                    sigma = operatorList[indexOfPi + 1]
                    attributePi = operator.getDescription()
                    tableOfSigma = sigma.getTables()
                    if tableOfSigma is not None:
                        if attributePi.__contains__(tableOfSigma) and notContainTheOtherTable(attributePi,
                                                                                              tableOfSigma):
                            operator.setTables(tableOfSigma)
                            sigma.setTables(None)
                            temp = operatorList[indexOfPi]
                            operatorList[indexOfPi] = operatorList[indexOfPi + 1]
                            operatorList[indexOfPi + 1] = temp
                            break

def oneOfCondInAllPredicateContainsBooleanAlgebra(listOfCond):
    for cond in listOfCond:
        if cond.__contains__("AND") or cond.__contains__("OR"):
            return True

    return False

def getOnePredicateThatContainsAndRemoveFromList(allPredicate):
    for cond in allPredicate:
        if cond.__contains__("AND") or cond.__contains__("OR"):
            condToReturn = cond
            allPredicate.remove(condToReturn)

            return condToReturn

def splitANDorORCond(condToSplit):
    while (isSimple_CondValid(condToSplit) or isCondANDcondValid(condToSplit) or isCondORcondValid(
            condToSplit) or isPartCONDValid(condToSplit)) and isPartCONDValid(condToSplit):
        condToSplit = condToSplit[1:condToSplit.__len__() - 1]
    if (isSimple_CondValid(condToSplit) or isCondANDcondValid(condToSplit) or isCondORcondValid(
            condToSplit) or isPartCONDValid(condToSplit)) and isCondANDcondValid(condToSplit):
        splited = str.split(condToSplit, "AND")
        numOfIter = splited.__len__()
        index = 1

        while index != numOfIter:
            firstCond = ""
            secCond = ""
            i = 0
            while i != index:
                firstCond += splited[i]
                i += 1
                firstCond += "AND"
            firstCond = firstCond[:firstCond.__len__() - 3]
            while i != numOfIter:
                secCond += splited[i]
                i += 1
                secCond += "AND"
            secCond = secCond[:secCond.__len__() - 3]
            index += 1

            if isConditionValid(cleanSpaces(firstCond)) and isConditionValid(cleanSpaces(secCond)):
                return cleanSpaces(firstCond), cleanSpaces(secCond)

    if (isSimple_CondValid(condToSplit) or isCondANDcondValid(condToSplit) or isCondORcondValid(
            condToSplit) or isPartCONDValid(
            condToSplit)) and isCondORcondValid(condToSplit):
        if ("OR" in condToSplit):
            splited = str.split(condToSplit, "OR")
            numOfIter = splited.__len__()
            index = 1

            while index != numOfIter:
                firstCond = ""
                secCond = ""
                i = 0

                while i != index:
                    firstCond += splited[i]
                    i += 1
                    firstCond += "OR"
                firstCond = firstCond[:firstCond.__len__() - 2]
                while i != numOfIter:
                    secCond += splited[i]
                    i += 1
                    secCond += "OR"
                secCond = secCond[:secCond.__len__() - 2]

                index += 1

                if isConditionValid(cleanSpaces(firstCond)) and isConditionValid(cleanSpaces(secCond)):
                    return cleanSpaces(firstCond), cleanSpaces(secCond)

def splitCondIntoSimpleConditions(predicate):
    allPredicate = [predicate]

    while oneOfCondInAllPredicateContainsBooleanAlgebra(allPredicate):
        condToSplit = getOnePredicateThatContainsAndRemoveFromList(allPredicate)
        firstCond, secCond = splitANDorORCond(condToSplit)
        allPredicate.append(firstCond)
        allPredicate.append(secCond)

    return allPredicate

def wrapperSplitCondIntoSimpleConditions(allPredicate):
    for cond in allPredicate:
        if not cond.__contains__("=") or not cond.__contains__("S") or not cond.__contains__("R"):
            return False

    return True

def Rule11b(operatorList):
    for operator in operatorList:
        if isinstance(operator, Sigma):
            indexOfSigma = operatorList.index(operator)
            allPredicate = splitCondIntoSimpleConditions(operator.getDescription())
            if wrapperSplitCondIntoSimpleConditions(allPredicate):
                if (indexOfSigma + 1 < operatorList.__len__()):
                    if isinstance(operatorList[indexOfSigma + 1], Cartesian):
                        cartesian = operatorList[indexOfSigma + 1]
                        tables = cartesian.getTables()
                        if tables.__contains__("S") and tables.__contains__("R"):
                            indexOfCartesian = indexOfSigma + 1
                            njoinToAdd = NJoin(None, cartesian.getTables())
                            operatorList.pop(indexOfSigma)
                            operatorList.pop(indexOfCartesian - 1)  # because we removed sigma
                            operatorList.insert(indexOfSigma, njoinToAdd)
                            break

# ------------------------------------------EX01 copied functions--------------------------------------------------------
def endOfQuerySignHandler(whereStatement):
    lastIndex = (str.__len__(whereStatement) - 1)

    if (whereStatement[lastIndex] == ";"):
        whereStatement = cleanSpaces(whereStatement[:lastIndex])

    return whereStatement

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

def isCondOnIntgerAttribute(toCheck):
    return toCheck in VALID_ATTRIBUTES

def isCondOnStringAttribute(toCheck):
    return False

def isDigitValid(toCheck):
    return toCheck in DIGIT_NUMBER

def isSameType(firstCond, secondCond):
    if (isCondOnStringAttribute(firstCond)):
        return isCondOnStringAttribute(secondCond) or isStringValid(secondCond)
    else:  # isCondOnIntgerAttribute == true
        return isCondOnIntgerAttribute(secondCond) or isNumberValid(secondCond)

def isAttributeValid(toCheck):
    return toCheck in VALID_ATTRIBUTES

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

def isConstantValid(toCheck):
    return isNumberValid(toCheck) or isStringValid(toCheck) or isAttributeValid(toCheck)

def isSimple_CondValid(toCheck):
    for op in REL_OPT:
        indexOfOp = str.find(toCheck, op)
        if (indexOfOp != -1):
            splited = str.split(toCheck, op, 1)
            firstCond = cleanSpaces(splited[0])
            secondCond = cleanSpaces(splited[1])
            return isConstantValid(firstCond) and isConstantValid(secondCond) and isSameType(firstCond, secondCond)

    return False

def isCondORcondValid(toCheck):
    if ("OR" in toCheck):
        splited = str.split(toCheck, "OR")
        numOfIter = splited.__len__()
        index = 1

        while index != numOfIter:
            firstCond = ""
            secCond = ""
            i = 0

            while i != index:
                firstCond += splited[i]
                i += 1
                firstCond += "OR"
            firstCond = firstCond[:firstCond.__len__() - 2]
            while i != numOfIter:
                secCond += splited[i]
                i += 1
                secCond += "OR"
            secCond = secCond[:secCond.__len__() - 2]

            index += 1

            if isConditionValid(cleanSpaces(firstCond)) and isConditionValid(cleanSpaces(secCond)):
                return True

    return False

def isCondANDcondValid(toCheck):
    if ("AND" in toCheck):
        splited = str.split(toCheck, "AND")
        numOfIter = splited.__len__()
        index = 1

        while index != numOfIter:
            firstCond = ""
            secCond = ""
            i = 0

            while i != index:
                firstCond += splited[i]
                i += 1
                firstCond += "AND"
            firstCond = firstCond[:firstCond.__len__() - 3]
            while i != numOfIter:
                secCond += splited[i]
                i += 1
                secCond += "AND"
            secCond = secCond[:secCond.__len__() - 3]

            index += 1

            if isConditionValid(cleanSpaces(firstCond)) and isConditionValid(cleanSpaces(secCond)):
                return True

    return False

def isPartCONDValid(toCheck):
    lastindex = str.__len__(toCheck) - 1

    if (lastindex != -1):  # for "" AND X case!
        if (toCheck[0] == '('):
            if (toCheck[lastindex] == ')'):
                updatedCond = cleanSpaces(toCheck[1:lastindex])
                return isConditionValid(updatedCond)

    return False

def isConditionValid(toCheck):
    return (isSimple_CondValid(toCheck) or isCondANDcondValid(toCheck)
            or isCondORcondValid(toCheck) or isPartCONDValid(toCheck))
# -----------------------------------------------------------------------------------------------------------------------

def activeRule(operatorList, selectedRuleToActive):
    print("Before:", end="")
    printExpression(operatorList)
    if selectedRuleToActive == 1 or selectedRuleToActive == "1":
        print("Rule4:")
        Rule4(operatorList)
    elif selectedRuleToActive == 2 or selectedRuleToActive == "2":
        print("Rule4a:")
        Rule4a(operatorList)
    elif selectedRuleToActive == 3 or selectedRuleToActive == "3":
        print("Rule6:")
        Rule6(operatorList)
    elif selectedRuleToActive == 4 or selectedRuleToActive == "4":
        print("Rule6a:")
        Rule6a(operatorList)
    elif selectedRuleToActive == 5 or selectedRuleToActive == "5":
        print("Rule5a:")
        Rule5a(operatorList)
    elif selectedRuleToActive == 6 or selectedRuleToActive == "6":
        print("Rule11b:")
        Rule11b(operatorList)
    elif (True):
        print("invalid input, no rule was activated")

    print("after:", end="")
    printExpression(operatorList)
    print("************************************")

def partOne(operatorList):
    print(
        "1 - rule4" + "\n" +
        "2 - rule4a" + "\n" +
        "3 - rule6" + "\n" +
        "4 - rule6a" + "\n" +
        '5 - rule5' + "\n" +
        '6 - rule11b')
    selectedRuleToActive = input("Please select rule:\n")
    activeRule(operatorList, selectedRuleToActive)

def partTwo(operatorList):
    copy1 = copy.deepcopy(operatorList)  # make a deep copy of operatorList
    copy2 = copy.deepcopy(operatorList)
    copy3 = copy.deepcopy(operatorList)
    copy4 = copy.deepcopy(operatorList)
    print("Expression 1:")
    active10RandomRules(copy1)
    print("Expression 2:")
    active10RandomRules(copy2)
    print("Expression 3:")
    active10RandomRules(copy3)
    print("Expression 4:")
    active10RandomRules(copy4)
    printFinalExpressions(operatorList, copy1, copy2, copy3, copy4)
    return copy1, copy2, copy3, copy4

def printFinalExpressions(operatorList, copy1, copy2, copy3, copy4):
    print("Original expression: ", end="")
    printExpression(operatorList)
    print("Four Expressions after 10 random rules")
    print("Expression 1: ", end="")
    printExpression(copy1)
    print("Expression 2: ", end="")
    printExpression(copy2)
    print("Expression 3: ", end="")
    printExpression(copy3)
    print("Expression 4: ", end="")
    printExpression(copy4)

def active10RandomRules(operatorList):
    for i in range(10):
        print("step " + (i + 1).__str__())
        randNum = random.randint(1, 6)
        activeRule(operatorList, randNum)

def afterCartesianOrNJoin(operator, rTableAfterAll, sTableAfterAll):
    if isinstance(operator, Cartesian):
        print("*")
        return sizeEstimationCartesian(rTableAfterAll, sTableAfterAll)
    if isinstance(operator, NJoin):
        print("*")
        return sizeEstimationNJoin(rTableAfterAll, sTableAfterAll)

def initializeFirstAndSecondTable(reversedList, schemaR, schemaS):
    rTableAfterAll = schemaR
    sTableAfterAll = schemaS
    index = 0
    operator = reversedList[index]
    lastUpdated = None

    while operator != Cartesian or operator != NJoin:
        operator = reversedList[index]

        if isinstance(operator, Sigma):
            if operator.getTables().__contains__("R"):
                rTableAfterAll = sizeEstimationSigma(schemaR, operator.getDescription())
                lastUpdated = "r"
            elif operator.getTables().__contains__("S"):
                sTableAfterAll = sizeEstimationSigma(schemaS, operator.getDescription())
                lastUpdated = "s"
            else: # not "S" and not "R" then have to be some shirshor from previous size estimation
                if lastUpdated == "s":
                    print("*")
                    sTableAfterAll = sizeEstimationSigma(sTableAfterAll, operator.getDescription())
                elif lastUpdated == "r":
                     rTableAfterAll = sizeEstimationSigma(rTableAfterAll, operator.getDescription())

                 lastUpdated = None
        if isinstance(operator, Pi):
            if operator.getTables().__contains__("R"):
                rTableAfterAll = sizeEstimationPi(schemaR, operator.getDescription())
                lastUpdated = "r"
            elif operator.getTables().__contains__("S"):
                sTableAfterAll = sizeEstimationPi(schemaS, operator.getDescription())
                lastUpdated = "s"
            else:  # not "S" and not "R" then have to be some shirshor from previous size estimation
                if lastUpdated == "s":
                    print("*")
                    sTableAfterAll = sizeEstimationPi(sTableAfterAll, operator.getDescription())
                elif lastUpdated == "r":
                    print("*")
                    rTableAfterAll = sizeEstimationPi(rTableAfterAll, operator.getDescription())
                lastUpdated = None

        index += 1

    return afterCartesianOrNJoin(operator[index], rTableAfterAll, sTableAfterAll)

def partThree(operatorList):
    reversedList = reverseTheList(operatorList)
    fileLines = openAndReadFile()
    schemaR = makeSchemaR(fileLines)
    schemaS = makeSchemaS(fileLines)
    finalTable = initializeFirstAndSecondTable(reversedList, schemaR, schemaS)


    for operator in reversedList:
        if isinstance(operator, Cartesian):
            schemaAfterCartesian = sizeEstimationCartesian(schemaR, schemaS)
        elif isinstance(operator, Sigma):
            schemaAfterSigma = sizeEstimationSigma(schemaAfterCartesian, operator.getDescription())
        elif isinstance(operator, Pi):
            sizeEstimationPi(schema, operator.getDescription())
        # elif isinstance(operator, NJoin):
        #    sizeEstimationNJoin()

#(R.E = S.E AND R.D = S.D) AND (R.I = S.I)
def recForCalculateSigma(schemaAfterSigma, cond):
    if isSimple_CondValid(cond):
        return simpleCondSizeEstimation(schemaAfterSigma, cond) #get prob
    else:
        condAsList = [cond]
        condToSplit = getOnePredicateThatContainsAndRemoveFromList(condAsList)
        firstCond, secCond = splitANDorORCond(condToSplit)
        return recForCalculateSigma(schemaAfterSigma, firstCond) * recForCalculateSigma(schemaAfterSigma, secCond)

def sizeEstimationSigma(schema, cond):
    printBeforeSigma(schema)
    schemaAfterSigma = copy.deepcopy(schema)
    prob = recForCalculateSigma(schemaAfterSigma, cond)
    schemaAfterSigma.numOfRows = int(prob * schemaAfterSigma.numOfRows)
    printAfterSigma(schemaAfterSigma)
    return schemaAfterSigma

def simpleCondSizeEstimation(schemaAfterSigma, simpleCond):
    numOfAttributes = simpleCond.count(".")
    if(numOfAttributes == 0):
        return condWithOutAttribute(schemaAfterSigma, simpleCond)
    elif((numOfAttributes == 1)):
        return condWithOneAttribute(schemaAfterSigma, simpleCond)
    elif((numOfAttributes) == 2):
        return condWithTwoAttribute(schemaAfterSigma, simpleCond)

def condWithOutAttribute(schemaAfterSigma, simpleCond):
    splited = str.split(simpleCond, "=", 1)
    splited[0] = int(cleanSpaces(splited[0]))
    splited[1] = int(cleanSpaces(splited[1]))
    if(splited[0] == splited[1]):
        return 1
    else:
        return 0

def getTableAndAttributeName(expr):
    tableName = getTableFromCond(expr)
    attributeName = getAttributeFromCond(expr)
    return tableName, attributeName

def condWithTwoAttribute(schemaAfterSigma, simplecond):
    splited = str.split(simplecond, "=", 1)
    splited[0] = cleanSpaces(splited[0])
    splited[1] = cleanSpaces(splited[1])
    tableName1, attributeName1 = getTableAndAttributeName(splited[0])
    tableName2, attributeName2 = getTableAndAttributeName(splited[1])
    if(tableName1 == tableName2 and attributeName1 == attributeName2):
        return 1
    numOfValuesInAttribute1 = getNumOfValues(schemaAfterSigma, attributeName1, tableName1)
    numOfValuesInAttribute2 = getNumOfValues(schemaAfterSigma, attributeName2, tableName2)
    maxNumOfValues = max(numOfValuesInAttribute1, numOfValuesInAttribute2)
    return (1 / maxNumOfValues)

def condISFalse(simplecond):
    splited = str.split(simplecond, "=", 1)
    splited[0] = int(cleanSpaces(splited[0]))
    splited[1] = int(cleanSpaces(splited[1]))
    return not splited[0] == splited[1]

def condWithOneAttribute(schemaAfterSigma, simplecond):
    attributeName = getAttributeFromCond(simplecond)
    tableName = getTableFromCond(simplecond)
    return (1 / getNumOfValues(schemaAfterSigma, attributeName, tableName))

def getNumOfValues(schemaAfterSigma, attribute, table):
    res = None
    if(attribute == "A"):
        res = schemaAfterSigma.numOfValuesInA
    elif(attribute == "B"):
        res = schemaAfterSigma.numOfValuesInB
    elif(attribute == "C"):
        res = schemaAfterSigma.numOfValuesInC
    elif(attribute == "D"):
        res = schemaAfterSigma.numOfValuesInD
    elif(attribute == "E"):
        res = schemaAfterSigma.numOfValuesInE
    elif(attribute == "F"):
        res = schemaAfterSigma.numOfValuesInF
    elif(attribute == "H"):
        res = schemaAfterSigma.numOfValuesInH
    elif(attribute == "I"):
        res = schemaAfterSigma.numOfValuesInI
    if (res == 0):
        attribute = table + attribute
        if(attribute == "RD"):
            res = schemaAfterSigma.numOfValuesInRD
        elif (attribute == "SD"):
            res = schemaAfterSigma.numOfValuesInSD
        elif(attribute == "RE"):
            res = schemaAfterSigma.numOfValuesInRE
        elif(attribute == "SE"):
            res = schemaAfterSigma.numOfValuesInSE
    return res

def getAttributeFromCond(simplecond):
    attributeIndex = simplecond.find(".") + 1
    return simplecond[attributeIndex]

def getTableFromCond(simplecond):
    tableIndex = simplecond.find(".") - 1
    return simplecond[tableIndex]

def printBeforeSigma(schema1):
    print("input: n_schema1 " + str(schema1.numOfRows) + " r_schema1 " + str(schema1.sizeOfRow))

def printAfterSigma(schemaAfterSigma):
    print("output: n_newSchema " + str(schemaAfterSigma.numOfRows) + " r_newSchema " + str(schemaAfterSigma.sizeOfRow))

def sizeEstimationCartesian(schema1, schema2):
    printBeforeCartesian(schema1, schema2)
    schemaAfterCartesian = TableData()
    schemaAfterCartesian.numOfRows = schema1.numOfRows * schema2.numOfRows
    schemaAfterCartesian.sizeOfRow = schema1.sizeOfRow + schema2.sizeOfRow
    schemaAfterCartesian.numOfValuesInA = updateAttributeCartesian(schema1.numOfValuesInA, schema2.numOfValuesInA)
    schemaAfterCartesian.numOfValuesInB = updateAttributeCartesian(schema1.numOfValuesInB, schema2.numOfValuesInB)
    schemaAfterCartesian.numOfValuesInC = updateAttributeCartesian(schema1.numOfValuesInC, schema2.numOfValuesInC)
    schemaAfterCartesian.numOfValuesInD = updateAttributeCartesian(schema1.numOfValuesInD, schema2.numOfValuesInD)
    schemaAfterCartesian.numOfValuesInE = updateAttributeCartesian(schema1.numOfValuesInE, schema2.numOfValuesInE)
    schemaAfterCartesian.numOfValuesInF = updateAttributeCartesian(schema1.numOfValuesInF, schema2.numOfValuesInF)
    schemaAfterCartesian.numOfValuesInH = updateAttributeCartesian(schema1.numOfValuesInH, schema2.numOfValuesInH)
    schemaAfterCartesian.numOfValuesInI = updateAttributeCartesian(schema1.numOfValuesInI, schema2.numOfValuesInI)
    schemaAfterCartesian.numOfValuesInRD = updateSharedAttributeCartesian(schema1.numOfValuesInD, schema2.numOfValuesInD)
    schemaAfterCartesian.numOfValuesInSD = updateSharedAttributeCartesian(schema1.numOfValuesInD, schema2.numOfValuesInD)
    schemaAfterCartesian.numOfValuesInRE = updateSharedAttributeCartesian(schema1.numOfValuesInE, schema2.numOfValuesInE)
    schemaAfterCartesian.numOfValuesInSE = updateSharedAttributeCartesian(schema1.numOfValuesInE, schema2.numOfValuesInE)
    printAfterCartesian(schemaAfterCartesian)
    return schemaAfterCartesian

def printBeforeCartesian(schema1, schema2):
    print("input: n_schema1 " + str(schema1.numOfRows) + " n_schema2 " + str(schema2.numOfRows) + " r_schema1 " + str(schema1.sizeOfRow) + " r_schema2 " + str(schema2.sizeOfRow))

def printAfterCartesian(schemaAfterCartesian):
    print("output: n_newSchema " + str(schemaAfterCartesian.numOfRows) + " r_newSchema " + str(schemaAfterCartesian.sizeOfRow))

def updateAttributeCartesian(schema1Value, schema2Value):
    if (schema1Value == 0):
        return schema2Value
    elif (schema2Value == 0):
        return schema1Value
    return 0

def updateSharedAttributeCartesian(schema1Value, schema2Value):
    if (schema1Value > 0 and schema2Value > 0):
        return schema1Value * schema2Value
    return 0

def openAndReadFile():
    statisticsFile = open("statistics.txt", "r")
    lines = statisticsFile.read().splitlines()
    for line in lines:
        line.rstrip('\n')
    return lines

def reverseTheList(operatorList):
    reversedList = copy.deepcopy(operatorList)
    list.reverse(reversedList)
    return reversedList

def makeSchemaR(lines):
    schemaR = TableData()
    schemaR.numOfRows = getValueAfterEqual(lines[2])
    schemaR.sizeOfRow = 5 * 4
    schemaR.numOfValuesInA = getValueAfterEqual(lines[3])
    schemaR.numOfValuesInB = getValueAfterEqual(lines[4])
    schemaR.numOfValuesInC = getValueAfterEqual(lines[5])
    schemaR.numOfValuesInD = getValueAfterEqual(lines[6])
    schemaR.numOfValuesInE = getValueAfterEqual(lines[7])
    return schemaR

def makeSchemaS(lines):
    schemaS = TableData()
    schemaS.numOfRows = getValueAfterEqual(lines[11])
    schemaS.sizeOfRow = 5 * 4
    schemaS.numOfValuesInD = getValueAfterEqual(lines[12])
    schemaS.numOfValuesInE = getValueAfterEqual(lines[13])
    schemaS.numOfValuesInF = getValueAfterEqual(lines[14])
    schemaS.numOfValuesInH = getValueAfterEqual(lines[15])
    schemaS.numOfValuesInI = getValueAfterEqual(lines[16])
    return schemaS

def getValueAfterEqual(line):
    equalIndex = line.find("=") + 1
    return int(line[equalIndex:])

def sizeEstimationPi(schema, attributes):   #PI[RD]
    newSchema = TableData()
    listOfAttributes = str.split(simplecond, ",")
    for currAttribute in listOfAttributes:
        currAttribute = cleanSpaces(currAttribute)
        tableName, attributeName = getTableAndAttributeName(currAttribute)
        currNumOfValue = getNumOfValues(schema, attributeName, tableName)
        if (currNumOfValue != 0):
            updateNumOfValues(newSchema, attributeName, tableName, currNumOfValue)

def updateNumOfValues(newSchema, attribute, tableName, currNumOfValue):
    if(attribute == "A"):
        newSchema.numOfValuesInA = currNumOfValue
    elif(attribute == "B"):
        newSchema.numOfValuesInB = currNumOfValue
    elif(attribute == "C"):
        newSchema.numOfValuesInC = currNumOfValue
    elif(attribute == "D"):
        if(newSchema.numOfValuesInD != 0):
            if(tableName == "R"):
                newSchema.numOfValuesInRD = currNumOfValue
                newSchema.numOfValuesInSD = newSchema.numOfValuesInD
                newSchema.numOfValuesInD = 0
            elif(tableName == "S"):
                newSchema.numOfValuesInSD = currNumOfValue
                newSchema.numOfValuesInRD = newSchema.numOfValuesInD
                newSchema.numOfValuesInD = 0

        newSchema.numOfValuesInD = currNumOfValue

    elif(attribute == "E"):
        if(newSchema.numOfValuesInE != 0):
            if(tableName == "R"):
                newSchema.numOfValuesInRE = currNumOfValue
                newSchema.numOfValuesInSE = newSchema.numOfValuesInE
                newSchema.numOfValuesInE = 0
            elif(tableName == "S"):
                newSchema.numOfValuesInSE = currNumOfValue
                newSchema.numOfValuesInRE = newSchema.numOfValuesInE
                newSchema.numOfValuesInE = 0

        newSchema.numOfValuesInE = currNumOfValue

    elif(attribute == "F"):
        newSchema.numOfValuesInF = currNumOfValue
    elif(attribute == "H"):
        newSchema.numOfValuesInH = currNumOfValue
    elif(attribute == "I"):
        newSchema.numOfValuesInI = currNumOfValue

#todo cond with and && or
#todo Cartesian shared attributes, D,E
#todo work flow of query. (which schema to send next)

if __name__ == '__main__':
    queryInput = input("Please enter query (must contain SELECT, FROM, WHERE):\n")
    operatorList = makeExpression(queryInput)
    printExpression(operatorList)
    #copyForPartOne = copy.deepcopy(operatorList)  # make a deep copy of operatorList
    #copyForPartTwo = copy.deepcopy(operatorList)
    #partOne(copyForPartOne)
    #copy1, copy2, copy3, copy4 = partTwo(copyForPartTwo)
    #partThree(copy1, copy2, copy3, copy4)
    partThree(operatorList)