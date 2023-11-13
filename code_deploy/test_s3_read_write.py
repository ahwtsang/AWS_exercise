import boto3

s3 = boto3.client("s3")

def lambda_handler(event, context):
    bucket = 'myincomingmri'
    key = '9894340694/MRI_ABDOMEN_PELVIS_WWO_CONT/LIVER-KIDNEYTIFL2DAXIAL/sample01.txt'
    
    try:
        data = s3.get_object(Bucket=bucket, Key=key)
        retdata = data["Body"].read()
        
        print ("Write to s3")
        
        text2str = 'Write some text in the second file'
        new_key = key.replace("01.txt","02.txt")
        s3.put_object(Bucket=bucket, Key=new_key, Body=text2str)
        
        return {
            'statusCode': 200,
            'data': retdata
        }
    except Exception as e:
        print (e)
        raise e