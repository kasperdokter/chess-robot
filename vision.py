import numpy as np
import cv2
from matplotlib import pyplot as plt

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
    ret,thresh = cv2.threshold(diff,27,255,cv2.THRESH_BINARY_INV)

    # Remove all small blobs via erosion followed by dilation (opening).
    #kernel = np.ones((25,25),np.uint8)
    #opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    
    # Set up the parameters of a SimpleBlobdetector.
    params = cv2.SimpleBlobDetector_Params()
    #params.minThreshold = 0;
    #params.maxThreshold = 256;
    params.filterByArea = False
    #params.minArea = 0.8
    params.filterByCircularity = False
    #params.minCircularity = 0
    params.filterByConvexity = False
    params.filterByInertia = False
    #params.minInertiaRatio = 0
    
    # Set up the SimpleBlobdetector.
    detector = cv2.SimpleBlobDetector_create(params)
    
    show(thresh)
 
    # Detect blobs.
    keypoints = detector.detect(thresh)
    
    print(keypoints)
    
    # Draw detected blobs as red circles.
    # cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS ensures the size of the circle corresponds to the size of blob
    im_with_keypoints = cv2.drawKeypoints(img2, keypoints, np.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
 
    # Show keypoints
    show(im_with_keypoints)
    return

print("Reading images...")
img1 = cv2.imread('pic/pic0.jpg')
img2 = cv2.imread('pic/pic1.jpg')

print("Detecting move")
detectMove(img1, img2)

 