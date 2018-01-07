from __future__ import print_function 
from __future__ import division

import io
import cv2
import time
import picamera
import picamera.array
import numpy as np

class Camera:
    
    # List of pictures
    L = []

    # Time to wait before taking picture
    t = 0.5

    # Color of dots
    h = 55

    # Threshold for piece detection
    th = 30

    def save(self,name):
        """
            Saves all pictures to disk.
        """
        for k, img in enumerate(self.L):
            cv2.imwrite(name + format(k, '03') + ".jpg", cv2.cvtColor(img,cv2.COLOR_BGR2RGB))
        return
        
    def picture(self):
        """
            Takes a picture, appends it to the list.
        """
        with picamera.PiCamera() as camera:
            rawCapture = picamera.array.PiRGBArray(camera)
            time.sleep(self.t)
            camera.capture(rawCapture, format='bgr')
            img = rawCapture.array
            self.show(img)
            warp = self.warp(img)
            gray = cv2.cvtColor(warp,cv2.COLOR_BGR2GRAY)
            blur = cv2.blur(gray,(5,5))
            self.show(blur)
            self.L.append(blur)
        return
       
    def show(self,img):
        cv2.namedWindow('image', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('image', 400,400)
        cv2.imshow('image', img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        return

    def changes(self):
        """
            Computes a list of squares that changes between the last two images in the list.
        """
        
        # Take the absolute difference of the these images
        diff = cv2.absdiff(self.L[-1],self.L[-2])
        
        # Transform the gray scale difference to black and white via thresholding
        ret,thresh = cv2.threshold(diff,self.th,255,cv2.THRESH_BINARY)
        
        self.show(thresh)

        # Iterate over the usual locations of the squares to find what changed
        squares = []
        for x in range(8):
            for y in range(8):
                mask = np.zeros((400,400), np.uint8)
                cv2.rectangle(mask, (50*x,50*y), (50*(x+1),50*(y+1)), 255, -1)
                m = cv2.mean(thresh, mask)
                print(x,y,m[0])
                if (m[0] > 5):
                    squares.append((x,y))    
        
        if len(squares) > 2:
            self.show(thresh)
        
        return squares
        
    def changes1(self):
        """
            Computes a list of squares that changes between the last two images in the list.
        """
        
        # Convert to gray scale
        img1, img2 = self.L[-2:]
        img1_gray = cv2.cvtColor(img1,cv2.COLOR_BGR2GRAY)
        img2_gray = cv2.cvtColor(img2,cv2.COLOR_BGR2GRAY)

        # Initiate STAR detector
        orb = cv2.ORB()

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
        good = matches[:80]

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
        k = 5
        blur_img1 = cv2.blur(img1_gray,(k,k))
        blur_img3 = cv2.blur(img3_gray,(k,k))
        
        # Take the absolute difference of the these images
        diff = cv2.absdiff(blur_img1,blur_img3)
        
        # Transform the gray scale difference to black and white via threshholding
        ret,thresh = cv2.threshold(diff,25,255,cv2.THRESH_BINARY)

        # Warp the thresholded image onto a square
        pts2 = np.float32([[0,0],[400,0],[0,400],[400,400]])
        pts1 = np.float32([[595,20],[145,13],[600,500],[115,485]])
        M = cv2.getPerspectiveTransform(pts1,pts2)
        square = cv2.warpPerspective(thresh,M,(400,400))
        sq1 = cv2.warpPerspective(img2_gray,M,(400,400))	

        self.show(sq1)
        #self.show(square)

        # Iterate over the usual locations of the squares to find what changed
        squares = []
        for x in range(8):
            for y in range(8):
                mask = np.zeros((400,400), np.uint8)
                cv2.rectangle(mask, (50*x,50*y), (50*(x+1),50*(y+1)), 255, -1)
                m = cv2.mean(square, mask)
                if (m[0] > 5):
                    squares.append((x,y))    
        
        if len(squares) > 2:
            self.show(square)
        
        return squares
        
    def getBlobs(self,img):
        # Convert BGR to HSV
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # Define range of marker color in HSV
        lower = np.array([self.h-10,50,50])
        upper = np.array([self.h+10,255,255])
        
        # Threshold the HSV image to get only marker colors
        blobs = cv2.inRange(hsv, lower, upper)
        
        # Remove noise
        k = 3
        kernel = np.ones((k,k),np.uint8)
        blobs = cv2.morphologyEx(blobs, cv2.MORPH_OPEN, kernel)
        
        # Close the holes
        k = 3
        kernel = np.ones((k,k),np.uint8)
        blobs = cv2.morphologyEx(blobs, cv2.MORPH_CLOSE, kernel)
        
        # Invert black and white
        blobs = cv2.bitwise_not(blobs)    
        self.show(blobs)
        return blobs
        
    def getKeyPoints(self,blob):
        # Setup SimpleBlobDetector parameters.
        params = cv2.SimpleBlobDetector_Params()
        
        #params.minThreshold = 10;
        #params.maxThreshold = 200;
        #params.filterByArea = True
        #params.minArea = 1500
        params.filterByCircularity = False
        #params.minCircularity = 0.1
        params.filterByConvexity = False
        #params.minConvexity = 0.87
        params.filterByInertia = False
        #params.minInertiaRatio = 0.01
         
        # Create a detector with the parameters
        ver = (cv2.__version__).split('.')
        if int(ver[0]) < 3 :
            detector = cv2.SimpleBlobDetector(params)
        else : 
            detector = cv2.SimpleBlobDetector_create(params)
            
        # Detect blobs.
        return detector.detect(blob)

    def order(self,keypoints):
        pts = [k.pt for k in keypoints]    
        rect = np.zeros((4, 2), dtype = "float32")

        s = [x+y for (x,y) in pts]
        rect[1] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]

        d = [x-y for (x,y) in pts]
        rect[3] = pts[np.argmin(d)]
        rect[0] = pts[np.argmax(d)]

        return rect
        
    def warp(self,img):
        # Find the green stickers
        blob = self.getBlobs(img)

        # Calculate the key points
        keypoints = self.getKeyPoints(blob)
        
        # Calculate the perspective transform
        pts1 = self.order(keypoints)
        pts2 = np.float32([[-28,22],[428,22],[-29,375],[426,373]])
        M = cv2.getPerspectiveTransform(pts1,pts2)
        
        return cv2.warpPerspective(img,M,(400,400))
