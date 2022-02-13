# -author Rahul K -*-
import cv2
import pytesseract
#import matplotlib.pyplot
import pandas as pd
import numpy as np
import tkinter as tk
import os
pytesseract.pytesseract.tesseract_cmd=r'C:\Program Files\Tesseract-OCR\tesseract.exe'
pd.set_option('display.max_colwidth', None)


input_d=r'C:\Users\rahul\Desktop\tesseract_project\tesseract_input'
output_d=r'C:\Users\rahul\Desktop\tesseract_project\tesseract_output'
take_one_by_one=False
IMAGE_SIZE = 1000


def get_resized_image(path):
    image=cv2.imread(path)
    height, width, channels=image.shape
    scale_factor = IMAGE_SIZE / height
    print("SCALE___"+str(scale_factor))
    im_resized = cv2.resize(image, None, fx= scale_factor, fy= scale_factor, interpolation= cv2.INTER_LINEAR)
    return im_resized

def pre_process_image_for_ocr(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (1,1), 0)
    return blur

def get_contours(img):
    gray=pre_process_image_for_ocr(img)
    thresh = cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,11,30)
    # Dilate to combine adjacent text contours
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9,9))
    dilate = cv2.dilate(thresh, kernel, iterations=4)
    # Find contours, highlight text areas, and extract ROIs
    cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    line_items_coordinates = []
    for c in cnts:
        x,y,w,h = cv2.boundingRect(c)
        image = cv2.rectangle(img, (x,y), (x+w, y+h), color=(255,0,255), thickness=1)
        line_items_coordinates.append([(x,y), (x+w, y+h)])
    return image,line_items_coordinates
    
 
    
def form_csv_from_image(df,original_img,coordinates_to_crop):
    if(not isinstance(df, pd.DataFrame)):
        df=pd.DataFrame(columns=list(coordinates_to_crop.keys()))
    prev_len=df.shape[0]
    for k in coordinates_to_crop:
        v=coordinates_to_crop[k]['pos']
        lang=coordinates_to_crop[k]['lang']
        cropped_image=original_img[v[0][1]:v[1][1], v[0][0]:v[1][0]]
        #cv2.imshow('cropped_image',cropped_image)
        img=pre_process_image_for_ocr(cropped_image)
        df.at[prev_len,k]=str(pytesseract.image_to_string(img,lang=lang)).replace('\n', ' ')
    return df
   

def submit():
    print( name_var.get(),clicked.get())
    root.destroy()
    
       
        
def click_event(event, x, y, flags, params):
    global pos_a,tmp,coordinates_with_columns,clicked,name_var,root
    if event == cv2.EVENT_LBUTTONDOWN:
        #if previous event was left click and current event is also left click
        if pos_a != None:
            pos_a=None
            cv2.imshow('image', img)
        else:
            pos_a=(x,y)
            print(pos_a)
            cv2.imshow('image', img)
    #if previous event was left click and current event is right or mouse move    
    if ((event==cv2.EVENT_RBUTTONDOWN or event==cv2.EVENT_MOUSEMOVE) and pos_a!=None):
        tmp=np.copy(img)
        if event==cv2.EVENT_MOUSEMOVE:
            cv2.rectangle(tmp, pos_a, (x, y), color=(255,0,255), thickness=1)
            cv2.imshow('image', tmp)
        #put pos_a=None to unbind mouse move and right click event
        if event == cv2.EVENT_RBUTTONDOWN:
            pos_a_copy=np.copy(pos_a)
            pos_a=None
            cv2.rectangle(img, pos_a_copy, (x, y), color=(255,0,255), thickness=1)
            cv2.imshow('image', img)
            root=tk.Tk()
            root.geometry("600x400")
            clicked = tk.StringVar()
            name_var=tk.StringVar()
            clicked.set( 'eng' )
            drop_label = tk.Label(root, text = 'Language', font = ('calibre',10,'bold'))
            drop = tk.OptionMenu( root , clicked , 'hin','eng','hin+eng' )
            name_label = tk.Label(root, text = 'Columnname', font=('calibre',10, 'bold'))
            name_entry = tk.Entry(root,textvariable = name_var, font=('calibre',10,'normal'))
            sub_btn=tk.Button(root,text = 'Submit', command = submit)
            name_label.grid(row=0,column=0)
            name_entry.grid(row=0,column=1)
            drop_label.grid(row=1,column=0)
            drop.grid(row=1,column=1)
            sub_btn.grid(row=2,column=1)
            root.mainloop()
            coordinates_with_columns[name_var.get()]={'pos':[pos_a_copy,(x,y)],'lang':clicked.get()}
            
           
def start_taking_inputs_from_image(img):
    cv2.imshow('image', img)
    cv2.setMouseCallback('image', click_event)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
              
         
if __name__=="__main__":
    global pos_a,tmp,coordinates_with_columns,root,clicked,name_var
    pos_a=None
    tmp=None
    img=None
    preprocessed_img=None
    df=None
    coordinates_with_columns={}
    count=0
    for path in os.listdir(input_d):
        full_path = os.path.join(input_d, path)
        if os.path.isfile(full_path):
            if count==0 or take_one_by_one==True:
                 img=get_resized_image(full_path)
                 start_taking_inputs_from_image(img)
            elif take_one_by_one==True:
                df=form_csv_from_image(df, img, coordinates_with_columns)
            else:
                df=form_csv_from_image(df, img, coordinates_with_columns)
            count+=1
    print(df)
    df.to_csv(output_d+'/'+"Result.csv", index=False)
    
    