
import cv2
import pytesseract


img='k.jpg'
gray='temp/grayscale.jpg'
thresh='temp/thresh.jpg'


def grayscale(img):
    readimg= cv2.imread(img)
    newimg= cv2.cvtColor(readimg, cv2.COLOR_BGR2GRAY )
    cv2.imshow("window", newimg)
    cv2.imwrite("temp/grayscale.jpg", newimg)


grayscale(img)


#this works best in gray image only
def threshold(img):
    readimg= cv2.imread(img)
    ret2, th2 = cv2.threshold(readimg, 0, 255, cv2.THRESH_BINARY)
    cv2.imwrite("temp/thresh.jpg", th2)

threshold(gray)  

#text extraction

def textu(img):
    readimg= cv2.imread(img)    
    text= pytesseract.image_to_string(readimg)
    print(text)



textu('temp/thresh.jpg')    