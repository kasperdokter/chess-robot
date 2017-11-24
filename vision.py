import numpy as np
import cv2
#import picamera
from matplotlib import pyplot as plt

#def pic():
#    stream = io.BytesIO()
#    with picamera.PiCamera() as camera:
#        camera.start_preview()
#        time.sleep(2)
#        camera.capture(stream, format='jpeg')
#    data = np.fromstring(stream.getvalue(), dtype=np.uint8)
#    img = cv2.imdecode(data, 1)
#    cv2.imshow('image', img)
#    cv2.waitkey(0)
#    cv2.destroyAllWindows()
#    return

def show(img):
   cv2.namedWindow('image', cv2.WINDOW_NORMAL)
   cv2.resizeWindow('image', 600, 700)
   cv2.imshow('image', img)
   cv2.waitKey(0)
   cv2.destroyAllWindows()
   return
   
def detectMove(img1, img2):
    """Detects a move by comparing two images. The first image captures 
    the initial position and the second image captures the position after
    the move.

    Args:
        img1 (numpy.ndarray): The first image.
        img2 (numpy.ndarray): The second image.

    Returns:
        string: textual representation of the move.
    """
    show(img1)
    show(img2)
    
    # Convert to gray scale
    img1_gray = cv2.cvtColor(img1,cv2.COLOR_BGR2GRAY)
    img2_gray = cv2.cvtColor(img2,cv2.COLOR_BGR2GRAY)
    
    # Initiate STAR detector
    orb = cv2.ORB_create()

    # Find the keypoints and descriptors with ORB
    kp1, des1 = orb.detectAndCompute(img2_gray,None)
    kp2, des2 = orb.detectAndCompute(img1_gray,None)

    # Create BFMatcher object
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

    # Match descriptors.
    matches = bf.match(des1,des2)

    # Sort them in the order of their distance.
    matches = sorted(matches, key = lambda x:x.distance)
    
    # Find the best matches.
    good = matches[:10]

    # Reformat the source and target points.
    src_pts = np.float32([ kp1[m.queryIdx].pt for m in good ]).reshape(-1,1,2)
    dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good ]).reshape(-1,1,2)

    # Compute the 3x3 transformation matrix.
    M, mask = cv2.findHomography(src_pts,dst_pts,cv2.RANSAC,5.0)

    # Get the size of the second image
    rows,cols = img2_gray.shape
    
    # Align the second image.
    img3_gray = cv2.warpPerspective(img2_gray, M, (cols, rows))
    
    # Blur the second image and the aligned version of the second image
    blur_img1 = cv2.blur(img1_gray,(45,45))
    blur_img3 = cv2.blur(img3_gray,(45,45))
    
    # Take the absolute difference of the these images
    diff = cv2.absdiff(blur_img1,blur_img3)
    
    # Transform the gray scale difference to black and white via threshholding
    ret,thresh = cv2.threshold(diff,27,255,cv2.THRESH_BINARY)
    
    show(thresh)
    
    squares = []
    for x in range(8):
       for y in range(8):
          mask = np.zeros(thresh.shape, np.uint8)
          mask = cv2.circle(mask, (900+1850*x/7-20*y/7,400+1840*y/7), 100, 255, -1)
          m = cv2.mean(thresh, mask)
          if (m[0] > 50):
              squares.append((x,y))   
              
    print(squares)
    
    return

print("Reading images...")
img1 = cv2.imread('pic.jpg')
img2 = cv2.imread('pic2.jpg')

print("Detecting move")
detectMove(img1, img2)

 