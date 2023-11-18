"""
Lambda script that is triggered via EventBridge every hour on the hour
https://docs.aws.amazon.com/lambda/latest/dg/services-cloudwatchevents-expressions.html

On even hours (UTC) the event action of "advertise" triggeres the configured BYOIP CIDR to be advertised. 
On uneven hours (UTC) the event action of "withdraw" causes the CIDR to be withdrawn.

As EventBridge triggered Lambda scripts run with a slight random delay, the exact timestamp of the last run
can be determined here: https://byoip.as213151.net/us-east-1.html
"""
import json
import boto3
import time
from datetime import datetime

CIDR = "2602:fb2a:ff::/48"
ASN = "213151"
BUCKET = <my bucket name> 
FILE = "us-east-1.html"

def lambda_handler(event, context):
    client = boto3.client('ec2')
    
    try:
        if event["action"] == "advertise":
            response = client.advertise_byoip_cidr(
                Cidr=CIDR,
                Asn=ASN,
                DryRun=False
            )
        elif event["action"] == "withdraw":
            response = client.withdraw_byoip_cidr(
                Cidr=CIDR,
                DryRun=False
            )
        else:
            response = []
    except:
        return {
            'statusCode': 500,
            'body': 'Unknown request'
        }    
    
    ts = round(time.time(), 2)
    try:
        if response["ByoipCidr"]["State"] == "advertised":
            status = "advertise"
        elif response["ByoipCidr"]["State"] == "provisioned":
            status = "withdraw"
    except:
        status = "Unknown"
    
    results_str = "action: " + status + "<br>prefix: " + CIDR + "<br>asn: " + ASN + "<br>date: " + "<br>date: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z') + "<br>timestamp: " + str(ts)
    s3 = boto3.resource('s3')
    object = s3.Object(BUCKET, FILE)
    object.put(Body=results_str, ContentType='text/html')
        
    return {
        'statusCode': 200,
        'body': status + " " + str(ts)
    }
