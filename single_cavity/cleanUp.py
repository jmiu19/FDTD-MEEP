import glob
import os


fileLists = ['./*.h5',
             './*.out',
             './*.png',
             './*.csv',
             './output/*.csv',
             './output/*.png',
             './output/*.dat',
             './output/fluxPlt/*.png',
             './output/resonancePlt/*.png',
             './output/animation/*.mp4',
             './output/*.out']

for name in fileLists:
    fileList = glob.glob(name)
    if len(fileList) == 0 :
        print('no '+name[-3:]+' file')
    else :
        for file in fileList :
            os.remove(file)
            print(file+' removed')
