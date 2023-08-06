# This is a test comment
def printList(theList, indentOn = False, level = 0):
    # This is another comment
    for item in theList:
        if (isinstance(item, list)):
            printList(item, indentOn, level + 1)
        else:
            if indentOn:
                for num in range(level):
                    print("\t", end='')
            print(item)

    
        
