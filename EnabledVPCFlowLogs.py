from boto3 import client
from os import environ


def lambda_handler(event, context):
    '''
    Extract the VPC ID from the event and enable VPC Flow Logs.
    '''

    try:
        vpc_id = event['detail']['responseElements']['vpc']['vpcId']

        print('VPC: ' + vpc_id)

        ec2_client = client('ec2')

        response = ec2_client.describe_flow_logs(
            Filter=[
                {
                    'Name': 'resource-id',
                    'Values': [
                        vpc_id,
                    ]
                },
            ],
        )

        if len(response[u'FlowLogs']) != 0:
            print('VPC Flow Logs are ENABLED')
        else:
            print('VPC Flow Logs are DISABLED')

            print('FLOWLOGS_GROUP_NAME: ' + environ['FLOWLOGS_GROUP_NAME'])
            print('ROLE_ARN: ' + environ['ROLE_ARN'])

            response = ec2_client.create_flow_logs(
                ResourceIds=[vpc_id],
                ResourceType='VPC',
                TrafficType='ALL',
                LogGroupName=environ['FLOWLOGS_GROUP_NAME'],
                DeliverLogsPermissionArn=environ['ROLE_ARN'],
            )

            print('Created Flow Logs: ' + response['FlowLogIds'][0])

    except Exception as e:
        print('Error - reason "%s"' % str(e))
