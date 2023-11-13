
import os, glob
import argparse
import subprocess

LOCAL_ROOT_DIR = "/mnt/c/Stratagen_Bio_Coding_Exercise/imaging_data/Pseudo-PHI-DICOM-Data"
BUCKET = "myincomingmri"
API_URL = "https://1kyg8luaxd.execute-api.us-east-2.amazonaws.com/deploy/adrian-coding-exercise"

def load_testing(in_dir):
    image_dir = os.path.join(LOCAL_ROOT_DIR,in_dir)
    print (image_dir)
    os.chdir(image_dir)
    dcm_images = sorted(glob.glob("*.dcm"))
    print (f"There are {len(dcm_images)} DICOM images in the folder")
    output_list = []
    if len(dcm_images) > 0:
        for eachimg in dcm_images:
            p = subprocess.Popen(["curl","-X","GET","-G","-d",f"bucket={BUCKET}","-d",f"key={os.path.join(in_dir,eachimg)}",API_URL], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, errors = p.communicate()
            output_list.append(output.decode('UTF-8'))
    
    output_string = '\n'.join(output_list)
    print (output_string)

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(prog='load_testing', description='Simple script to perform load testing of lambda function')
    parser.add_argument("-i", "--input", help = "File path of input DICOM series", required=True)
    args = parser.parse_args()
    input_path = args.input

    load_testing(input_path)