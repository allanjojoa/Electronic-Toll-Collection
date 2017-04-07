# Main.py
 
import cv2
import numpy as np
import os
import MySQLdb 
import time

import DetectChars
import DetectPlates
import PossiblePlate
 
# module level variables ##########################################################################
SCALAR_BLACK = (0.0, 0.0, 0.0)
SCALAR_WHITE = (255.0, 255.0, 255.0)
SCALAR_YELLOW = (0.0, 255.0, 255.0)
SCALAR_GREEN = (0.0, 255.0, 0.0)
SCALAR_RED = (0.0, 0.0, 255.0)
 
showSteps = False
plate='none'
###################################################################################################
def main(): 
    cap = cv2.VideoCapture(1)
    found=False
    try:
        os.remove("static/Found.png")
    except:
        print 'No file to Remove\n'

    print 'Detecting\n'
    while found==False:
        ret, filename= cap.read()
        plate=new_main(filename)
        found=os.path.exists("static/Found.png")
    print 'Found\n'


def new_main(filename):
 
    blnKNNTrainingSuccessful = DetectChars.loadKNNDataAndTrainKNN()         # attempt KNN training
 
    if blnKNNTrainingSuccessful == False:                               # if KNN training was not successful
        print "\nerror: KNN traning was not successful\n"               # show error message
        return                                                          # and exit program
    # end if
 
    imgOriginalScene  = filename
    imgOriginalScene=cv2.resize(imgOriginalScene, (640,470 ))
 
    """if imgOriginalScene is None:                            # if image was not read successfully
        print "\nerror: image not read from file \n\n"      # print error message to std out
        os.system("pause")                                  # pause so user can see error message
        return"""                                              # and exit program
    # end if
 
    listOfPossiblePlates = DetectPlates.detectPlatesInScene(imgOriginalScene)           # detect plates
 
    listOfPossiblePlates = DetectChars.detectCharsInPlates(listOfPossiblePlates)        # detect chars in plates
 
    #cv2.imshow("imgOriginalScene", imgOriginalScene)            # show scene image
 
    if len(listOfPossiblePlates) == 0:                          # if no plates were found
        #print "\nno license plates were detected\n"             # inform user no plates were found
        return
    else:                                                       # else
     if len(listOfPossiblePlates) > 0:      
                # if we get in here list of possible plates has at leat one plate
 
                # sort the list of possible plates in DESCENDING order (most number of chars to least number of chars)
        listOfPossiblePlates.sort(key = lambda possiblePlate: len(possiblePlate.strChars), reverse = True)
 
                # suppose the plate with the most recognized chars (the first plate in sorted by string length descending order) is the actual plate
        licPlate = listOfPossiblePlates[0]
        if len(listOfPossiblePlates) > 1:
         licPlate1 = listOfPossiblePlates[1]
 
        #cv2.imshow("imgPlate", licPlate.imgPlate)           # show crop of plate and threshold of plate
        #aaacv2.imshow("imgThresh", licPlate.imgThresh)
 
        if len(licPlate.strChars) == 0:                     # if no chars were found in the plate
            #print "\nno characters were detected\n\n"       # show message
            return                                          # and exit program
        # end if
 
        drawRedRectangleAroundPlate(imgOriginalScene, licPlate)             # draw red rectangle around plate
        licPlate_length=len(licPlate.strChars)
        if licPlate_length >6:
            s = list(licPlate.strChars)
            try:
               if s[0] == 'X':
                  s[0]='K'
               if s[2] == 'X':
                  s[2]='K'
               if s[3] == 'I':
                  s[3]='1'
               if s[6] == 'I':
                  s[6]='1'
               if s[7] == 'I':
                  s[7]='1'
               if licPlate_length > 8:
                  if s[8] == 'I':
                     s[8]='1'
               if licPlate_length >9:
                  if s[9] == 'I':
                     s[9] = 1
            except:
               print "Error"
            licPlate.strChars = ''.join(s)
            print "\nlicense plate read from image = " + licPlate.strChars + "\n"       # write license plate text to std out
            print "----------------------------------------"
            writeLicensePlateCharsOnImage(imgOriginalScene, licPlate)           # write license plate text on the image
        if len(licPlate.strChars) < 5:
         #if len(licPlate1.strChars) == 0:                                            # if no chars were found in the plate
            #print "\nno characters were detected\n\n"       # show message
            return                                          # and exit program
         # end if
 
        if len(listOfPossiblePlates) > 1:
         drawRedRectangleAroundPlate(imgOriginalScene, licPlate1)             # draw red rectangle around plate
         licPlate_length=len(licPlate1.strChars)
         if licPlate_length >1:
           print "\nlicense plate read from image = " + licPlate1.strChars + "\n"       # write license plate text to std out
           print "----------------------------------------"
           writeLicensePlateCharsOnImage(imgOriginalScene, licPlate1)
        if( len(listOfPossiblePlates) > 1) and (len(licPlate.strChars) < 7): 
         print "\nLicense Plate = " +licPlate1.strChars + licPlate.strChars + "\n"
        else:
         print "\nLicense Plate = " + licPlate.strChars + "\n"
        #cv2.imshow("imgOriginalScene", imgOriginalScene)                # re-show scene image
        if licPlate_length > 1:
            cv2.imwrite("static/imgOriginalScene.png", imgOriginalScene)          # write image out to file
            cv2.imwrite("static/Found.png", imgOriginalScene)
            plate=licPlate.strChars
            cv2.destroyAllWindows()
             
            #updating Database
            db = MySQLdb.connect("localhost","root","root","plate_information" )
            cursor = db.cursor()
            cursor.execute("SELECT * from plate_info")
            data = cursor.fetchall() 
            for row in data:
              if row[0]==plate:
                print "Plate Found In DB"
                time.sleep(5)
                due=row[5]
                due=due+10
                cursor.execute ("""UPDATE plate_info SET due=%s WHERE PLATE_NO=%s""", (due,plate))
                cursor.execute('''commit''')            
            db.close()
            return plate                
      # end if else 
    
 
    #cv2.waitKey(0)                 # hold windows open until user presses a key
    cv2.destroyAllWindows()
    return
# end main
 
###################################################################################################
def drawRedRectangleAroundPlate(imgOriginalScene, licPlate):
 
    p2fRectPoints = cv2.boxPoints(licPlate.rrLocationOfPlateInScene)            # get 4 vertices of rotated rect
 
    cv2.line(imgOriginalScene, tuple(p2fRectPoints[0]), tuple(p2fRectPoints[1]), SCALAR_RED, 2)         # draw 4 red lines
    cv2.line(imgOriginalScene, tuple(p2fRectPoints[1]), tuple(p2fRectPoints[2]), SCALAR_RED, 2)
    cv2.line(imgOriginalScene, tuple(p2fRectPoints[2]), tuple(p2fRectPoints[3]), SCALAR_RED, 2)
    cv2.line(imgOriginalScene, tuple(p2fRectPoints[3]), tuple(p2fRectPoints[0]), SCALAR_RED, 2)
# end function
 
###################################################################################################
def writeLicensePlateCharsOnImage(imgOriginalScene, licPlate):
    ptCenterOfTextAreaX = 0                             # this will be the center of the area the text will be written to
    ptCenterOfTextAreaY = 0
 
    ptLowerLeftTextOriginX = 0                          # this will be the bottom left of the area that the text will be written to
    ptLowerLeftTextOriginY = 0
 
    sceneHeight, sceneWidth, sceneNumChannels = imgOriginalScene.shape
    plateHeight, plateWidth, plateNumChannels = licPlate.imgPlate.shape
 
    intFontFace = cv2.FONT_HERSHEY_SIMPLEX                      # choose a plain jane font
    fltFontScale = float(plateHeight) / 30.0                    # base font scale on height of plate area
    intFontThickness = int(round(fltFontScale * 1.5))           # base font thickness on font scale
 
    textSize, baseline = cv2.getTextSize(licPlate.strChars, intFontFace, fltFontScale, intFontThickness)        # call getTextSize
 
            # unpack roatated rect into center point, width and height, and angle
    ( (intPlateCenterX, intPlateCenterY), (intPlateWidth, intPlateHeight), fltCorrectionAngleInDeg ) = licPlate.rrLocationOfPlateInScene
 
    intPlateCenterX = int(intPlateCenterX)              # make sure center is an integer
    intPlateCenterY = int(intPlateCenterY)
 
    ptCenterOfTextAreaX = int(intPlateCenterX)         # the horizontal location of the text area is the same as the plate
 
    if intPlateCenterY < (sceneHeight * 0.75):                                                  # if the license plate is in the upper 3/4 of the image
        ptCenterOfTextAreaY = int(round(intPlateCenterY)) + int(round(plateHeight * 1.6))      # write the chars in below the plate
    else:                                                                                       # else if the license plate is in the lower 1/4 of the image
        ptCenterOfTextAreaY = int(round(intPlateCenterY)) - int(round(plateHeight * 1.6))      # write the chars in above the plate
    # end if
 
    textSizeWidth, textSizeHeight = textSize                # unpack text size width and height
 
    ptLowerLeftTextOriginX = int(ptCenterOfTextAreaX - (textSizeWidth / 2))           # calculate the lower left origin of the text area
    ptLowerLeftTextOriginY = int(ptCenterOfTextAreaY + (textSizeHeight / 2))          # based on the text area center, width, and height
 
            # write the text on the image
    cv2.putText(imgOriginalScene, licPlate.strChars, (ptLowerLeftTextOriginX, ptLowerLeftTextOriginY), intFontFace, fltFontScale, SCALAR_YELLOW, intFontThickness)
# end function
 
###################################################################################################
if __name__ == "__main__":
    while True:
        main()
