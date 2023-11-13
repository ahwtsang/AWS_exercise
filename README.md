# Exercise Objective
This coding exercise deploys a simple medical image processing algorithm in serverless cloud infrastructure. The image processing algorithm draws three circles that are evenly spaced (from each other and the top and bottom of the image) along a vertical line in the center of the image. The deployment exposes a RESTful HTTPS endpoint that accepts the URL of a DICOM image in cloud storage, processes the image, and deposits its output in the same cloud storage bucket, adjacent to the input image. The deployment will automatically spin down to zero when not in use and spin up to multiple instances when under load. The deployment is done using Amazon Web Services.  

## Dataset
The **Pseudo-PHI-DICOM-Data** dataset from [The Cancer Imaging Archive](https://www.cancerimagingarchive.net/collections/) provided by the Cancer Imaging Program (CIP) of the National Cancer Institute is used for this exercise. Refer to this [publication](https://www.nature.com/articles/s41597-021-00967-y) for further details of this dataset.
*Rutherford, M., Mun, S.K., Levine, B. et al. A DICOM dataset for evaluation of medical image de-identification. Sci Data 8, 183 (2021)*.

## Algorithm
The image processing algorithm is implemented in Python 3.9 using the following packages:
* Pydicom
* Numpy
* Pillow
The output DICOM file is converted to RGB with window width and center adjusted in the header and saved as *_annot.dcm appended to the original filename in the same cloud storage bucket.

## Deployment
The deployment uses the following AWS services:
* S3
* IAM
* Lambda
* API Gateway
The boto3 Python package is required for the Lambda function to access files in S3 bucket.

## Load Testing
The load of the AWS lambda function can be monitored using AWS CloudWatch. The HTTPS requests to the API to invoke the image processing application can be achieved by:
1. Python script to send http requests using curl (WSL Ubuntu 22.04.2 LTS)
2. Load/Performance testing using [Artillery](https://www.artillery.io/) (Windows PowerShell)


