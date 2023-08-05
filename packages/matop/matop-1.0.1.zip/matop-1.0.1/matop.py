"""this is a module called matop and it provides four functions matadd, matsub,
matmult and matprint to add, subtract and multiply matrices"""

def matadd (mat1,mat2):

    '''this function takes two arguments matrix one and matrix two which are to
    be added, these matrices are just the list of the colomns of the matrix ,
    which in turn are lists containing elements of one colomn of a matrix.the
    function returns the answer in the same format.''' 

    if len(mat1)==len(mat2):
        var = [0,0]
        if isinstance (mat1[0],int):
            var[0] = 1
        else:
            var[0] = len(mat1[0])
        if isinstance (mat2[0],int):
            var[1] = 1
        else:
            var[1] = len(mat2[0])
        if var[0]==var[1]:
            matres = [None]*len(mat1)
            for i in range(len(mat1)):
                matres[i]=[0]*var[0]
            for lvl1 in range(len(mat1)):
                for lvl2 in range(var[0]):
                    matres[lvl1][lvl2]=mat1[lvl1][lvl2]+mat2[lvl1][lvl2]
            return matres
        else:
            print ("invalid matrix operation")
    else:
        print ("invalid matrix operation")
    

def matsub (mat1,mat2):

    '''this function takes two arguments matrix one and matrix two which are to
    be subtracted, these matrices are just the list of the colomns of the matrix ,
    which in turn are lists containing elements of one colomn of a matrix.the
    function returns the answer in the same format.'''

    if len(mat1)==len(mat2):
        var = [0,0]
        if isinstance (mat1[0],int):
            var[0] = 1
        else:
            var[0] = len(mat1[0])
        if isinstance (mat2[0],int):
            var[1] = 1
        else:
            var[1] = len(mat2[0])
        if var[0]==var[1]:
            matres = [None]*len(mat1)
            for i in range(len(mat1)):
                matres[i]=[0]*var[0]
            for lvl1 in range(len(mat1)):
                for lvl2 in range(var[0]):
                    matres[lvl1][lvl2]=mat1[lvl1][lvl2]-mat2[lvl1][lvl2]
            return matres
        else:
            print ("invalid matrix operation")
    else:
        print ("invalid matrix operation")
    

def matmult (mat1,mat2):

    '''this function takes two arguments matrix one and matrix two which are to
    be multiplied, these matrices are just the list of the colomns of the matrix ,
    which in turn are lists containing elements of one colomn of a matrix.the
    function returns the answer in the same format.'''

    var = [0,0]
    if isinstance (mat1[0],int):
        var[0] = 1
    else:
        var[0] = len(mat1[0])
    if isinstance (mat2[0],int):
        var[1] = 1
    else:
        var[1] = len(mat2[0])
 
    if len(mat1)==var[1]:
        if var[0]==1:
            matres = [0] * len(mat2)
        else:
            matres = [None] * len(mat2)
            for i in range(len(mat2)):
                matres[i]=[0]* var[0] 
        for lvl1 in range(len(mat2)):
            for lvl2 in range(var[0]):
               for lvl3 in range(len(mat1)):
                   if (var[1] == 1)and(var[0]!=1):
                       matres[lvl1][lvl2] = (mat1[0][lvl2]*mat2[lvl1])
                   if (var[0] == 1)and(var[1]!=1):
                       matres[lvl1] = matres [lvl1]+(mat1[lvl3]*mat2[lvl1][lvl3])
                   if (var[1] == 1)and(var[0]==1):
                       matres[lvl1] = matres[lvl1]+(mat1[0]*mat2[lvl1])
                   if (var[0]!=1)and((var[1]!=1)):
                       matres[lvl1][lvl2] = matres[lvl1][lvl2]+(mat1[lvl3][lvl2]*mat2[lvl1][lvl3])
        return matres
    else:
        print ("invalid matrix operation")


def matprint (mat):

    '''this functin takes a matrix as an argument which is just the list of the
    colomns of the matrix ,which in turn are lists containing elements of one
    colomn of a matrix.it then prints the matrix in a readable format'''

    if isinstance (mat[0],int):
        for i in range(len(mat)):
            print(mat[i],end='')
            print("\t",end='')
        print("")
    else:
        for lvl1 in range(len(mat[0])):
            for lvl2 in range (len(mat)):
                print(mat[lvl2][lvl1],end='')
                print("\t",end='')
                print(" ")
        
