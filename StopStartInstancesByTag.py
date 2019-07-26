from boto3 import client, session, resource
from logging import getLogger, info, error
from os import environ
from datetime import datetime, tzinfo

REGION = environ['REGION']
TAG = environ['TAG']
TAG_VALUE = environ['TAG_VALUE']
ACTION = environ['ACTION'] #stop on start

TAG = 'tag:%s' %TAG



class StartStopEc2(object):
    
    def __init__(self):
        """
        Function for Starting and Stop EC2
        """
        logger = getLogger()
        logger.setLevel("INFO")

        self.client_ec2 = client('ec2', region_name=REGION)
        
        self.running = set()
        self.pending = set()
        self.shuttingdown = set()
        self.stopping = set()
        self.stopped = set()
        
    
    def _getEc2status(self):
        """
        :return: 
        """
        Filters = [
            {
                'Name': TAG,
                'Values': [TAG_VALUE]
            }
        ]

        try:

            response = self.client_ec2.describe_instances(Filters=Filters)
            info(response)
            for reservation in response['Reservations']:
                instances = reservation['Instances']
                for instance in instances:
                    print(instance['InstanceId'], instance['State']['Name'], '\n')
                    instance_id = instance['InstanceId']
                    instance_state = instance['State']['Name']

                    if instance_state == 'pending':
                        self.pending.add(instance_id)
                    elif instance_state == "running":
                        self.running.add(instance_id)
                    elif instance_state == "shutting-down":
                        self.shuttingdown.add(instance_id)
                    elif instance_state == "terminated":
                        self.terminated.add(instance_id)
                    elif instance_state == "stopping":
                        self.stopping.add(instance_id)
                    elif instance_state == "stopped":
                        self.stopped.add(instance_id)
        except Exception as err:
            error(err)


    def stopEc2(self):
        """
        Stop EC2
        :return: 
        """
        try:
            self.client_ec2.stop_instances(InstanceIds=list(self.running))
            info("stoppen instances" + str(self.running))
        except Exception as err:
            error(err)

    
    def startEc2(self):
        """
        Start Ec2
        :return: 
        """
        try:
            self.client_ec2.start_instances(InstanceIds=list(self.stopped))
            info("stoppend instances" + str(self.running))
        except Exception as err:
            error(err)

def lambda_handler(event, context):
    instances = StartStopEc2()
    instances._getEc2status()
    
    if ACTION.lower() == "stop":
        # Stop instances
        info("Stopping Instances...")
        instances.stopEc2()
    elif ACTION.lower() == "start":
        # Start instances
        info("Starting Instances...")
        instances.startEc2()
