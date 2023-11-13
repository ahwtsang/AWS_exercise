import numpy as np
import pydicom
import argparse
import os, glob
import math
from PIL import Image, ImageDraw

def process_image(dcmfile):
    ds = pydicom.dcmread(dcmfile)
    img = ds.pixel_array # dtype = uint16

    # rescale image to 0-255 range
    img_rescale = img - np.min(img)
    img_rescale = img_rescale / np.max(img)
    img_rescale = (img_rescale * 255).astype(np.uint8)
    
    rows = ds['Rows'].value
    cols = ds['Columns'].value
    print (f"the image dimension of {dcmfile} is {rows}x{cols}")
    
    # create a PIL image to draw                 
    img_pil = Image.fromarray(img_rescale)
    img_rgb = img_pil.convert('RGB')
    draw = ImageDraw.Draw(img_rgb)

    # draw a vertical line to the image
    line_pts = [(math.floor(rows/2),0), (math.floor(rows/2),cols-1)]
    draw.line(line_pts,fill=None,width=1)

    # draw circles to the image
    offset = math.floor(cols/16)
    circle1_pts = [(math.floor(rows/8)-offset,3*math.floor(cols/8)), (3*math.floor(rows/8)-offset,5*math.floor(cols/8))]
    draw.ellipse(circle1_pts,fill=None,outline=(255,0,0))

    circle2_pts = [(3*math.floor(rows/8),3*math.floor(cols/8)), (5*math.floor(rows/8),5*math.floor(cols/8))]
    draw.ellipse(circle2_pts,fill=None,outline=(0,255,0))

    circle3_pts = [(5*math.floor(rows/8)+offset,3*math.floor(cols/8)), (7*math.floor(rows/8)+offset,5*math.floor(cols/8))]
    draw.ellipse(circle3_pts,fill=None,outline=(0,0,255))
    
    # modify DICOM tags
    ds.PhotometricInterpretation = 'RGB'
    ds.SamplesPerPixel = 3
    ds.BitsAllocated = 8
    ds.BitsStored = 8
    ds.HighBit = 7
    ds.add_new(0x00280006, 'US', 0)
    ds.is_little_endian = True
    if "WindowCenter" in ds:
        ds.WindowCenter=[128,128]
    if "WindowWidth" in ds:
        ds.WindowWidth=[256,256]
    ds.fix_meta_info()

    # convert PIL image back to numpy array
    img_np = np.asarray(img_rgb)
    
    # save pixel data and dicom file
    ds.PixelData = img_np.tobytes()
    dcmfile_new = dcmfile.replace(".dcm","_annot.dcm")
    ds.save_as(dcmfile_new)
    print(f"Processed DICOM file and saved as {dcmfile_new}")
    
    del ds, img, img_rescale, img_pil, img_rgb, draw, img_np

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(prog='process_image', description='Simple script to read DICOM series and draw on image')
    parser.add_argument("-i", "--input", help = "File path of input DICOM series or single DICOM file", required=True)
    args = parser.parse_args()
    input_path = args.input

    if input_path.endswith('.dcm'):
        process_image(input_path)
    else:
        # this is a folder of a MRI scan series
        os.chdir(input_path)
        dcm_images = glob.glob("*.dcm")
        print (f"There are {len(dcm_images)} DICOM images in the folder")
        if len(dcm_images) > 0:
            for eachimg in dcm_images:
                process_image(os.path.join(input_path,eachimg))