import cv2
import numpy as np
import matplotlib.pyplot as plt
import math
from math import log10, atan2, cos, sin, sqrt
import os

src_line_list = [] # Source
dest_line_list = [] # Destination
dest2_line_list = [] # Destination2
result_images = []

warp_line_list_dest = []
warp_line_list_dest2 = []
count = 0
frame_count = 30

class CvPoint():
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Line:
    
    def PQ_to_MLA(self):
        M_x = (self.P.x + self.Q.x) / 2
        M_y = (self.P.y + self.Q.y) / 2
        self.M = CvPoint(M_x, M_y)
        
        tmp_x = self.Q.x - self.P.x
        tmp_y = self.Q.y - self.P.y
        
        self.len = sqrt(tmp_x * tmp_x + tmp_y * tmp_y)
        self.angle = atan2(tmp_y, tmp_x)
        
    def MLA_to_PQ(self):
        deltaX = 0.5 * self.len * cos(self.angle)
        deltaY = 0.5 * self.len * sin(self.angle)
        
        P_x = self.M.x - deltaX
        P_y = self.M.y - deltaY
        Q_x = self.M.x + deltaX
        Q_y = self.M.y + deltaY
        
        self.P = CvPoint((self.M.x - deltaX), (self.M.y - deltaY))
        self.Q = CvPoint((self.M.x + deltaX), (self.M.y + deltaY))
        
    
    def get_u(self, X):
        X_P_x = X.x - self.P.x
        X_P_y = X.y - self.P.y 
        Q_P_x = self.Q.x - self.P.x 
        Q_P_y = self.Q.y - self.P.y 
        u = ((X_P_x * Q_P_x) + (X_P_y * Q_P_y)) / self.len ** 2
        return u
    
    def get_v(self, X):
        X_P_x = X.x - self.P.x 
        X_P_y = X.y - self.P.y 
        Q_P_x = self.Q.x - self.P.x 
        Q_P_y = self.Q.y - self.P.y
        Prep_Q_P_x = Q_P_y
        Prep_Q_P_y = - Q_P_x
        v = ((X_P_x * Prep_Q_P_x) + (X_P_y * Prep_Q_P_y)) / self.len
        return v
    
    def get_point(self, u, v):
        Q_P_x = self.Q.x - self.P.x
        Q_P_y = self.Q.y - self.P.y 
        
        Prep_Q_P_x = Q_P_y
        Prep_Q_P_y = - Q_P_x
      
        point_x = self.P.x + u * (self.Q.x - self.P.x) + ((v * Prep_Q_P_x) / self.len)
        point_y = self.P.y + u * (self.Q.y - self.P.y) + ((v * Prep_Q_P_y) / self.len)
        return CvPoint(point_x, point_y)
    
    def get_weight(self, X):
        a = 1
        b = 2
        p = 0
        
        u = self.get_u(X)
        if u > 1.0:
            dist = sqrt((X.x - self.Q.x) ** 2 + (X.y - self.Q.y) ** 2)
        elif u < 0:
            dist = sqrt((X.x - self.P.x) ** 2 + (X.y - self.P.y) ** 2)
        else:
            dist = abs(self.get_v(X))
        weight = pow(pow(self.len, p) / (a + dist), b)
        return weight
    

def gen_warp_line(left_line, right_line):
    pi = 3.141592
    while left_line.angle - right_line.angle > pi:
        right_line.angle += pi
    while right_line.angle - left_line.angle > pi:
        left_line.angle += pi
    
    warp_list = []
    
    for i in range(frame_count):
        ratio = float(i) / ( frame_count - 1 )
        
        cur_line = Line()
        M_x = (1 - ratio) * left_line.M.x + ratio * right_line.M.x
        M_y = (1 - ratio) * left_line.M.y + ratio * right_line.M.y
        M_point = CvPoint(M_x, M_y)
        cur_line.M = M_point
        cur_line.len = (1 - ratio) * left_line.len + ratio * right_line.len
        cur_line.angle = (1 - ratio) * left_line.angle + ratio * right_line.angle
        
        cur_line.MLA_to_PQ()
        warp_list.append(cur_line)
    return warp_list
def bilinear(img, x, y):
    x_floor = int(x)
    y_floor = int(y)
    
    x_ceil = math.ceil(x)
    y_ceil = math.ceil(y)
    
    a = x - x_floor
    b = y - y_floor
    
    if x_ceil >= Widths - 1:
        x_ceil = Widths - 1
    if y_ceil >= Heights - 1:
        y_ceil = Heights - 1
        
    left_down = img[y_floor][x_floor]
    left_top = img[y_ceil][x_floor]
    right_down = img[y_floor][x_ceil]
    right_top = img[y_ceil][x_ceil]
    
    output_scalar = [0, 0, 0]
    for i in range(3):
        output_scalar[i] = (1 - a) * (1 - b) * left_down[i] + a * (1 - b) * right_down[i] + a * b * right_top[i] + (1 - a) * b * left_top[i]
    return output_scalar

def warp_image(left_image, right_image,left_line_list, right_line_list, warp_line_list):
    for frame_id in range(frame_count):
        new_image = np.zeros((Heights, Widths, Channels), np.uint8)
        new_right_image = np.zeros((Heights, Widths, Channels), np.uint8)
        new_left_image = np.zeros((Heights, Widths, Channels), np.uint8)
        
        ratio = float(frame_id) / (frame_count - 1)
        print(frame_id)
        
        for x in range(Widths):
            for y in range(Heights):
                cvPoint_new = CvPoint(x, y)
                right_sum_x = 0
                right_sum_y = 0
                right_weight = 0
                left_sum_x = 0
                left_sum_y = 0
                left_weight = 0
                
                for i in range(len(left_line_list)):
                    
                    new_line = warp_line_list[i][frame_id]
                    new_u = new_line.get_u(cvPoint_new)
                    new_v = new_line.get_v(cvPoint_new)
                        
                    # left line
                    left_src_line = left_line_list[i]
                    left_src_point = left_src_line.get_point(new_u, new_v)
                    left_src_weight = new_line.get_weight(cvPoint_new)
                
                    left_sum_x += left_src_point.x * left_src_weight
                    left_sum_y += left_src_point.y * left_src_weight
                    left_weight += left_src_weight
                    
                    # right line
                    right_src_line = right_line_list[i]                    
                    right_src_point = right_src_line.get_point(new_u, new_v)
                    right_src_weight = new_line.get_weight(cvPoint_new)
                    
                    right_sum_x += right_src_point.x * right_src_weight
                    right_sum_y += right_src_point.y * right_src_weight
                    right_weight += right_src_weight

                left_x = left_sum_x / left_weight
                left_y = left_sum_y / left_weight
                right_x = right_sum_x / right_weight
                right_y = right_sum_y / right_weight
              
                def update_point(x, y):
                    if x < 0:
                        x = 0
                    if y < 0:
                        y = 0
                        
                    if x >= Widths:
                        x = Widths -1
                    if y >= Heights:
                        y = Heights - 1
                    return x, y
                
                left_x, left_y = update_point(left_x, left_y)
                right_x, right_y = update_point(right_x, right_y)
                
                left_scalar = bilinear(left_image, left_x, left_y)
                right_scalar = bilinear(right_image, right_x, right_y)
                
                new_scalar = [0, 0, 0]
                for i in range(3):
                    new_scalar[i] = (1 - ratio) * left_scalar[i] + ratio * right_scalar[i]
                     
                new_image[y][x] = new_scalar
                new_left_image[y][x] = left_scalar
                new_right_image[y][x] = right_scalar
        result_images.append([new_image, new_left_image, new_right_image])
       
def onMouseImageSource(event, x, y, flags, param):
    global curSourceLine, src_line_list, SourceStart,SourceStart_x, SourceStart_y, SourceEnd, SourceDrag, SourceActive, DestActive

    if SourceActive:
        
        if  event == cv2.EVENT_LBUTTONDOWN:
            SourceDrag = True
            SourceStart_x = x
            SourceStart_y = y
            SourceStart = (x, y)
            print("SourceStart: ", SourceStart)
            
        elif event == cv2.EVENT_LBUTTONUP:
            SourceDrag = False
            SourceEnd = (x, y)
            SourceActive = False
            DestActive = True
            cv2.arrowedLine(imageSourceCopy, SourceStart, SourceEnd, (0, 255, 0), 2)
            cv2.imshow("Image 1", imageSourceCopy)
            curSourceLine = Line()
            curSourceLine.P = CvPoint(SourceStart_x, SourceStart_y)
            curSourceLine.Q = CvPoint(x, y)
            print("SourceEnd: ", (x, y))
            curSourceLine.PQ_to_MLA()
            src_line_list.append(curSourceLine)
            
        elif event == cv2.EVENT_MOUSEMOVE:
            if SourceDrag:
                tempImage = imageSourceCopy.copy()
                cv2.arrowedLine(tempImage, SourceStart, (x, y), (0, 255, 0), 2)
                cv2.imshow('Image 1', tempImage)
                
def onMouseImageDest(event, x, y, flags, param):
    global count, dest_line_list, DestStart, DestStart_x, DestStart_y, DestEnd, DestDrag, DestActive, Dest2Active
    
    if DestActive:
        if event == cv2.EVENT_LBUTTONDOWN:
            DestDrag = True
            DestStart = (x, y)
            DestStart_x = x
            DestStart_y = y
            print("DestStart: ", (x, y))

        elif event == cv2.EVENT_LBUTTONUP:
            DestDrag = False
            DestEnd = (x, y)
            DestActive = False
            Dest2Active = True
            cv2.arrowedLine(imageDestCopy, DestStart, DestEnd, (0, 255, 0), 2)
            cv2.imshow('Image 2', imageDestCopy)
            curDestLine = Line()
            curDestLine.P = CvPoint(DestStart_x, DestStart_y)
            curDestLine.Q = CvPoint(x, y)
            print("DestEnd: ", (x, y))
            curDestLine.PQ_to_MLA()
            dest_line_list.append(curDestLine)
        elif event == cv2.EVENT_MOUSEMOVE:
            if DestDrag:
                tempImage = imageDestCopy.copy()
                cv2.arrowedLine(tempImage, DestStart, (x, y), (0, 255, 0), 2)
                cv2.imshow('Image 2', tempImage)

def onMouseImageDest2(event, x, y, flags, param):
    global count, dest2_line_list, Dest2Start, Dest2Start_x, Dest2Start_y, Dest2End, Dest2Drag, Dest2Active

    if Dest2Active:
        if event == cv2.EVENT_LBUTTONDOWN:
            Dest2Drag = True
            Dest2Start = (x, y)
            Dest2Start_x = x
            Dest2Start_y = y
            print("Dest2Start: ", (x, y))

        elif event == cv2.EVENT_LBUTTONUP:
            Dest2Drag = False
            Dest2End = (x, y)
            Dest2Active = False
            cv2.arrowedLine(imageDest2Copy, Dest2Start, Dest2End, (0, 255, 0), 2)
            cv2.imshow('Image 3', imageDest2Copy)
            curDest2Line = Line()
            curDest2Line.P = CvPoint(Dest2Start_x, Dest2Start_y)
            curDest2Line.Q = CvPoint(x, y)
            print("Dest2End: ", (x, y))
            curDest2Line.PQ_to_MLA()
            dest2_line_list.append(curDest2Line)
        elif event == cv2.EVENT_MOUSEMOVE:
            if Dest2Drag:
                tempImage = imageDest2Copy.copy()
                cv2.arrowedLine(tempImage, Dest2Start, (x, y), (0, 255, 0), 2)
                cv2.imshow('Image 3', tempImage)

def read_img(result_images):
    global count
    cv2.namedWindow('Warpped 1')
    cv2.moveWindow('Warpped 1', WINDOW_X, WINDOW_Y + imageSource.shape[0] + PADDING)
    
    cv2.namedWindow('Warpped 2')
    cv2.moveWindow('Warpped 2', WINDOW_X + PADDING + imageSource.shape[1], WINDOW_Y + imageSource.shape[0] + PADDING)
    
    cv2.namedWindow('Warpped 3')
    cv2.moveWindow('Warpped 3', WINDOW_X + 2 * PADDING + 2 * imageSource.shape[1], WINDOW_Y + imageSource.shape[0] + PADDING)
    
    cv2.namedWindow('Final Result')
    cv2.moveWindow('Final Result', WINDOW_X + 3 * PADDING + 3 * imageSource.shape[1], WINDOW_Y + imageSource.shape[0] + PADDING)
    
    for i in range(len(result_images)):
        
        cv2.imshow('Final Result', result_images[i][0])
        if i < len(result_images) / 2:
            cv2.imshow('Warpped 1', result_images[i][1])
            cv2.imshow('Warpped 2', result_images[i][2])
            cv2.imshow('Warpped 3', imageDest2)
        else:
            cv2.imshow('Warpped 2', result_images[i][1])
            cv2.imshow('Warpped 3', result_images[i][2])
        cv2.waitKey(500)
        count += 1
        print(f'Frame No.{count}  Total Frame {len(result_images)}')
        
    cv2.destroyAllWindows() 
    
    
    
if __name__ == "__main__":
    # Initialize images
    imageSource = cv2.imread('.\images\women.jpg')
    imageDest = cv2.imread('.\images\cheetah.jpg')
    imageDest2 = cv2.imread('.\images\wife.jpg')
    print(imageDest2.shape)
    # Check image dimensions and resize if necessary
    if imageSource.shape != imageDest.shape:
        imageDest = cv2.resize(imageDest, (imageSource.shape[1], imageSource.shape[0]))
    
    if imageDest.shape != imageDest2.shape:
        imageDest2 = cv2.resize(imageDest2, (imageDest.shape[1], imageDest.shape[0]))

    Heights, Widths, Channels = imageSource.shape # 189, 255, 3
    print(Heights, Widths, Channels)
    
    print("Do you want to draw? Press y(yes) or n(no)")
    
     # Create windows
    WINDOW_X = 100
    WINDOW_Y = 200
    PADDING = 20
    cv2.namedWindow("Image 1")
    cv2.namedWindow("Image 2")
    cv2.namedWindow("Image 3")

    
    cv2.moveWindow('Image 1', WINDOW_X, WINDOW_Y)
    cv2.moveWindow('Image 2', WINDOW_X + PADDING + imageSource.shape[1], WINDOW_Y)
    cv2.moveWindow('Image 3', WINDOW_X + PADDING*2 + 2*imageDest.shape[1], WINDOW_Y)

    
    imageSourceCopy = imageSource.copy()
    imageDestCopy = imageDest.copy()
    imageDest2Copy = imageDest2.copy()

    
    # Show images
    cv2.imshow('Image 1', imageSourceCopy)
    cv2.imshow('Image 2', imageDestCopy)
    cv2.imshow('Image 3', imageDest2Copy)


    
    while True:
        key1 = cv2.waitKey(0)
        
        if key1 == ord("y"):
            want_to_draw = True
            break
        elif key1 == ord("n"):
            want_to_draw = False
            break
       
       
    if want_to_draw:  
      
        # Initialize variables for draw interactive line 
        SourceStart = None
        SourceStart_x = None
        SourceStart_y = None
        SourceEnd = None
        DestStart = None
        DestStart_x = None
        DestStart_y = None
        DestEnd = None
        Dest2Start = None
        Dest2Start_x = None
        Dest2Start_y = None
        Dest2End = None
        SourceDrag = False
        DestDrag = False
        Dest2Drag = False
        SourceActive = False
        DestActive = False
        Dest2Active = False
   
        cv2.setMouseCallback('Image 1', onMouseImageSource)
        cv2.setMouseCallback('Image 2', onMouseImageDest)  
        cv2.setMouseCallback('Image 3', onMouseImageDest2)  

        
        print("Usage:")
        print("Press 'a' to add new pairs of feature lines.")
        print("Press 's' to start warping.")

        while True:
            key = cv2.waitKey(0)
            if key == 97:
                SourceActive = True
            elif key == 115:
                print("Computing...")
                break
    else:
        Source = [[112, 41, 111, 104], [62, 43, 92, 47], [138, 48, 167, 45], [89, 131, 138, 131], [41, 76, 57, 142], [187, 76, 171, 149]]
        Dest = [[129, 48, 129, 134], [35, 17, 72, 30], [174, 29, 221, 17], [84, 181, 171, 181], [6, 46, 7, 156], [246, 45, 246, 146]]
        Dest2 = [[133, 81, 141, 127], [96, 81, 115,80], [147, 77, 161, 71], [121, 150, 151, 147], [66, 114, 80, 149], [169, 102, 159, 160]]
        for i in range(len(Source)):
            S_line = Line()
            D_line = Line()
            D2_line = Line()
            
            S_line.P = CvPoint(Source[i][0], Source[i][1])
            S_line.Q = CvPoint(Source[i][2], Source[i][3])
            D_line.P = CvPoint(Dest[i][0], Dest[i][1])
            D_line.Q = CvPoint(Dest[i][2], Dest[i][3])
            D2_line.P = CvPoint(Dest2[i][0], Dest2[i][1])
            D2_line.Q = CvPoint(Dest2[i][2], Dest2[i][3])
            
            S_line.PQ_to_MLA()
            D_line.PQ_to_MLA()
            D2_line.PQ_to_MLA()
            
            src_line_list.append(S_line)
            dest_line_list.append(D_line)
            dest2_line_list.append(D2_line)
    dest_line_list_copy = dest_line_list    
    for i in range(len(src_line_list)):
        src_line = src_line_list[i]
        dest_line = dest_line_list[i]
        dest2_line = dest2_line_list[i]
        warp_line_list_dest.append(gen_warp_line(src_line, dest_line))
        
    for i in range(len(dest2_line_list)):
        dest_line2 = dest_line_list_copy[i]
        dest2_line = dest2_line_list[i]
        warp_line_list_dest2.append(gen_warp_line(dest_line2, dest2_line))

    warp_image(imageSource, imageDest, src_line_list, dest_line_list, warp_line_list_dest)
    warp_image(imageDest, imageDest2, dest_line_list_copy, dest2_line_list, warp_line_list_dest2)
    read_img(result_images)
    print("Complete!")
        