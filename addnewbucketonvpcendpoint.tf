###############################################
## Author : HKO
## Date: 16/02/2020
## Description: This Lambda function Add Bucket in VPC S3 Endpoint Policy
#####################################################

from boto3 import resource, client
from logging import getLogger, info, error, debug
from os import environ
from botocore.exceptions import ClientError
from json import dumps

class AddBucketToEndpointPolicy(object):

    def __init__(self):
        
        self.s3_client = client('s3')
        self.ec2_client = client('ec2')
        
        self.logger = getLogger()
        self.logger.setLevel("INFO")

        self.allbuckets = set()
        self.routes_and_vpcs = dict()
        self.oldendpoints = set()
        self.newendpoints = list()
        self.jsonpolicy = str()

    def getlistofBuckets(self):
        response = self.s3_client.list_buckets()
        for bucket in response['Buckets']:
            self.allbuckets.add(bucket['Name'])
    
    def getRouteTables(self):
        print("GetRouteTables")
        response = self.ec2_client.describe_route_tables()
        for resp in response['RouteTables']:
            info(resp)
            route = resp["RouteTableId"]
            vpc_id = resp["VpcId"]
            self.routes_and_vpcs[route] = vpc_id
    
    def getCurrentS3Endpoint(self):
        print("GetCurrentS3Endpoint")
        response = self.ec2_client.describe_vpc_endpoints(
            Filters=[
                {
                    'Name': 'service-name',
                    'Values': ['com.amazonaws.eu-west-1.s3']
                }
                
            ]
        )
        for resp in response["VpcEndpoints"]:
            info(resp)
            self.oldendpoints.add(resp["VpcEndpointId"])
            print("GetEndpointID : {}".format(self.oldendpoints))
    
    def deleteCurrentS3Endpoint(self):
        print("DeleteCurrentS3Endpoint")
        for endpoint in self.oldendpoints:
            try:

                response = self.ec2_client.delete_vpc_endpoints(
                    VpcEndpointIds = [
                        endpoint
                    ]
                )
            except ClientError:
                pass
    
    def buildJsonPolicy(self):
        print("BuildJsonPolicy")
        buckets_arn = ['arn:aws:s3:::{0}'.format(bucket) for bucket in self.allbuckets]
        #print(buckets_arn)
        data =  { "Statement": [{ "Sid": "Stmt1581954372280", "Action": "s3:*", "Effect": "Allow", "Resource": buckets_arn, "Principal": "*" }] }
        info(data)
        self.jsonpolicy = dumps(data, indent=2)
    
    def createNewS3Endpoint(self):
        print("CreateNewS3Endpoint")
        for route, vpc_id in self.routes_and_vpcs.items():
            info('{0}-{1}'.format(route, vpc_id))
            response = self.ec2_client.create_vpc_endpoint(
                VpcEndpointType = 'Gateway',
                VpcId = vpc_id,
                ServiceName = 'com.amazonaws.eu-west-1.s3',
                PolicyDocument = self.jsonpolicy,
                RouteTableIds = [route]
            )
            self.newendpoints.append(response['VpcEndpoint']['VpcEndpointId'])
        
    def putTagOnNewS3Endpoint(self):
        response = self.ec2_client.create_tags(
            Resources = self.newendpoints,
            Tags=[
                {
                    'Key' : 'Name',
                    'Value' : 'S3 VPC Endpoint Gateway'
                }
            ]
        )

def lambda_handler(event, context):
    print("***** Start Processing Endpoint Policy ****")
    endpoint = AddBucketToEndpointPolicy()
    endpoint.getlistofBuckets()
    endpoint.getRouteTables()
    endpoint.getCurrentS3Endpoint()
    endpoint.deleteCurrentS3Endpoint()
    endpoint.buildJsonPolicy()
    endpoint.createNewS3Endpoint()
    endpoint.putTagOnNewS3Endpoint()
    print("***** End Processing Endpoint Policy ****")
