import random
import numpy as np

def neuralNetwork(inputs, matrix):
    return neuralNetworkNumpy(inputs, matrix)

#Just really simple matrix multiplication
def neuralNetworkNumpy( inputList, inputMatrix ):
    if ( len(inputList.shape) != 1):
        raise Exception("Invalid input list")
#    print "Array: " + str(inputMatrix)
    if ( len(inputMatrix.shape) > 1 and inputMatrix.shape[1] != inputList.shape[0]):
        raise Exception("Invalid matrix") #This is critical, if the collumns of the row and length of the input dont match, our math doesnt work
    result = np.matmul(inputMatrix, inputList)

    return (np.sum(result) % 8) + 1 #Processing output for external consumption


def evolve(inputMatrix):
    changedLayer = random.randint(0, inputMatrix.shape[0])
    changedElement = random.randint(0, inputMatrix.shape[1] - 1)
    changedAmount = random.random() - 0.5

#    print "\nMatrix Shape: " + str(inputMatrix.shape)
#    print "\nchanged Element: " + str(changedElement)
#    print "\nchanged Layer: " + str(changedLayer)
#    print inputMatrix

    if ( changedLayer == inputMatrix.shape[0] ): #Chance of adding row to matrix
        if (changedElement % 3 == 0 and changedAmount > 0.49): # Makes it slightly less likely for new rows to be added. Can and probably should be tweaked
            addedRow = np.zeros(inputMatrix.shape[1])
            addedRow[changedElement] = abs(changedAmount)
            inputMatrix = np.vstack([inputMatrix, addedRow]) #append row to bottom of matrix
#        print inputMatrix.shape
            return inputMatrix
        changedLayer -= 1

    inputMatrix[changedLayer,changedElement] = changedAmount
    inputMatrix[changedLayer,changedElement] = abs(inputMatrix[changedLayer,changedElement]) #Probably a more elegant way of doing this

    return inputMatrix
