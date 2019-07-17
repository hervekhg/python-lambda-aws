from boto3 import client, session, resource
from logging import getLogger, info
from os import environ
from datetime import datetime, tzinfo


BUCKET = environ['BUCKET']
REGION = environ['REGION']

OLD_PREFIX = environ['OLD_PREFIX']
NEW_PREFIX = environ['NEW_PREFIX']


class RenameFileOnS3(object):

    def __init__(self):
        """
        Initialisation
        """
        logger = getLogger()
        logger.setLevel("INFO")

        self.client_s3 = client('s3', region_name=REGION)
        self.files = dict()

        self.getIsOK = False
        self.createIsOK = False


    def getlistfile(self):
        """
        :return:
        """
        resp = self.client_s3.list_objects_v2(
            Bucket=BUCKET,
            Prefix=OLD_PREFIX

        )
        for obj in resp['Contents']:
            key = obj['Key']
            info("Get File: %s" %key)
            extension = key.split(".")[-1]

            aaaammjj = key.split("_")[-1].split(".")[0]
            aaaa = aaaammjj[0:4]
            mm = aaaammjj[4:6]
            jj = aaaammjj[6:8]

            new_key="%s%s%s%s.%s" %(NEW_PREFIX, jj, mm, aaaa, extension)

            self.files[key] = new_key
            self.getIsOK = True

    def createnewfile(self):
        """
        Create New File on Bucket
        :return:
        """

        for key, new_key in self.files.items():
            source = "%s/%s" %(BUCKET, key)
            response = self.client_s3.copy_object(
                Bucket=BUCKET,
                CopySource=source,
                Key=new_key
            )
        self.createIsOK = True

    def deletenewfile(self):
        """
        Delete Old File on Bucket
        :return:
        """
        for key, old_key in self.files.items():
            response = self.client_s3.delete_object(
                Bucket=BUCKET,
                Key=key
            )
            info("Deleting Key: %s" %key)

def lambda_handler(event, context):
    """

    :param event:
    :param context:
    :return:
    """
    rename = RenameFileOnS3()
    rename.getlistfile()
    if rename.getIsOK:
        rename.createnewfile()
        if rename.createIsOK:
            rename.deletenewfile()
