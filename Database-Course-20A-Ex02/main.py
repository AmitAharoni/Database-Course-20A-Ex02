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
SELECT R.D,S.E FROM R,S WHERE S.D>4  AND R.A>10; // same as in example
SELECT R.D,S.E FROM R,S WHERE S.D=R.D  AND S.E=R.E;  // 11b example

SELECT R.C,S.F FROM S,R WHERE R.C=S.F AND S.F>1000; // run on example
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
            print(operatorsList[i].getOperatorName() + "[" + operatorsList[i].getDescription() + "]" + "(" +
                  operatorsList[i].getTables() + ")", end="")
        elif operatorsList[i].getDescription() is None and operatorsList[i].getTables() is not None:
            # Cartesian
            cartesianOrNjoin = operatorsList[i]

            if cartesianOrNjoin.isOperatorInFirst() and cartesianOrNjoin.isOperatorInSecond():
                firstSigma = operatorsList[i + 1]
                secondSigma = operatorsList[i + 2]
                print(
                    cartesianOrNjoin.getOperatorName() + "(" + firstSigma.getOperatorName() + "[" + firstSigma.getDescription() + "]" + "(" + firstSigma.getTables() + ")",
                    ",",
                    secondSigma.getOperatorName() + "[" + secondSigma.getDescription() + "]" + "(" + secondSigma.getTables() + "))",
                    end="")
                i += 2
            elif cartesianOrNjoin.isOperatorInFirst() and not cartesianOrNjoin.isOperatorInSecond():
                firstSigma = operatorsList[i + 1]
                print(
                    cartesianOrNjoin.getOperatorName() + "(" + firstSigma.getOperatorName() + "[" + firstSigma.getDescription() + "]" + "(" + firstSigma.getTables() + ")"
                    + cartesianOrNjoin.getTables() + ")", end="")
                i += 1
            elif not cartesianOrNjoin.isOperatorInFirst() and cartesianOrNjoin.isOperatorInSecond():
                secondSigma = operatorsList[i + 1]
                print(
                    cartesianOrNjoin.getOperatorName() + "(" + cartesianOrNjoin.getTables() + secondSigma.getOperatorName() + "[" + secondSigma.getDescription() + "]" + "(" + secondSigma.getTables() + "))",
                    end="")
                i += 1
            else:
                print(cartesianOrNjoin.getOperatorName() + "(" + operatorsList[i].getTables() + ")", end="")

        elif operatorsList[i].getDescription() is not None and operatorsList[i].getTables() is None:
            print(operatorsList[i].getOperatorName() + "[" + operatorsList[i].getDescription() + "]" + "(", end="")
        else:
            print(operatorsList[i].getOperatorName() + "(", end="")
        i += 1

    for i in range(
            operatorsList.__len__() - 1):  # operator.getDescription() is not None and operator.getTables() is not None close one paratensis
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
                if isinstance(operatorList[indexOfSigma + 1], Cartesian) or isinstance(operatorList[indexOfSigma + 1],
                                                                                       NJoin):
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


def isEveryCondOfPredicateContainEqualSign(predicate):
    allPredicate = [predicate]

    while oneOfCondInAllPredicateContainsBooleanAlgebra(allPredicate):
        condToSplit = getOnePredicateThatContainsAndRemoveFromList(allPredicate)
        firstCond, secCond = splitANDorORCond(condToSplit)
        allPredicate.append(firstCond)
        allPredicate.append(secCond)

    for cond in allPredicate:
        if not cond.__contains__("=") or not cond.__contains__("S") or not cond.__contains__("R"):
            return False

    return True


def Rule11b(operatorList):
    for operator in operatorList:
        if isinstance(operator, Sigma):
            indexOfSigma = operatorList.index(operator)
            if isEveryCondOfPredicateContainEqualSign(operator.getDescription()):
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


# def partThree(copy1, copy2, copy3, copy4):

def afterCartesianOrNJoin(operator, rTableAfterAll, sTableAfterAll):
    if isinstance(operator, Cartesian):
        #return sizeEstimationCartesian(rTableAfterAll, sTableAfterAll)
    if isinstance(operator, NJoin):
        #return sizeEstimationNJoin(rTableAfterAll, sTableAfterAll)



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
                #rTableAfterAll = sizeEstimationSigma(schemaR, operator.getDescription())
                lastUpdated = "r"
            elif operator.getTables().__contains__("S"):
                #sTableAfterAll = sizeEstimationSigma(schemaS, operator.getDescription())
                lastUpdated = "s"
            else: # not "S" and not "R" then have to be some shirshor from previous size estimation
                if lastUpdated == "s":
                    # sTableAfterAll = sizeEstimationSigma(sTableAfterAll, operator.getDescription())
                elif lastUpdated == "r":
                    # rTableAfterAll = sizeEstimationSigma(rTableAfterAll, operator.getDescription())

                 lastUpdated = None
        if isinstance(operator, Pi):
            if operator.getTables().__contains__("R"):
                # rTableAfterAll = sizeEstimationPi(schemaR, operator.getDescription())
                lastUpdated = "r"
            elif operator.getTables().__contains__("S"):
                # sTableAfterAll = sizeEstimationPi(schemaS, operator.getDescription())
                lastUpdated = "s"
            else:  # not "S" and not "R" then have to be some shirshor from previous size estimation
                if lastUpdated == "s":
                  # sTableAfterAll = sizeEstimationPi(sTableAfterAll, operator.getDescription())
                elif lastUpdated == "r":
                    # rTableAfterAll = sizeEstimationPi(rTableAfterAll, operator.getDescription())
                lastUpdated = None

        index += 1

    return afterCartesianOrNJoin(operator[index], rTableAfterAll, sTableAfterAll)


def partThree(operatorList):
    reversedList = reverseTheList(operatorList)
    fileLines = openAndReadFile()
    schemaR = makeSchemaR(fileLines)
    schemaS = makeSchemaS(fileLines)
    finalTable = None

    finalTable = initializeFirstAndSecondTable(reversedList, schemaR, schemaS)

    for operator in reversedList:
        if isinstance(operator, Cartesian):
             #schemaAfterCartesian = sizeEstimationCartesian(schemaR, schemaS)
    # elif isinstance(operator, Sigma):
    #    sizeEstimationSigma()
    # elif isinstance(operator, Pi):
    #    sizeEstimationPi()
    # elif isinstance(operator, NJoin):
    #    sizeEstimationNJoin()


def sizeEstimationCartesian():
    return True


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
    schemaR.schemeName = "R"
    schemaR.attributes = "A,B,C,D,E"
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
    schemaS.schemeName = "S"
    schemaS.attributes = "D,E,F,H,I"
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


# todo more checks on OR query
if __name__ == '__main__':
    queryInput = input("Please enter query (must contain SELECT, FROM, WHERE):\n")
    operatorList = makeExpression(queryInput)
    # copyForPartOne = copy.deepcopy(operatorList)  # make a deep copy of operatorList
    # copyForPartTwo = copy.deepcopy(operatorList)
    # partOne(copyForPartOne)
    # copy1, copy2, copy3, copy4 = partTwo(copyForPartTwo)
    # partThree(copy1, copy2, copy3, copy4)
    partThree(operatorList)
