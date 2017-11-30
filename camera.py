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
    
    def save(self,name):
        """
            Saves all pictures to disk.
        """
        for k, img in enumerate(self.L):
            cv2.imwrite(name + str(k) + ".jpg", img)
        return
        
    def picture(self):
        """
            Takes a picture, appends it to the list.
        """
        print("Taking picture...")
        with picamera.PiCamera() as camera:
            rawCapture = picamera.array.PiRGBArray(camera)
            time.sleep(self.t)
            camera.capture(rawCapture, format='bgr')
            img = rawCapture.array
            self.L.append(img)
        return
       
    def changes(self):
        """
            Computes a list of squares that changes between the last two images in the list.
        """
       
        print(cv2.__version__) 
        # Convert to gray scale
        img1, img2 = self.L[:2]
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
        k = 35
        blur_img1 = cv2.blur(img1_gray,(k,k))
        blur_img3 = cv2.blur(img3_gray,(k,k))
        
        # Take the absolute difference of the these images
        diff = cv2.absdiff(blur_img1,blur_img3)
        
        # Transform the gray scale difference to black and white via threshholding
        ret,thresh = cv2.threshold(diff,50,255,cv2.THRESH_BINARY)
        
        # Iterate over the usual locations of the squares to find what changed
        squares = []
        for x in range(8):
           for y in range(8):
              mask = np.zeros(thresh.shape, np.uint8)
              mask = cv2.circle(mask, (485+2040*x/7+10*y/7,300+2040*y/7), 150, 255, -1)
              m = cv2.mean(thresh, mask)
              if (m[0] > 5):
                  squares.append((8-x,y))   
        
        return squares
