import numpy as np
import pydicom
import math
import io
import boto3
from PIL import Image, ImageDraw

s3 = boto3.client("s3")

def lambda_handler(event, context):
    bucket = event["bucket"]
    key = event["key"]

    try:
        # get the file from s3 bucket
        s3_obj = s3.get_object(Bucket=bucket, Key=key)
        file_stream = s3_obj['Body'].read()
        ds = pydicom.dcmread(io.BytesIO(file_stream))
        img = ds.pixel_array # dtype = uint16

        # rescale image to 0-255 range
        img_rescale = img - np.min(img)
        img_rescale = img_rescale / np.max(img)
        img_rescale = (img_rescale * 255).astype(np.uint8)
        
        rows = ds['Rows'].value
        cols = ds['Columns'].value
        
        print (f"Received {key} from s3, the image dimension is {rows}x{cols}")

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
        
        # save pixel data and dicom file to s3 bucket
        ds.PixelData = img_np.tobytes()
        new_key = key.replace(".dcm","_annot.dcm")
        file_stream = io.BytesIO()
        ds.save_as(file_stream)
        s3.put_object(Bucket=bucket, Key=new_key, Body=file_stream.getvalue())

        return {
            "response_code": 200,
            "body": f"Processed DICOM file and saved as {new_key}"
        }
    
    except Exception as e:
        print (e)
