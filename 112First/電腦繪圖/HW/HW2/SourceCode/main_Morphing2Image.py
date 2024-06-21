import cv2
import numpy as np
import matplotlib.pyplot as plt
import math
from math import log10, atan2, cos, sin, sqrt
import os



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
    
left_line_list = [] # Source
right_line_list = [] # Destination
warp_line_list = []
frame_count = 30

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
    warp_line_list.append(warp_list)

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

def warp_image():
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
                left_sum_x = 0
                left_sum_y = 0
                right_weight = 0
                left_weight = 0 
                
                for i in range(len(left_line_list)):
                    
                    new_line = warp_line_list[i][frame_id]
                    new_u = new_line.get_u(cvPoint_new)
                    new_v = new_line.get_v(cvPoint_new)
                        
                    # left line
                    src_line = left_line_list[i]
                    src_point = src_line.get_point(new_u, new_v)
                    src_weight = new_line.get_weight(cvPoint_new)
                
                    left_sum_x += src_point.x * src_weight
                    left_sum_y += src_point.y * src_weight
                    left_weight += src_weight
                    
                    # right line
                    dest_line = right_line_list[i]                    
                    dest_point = dest_line.get_point(new_u, new_v)
                    dest_weight = new_line.get_weight(cvPoint_new)
                    
                    right_sum_x += dest_point.x * dest_weight
                    right_sum_y += dest_point.y * dest_weight
                    right_weight += dest_weight
                
                left_x = left_sum_x / left_weight
                left_y = left_sum_y / left_weight
                right_x = right_sum_x / right_weight
                right_y = right_sum_y / right_weight
                
                # update point 
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
                
                left_scalar = bilinear(imageSource, left_x, left_y)
                right_scalar = bilinear(imageDest, right_x, right_y)
                
                new_scalar = [0, 0, 0]
                for i in range(3):
                    new_scalar[i] = (1 - ratio) * left_scalar[i] + ratio * right_scalar[i]
                     
                new_image[y][x] = new_scalar
                new_left_image[y][x] = left_scalar
                new_right_image[y][x] = right_scalar
                
        # save img
        fix, axes = plt.subplots(1, 3, figsize = (10, 6))
        plt.suptitle("Total Frame: " + str(frame_count) + " , Now Frame: " + str(frame_id) )
        [a.axis('off') for a in axes.ravel()]
        axes[0].imshow(cv2.cvtColor(new_left_image, cv2.COLOR_BGR2RGB))
        axes[0].title.set_text("Source image warping")
        
        axes[1].imshow(cv2.cvtColor(new_image, cv2.COLOR_BGR2RGB))
        axes[1].title.set_text("color blending")
        
        axes[2].imshow(cv2.cvtColor(new_right_image, cv2.COLOR_BGR2RGB))
        axes[2].title.set_text("Destination image warping")
        
        if frame_id == 0:
            log_10 = 0
        else:
            log_10 = int(log10(frame_id))
        log_10_all = int(log10(frame_count))
        plt.savefig("./outputs/" + "0" * (log_10_all - log_10) + str(frame_id) + ".jpg")
 

def onMouseImageSource(event, x, y, flags, param):
    global curSourceLine, left_line_list, SourceStart,SourceStart_x, SourceStart_y, SourceEnd, SourceDrag, SourceActive, DestActive

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
            cv2.imshow("Source Image", imageSourceCopy)
            curSourceLine = Line()
            curSourceLine.P = CvPoint(SourceStart_x, SourceStart_y)
            curSourceLine.Q = CvPoint(x, y)
            print("SourceEnd: ", (x, y))
            curSourceLine.PQ_to_MLA()
            left_line_list.append(curSourceLine)
            
        elif event == cv2.EVENT_MOUSEMOVE:
            if SourceDrag:
                tempImage = imageSourceCopy.copy()
                cv2.arrowedLine(tempImage, SourceStart, (x, y), (0, 255, 0), 2)
                cv2.imshow('Source Image', tempImage)
                
def onMouseImageDest(event, x, y, flags, param):
    global count, right_line_list, DestStart, DestStart_x, DestStart_y, DestEnd, DestDrag, SourceActive, DestActive

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
            cv2.arrowedLine(imageDestCopy, DestStart, DestEnd, (0, 255, 0), 2)
            cv2.imshow('Destination Image', imageDestCopy)
            curDestLine = Line()
            curDestLine.P = CvPoint(DestStart_x, DestStart_y)
            curDestLine.Q = CvPoint(x, y)
            print("DestEnd: ", (x, y))
            curDestLine.PQ_to_MLA()
            right_line_list.append(curDestLine)
        elif event == cv2.EVENT_MOUSEMOVE:
            if DestDrag:
                tempImage = imageDestCopy.copy()
                cv2.arrowedLine(tempImage, DestStart, (x, y), (0, 255, 0), 2)
                cv2.imshow('Destination Image', tempImage)
                

def read_img():
    file_list = os.listdir("./outputs/")
    file_list = np.sort(file_list)
    print(file_list)

    for img in file_list:
        cv2.namedWindow('Image', cv2.WINDOW_NORMAL)
        cv2.imshow("Image", cv2.imread("./outputs/" + img))
        cv2.waitKey(500)
    cv2.destroyAllWindows() 
    
    
    
if __name__ == "__main__":
    # Initialize images
    imageSource = cv2.imread('.\images\women.jpg')
    imageDest = cv2.imread('.\images\cheetah.jpg')

    # Check image dimensions and resize if necessary
    if imageSource.shape != imageDest.shape:
        imageDest = cv2.resize(imageDest, (imageSource.shape[1], imageSource.shape[0]))
    
    

    Heights, Widths, Channels = imageSource.shape # 189, 255, 3
    print(Heights, Widths, Channels)
    
    print("Do you want to draw? Press y(yes) or n(no)")
    
     # Create windows
    WINDOW_X = 100
    WINDOW_Y = 200
    PADDING = 20
    cv2.namedWindow("Source Image")
    cv2.namedWindow("Destination Image")

    
    cv2.moveWindow('Source Image', WINDOW_X, WINDOW_Y)
    cv2.moveWindow('Destination Image', WINDOW_X + PADDING + imageSource.shape[1], WINDOW_Y)

    
    imageSourceCopy = imageSource.copy()
    imageDestCopy = imageDest.copy()

    
    # Show images
    cv2.imshow('Source Image', imageSourceCopy)
    cv2.imshow('Destination Image', imageDestCopy)


    
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
        SourceDrag = False
        DestDrag = False
        SourceActive = False
        DestActive = False
        count = 0
        Source_line_list = []
        cv2.setMouseCallback('Source Image', onMouseImageSource)
        cv2.setMouseCallback('Destination Image', onMouseImageDest)  
        
        print("Usage:")
        print("Press 'a' to add new pairs of feature lines.")
        print("Press 's' to start warping.")
        print("Press ESC/'q' to quit.")      

        while True:
            key = cv2.waitKey(0)
            if key == 27 or key == 113:
                break
            elif key == 97:
                SourceActive = True
            elif key == 115:
                print("Computing...")
                break
    else:
        Source = [[65, 19, 94, 33], [133, 32, 166, 25], [62, 41, 92, 45], [136, 44, 166, 48], [119, 42, 117, 96], [88, 130, 133, 130], [43, 62, 54, 137], [182, 68, 172, 138], [69, 149, 96, 177], [163, 154, 146, 174]]
        Dest = [[29, 13, 67, 11], [178, 14, 215, 12], [39, 24, 73, 21], [181, 26, 213, 22], [126, 28, 130, 161], [91, 173, 169, 177], [5, 43, 8, 158], [249, 49, 250, 150], [11, 167, 12, 185], [246, 161, 247, 179]]
        for i in range(len(Source)):
            S_line = Line()
            D_line = Line()
            S_line.P = CvPoint(Source[i][0], Source[i][1])
            S_line.Q = CvPoint(Source[i][2], Source[i][3])
            D_line.P = CvPoint(Dest[i][0], Dest[i][1])
            D_line.Q = CvPoint(Dest[i][2], Dest[i][3])
            
            S_line.PQ_to_MLA()
            D_line.PQ_to_MLA()
            
            left_line_list.append(S_line)
            right_line_list.append(D_line)
        
    for i in range(len(left_line_list)):
        left_line = left_line_list[i]
        right_line = right_line_list[i]
        gen_warp_line(left_line, right_line)
    warp_image()
    read_img()
    print("Complete!")
        