import os
import sys
from sys import argv
import jinja2
import boto3
import hashlib
import json
import re

s3_bucket = os.environ.get('INSTALLAPPLICATIONS_S3_BUCKET')
bootstrap_template = os.environ.get('BOOTSTRAP_TEMPLATE')
bootstrap_file = os.environ.get('BOOTSTRAP_FILE')
s3_client = boto3.client('s3')
lambda_task_root = os.environ.get('LAMBDA_TASK_ROOT')


def Create_Signed_URL(s3_bucket, item, expirytime):
    return s3_client.generate_presigned_url('get_object', Params = {'Bucket': s3_bucket, 'Key': item}, ExpiresIn = expirytime)

#Hashing function borrowed from the installapplications generate json code. Which makes sense as I want a hash which works with InstallApplications
#Tweaked by me to include some boto3 magic.

def gethash(s3_bucket, folder, filename):
    hash_function = hashlib.sha256()
    localfilename = "/tmp/" + filename
    print("downloading {}/{}/{}".format(s3_bucket, folder, filename))
    s3_client.download_file(s3_bucket, "{}/{}".format(folder, filename), localfilename)

    if not os.path.isfile(localfilename):
        return 'NOT A FILE'

    fileref = open(localfilename, 'rb')
    while 1:
        chunk = fileref.read(2**16)
        if not chunk:
            break
        hash_function.update(chunk)
    fileref.close()
    os.remove(localfilename)

    return hash_function.hexdigest()


def lambda_handler(event, context):
    #Variables
    # s3_bucket = "tw-dep-installapplications-dev"
    expirytime = 60*60*24*7
    
    working_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    templateLoader = jinja2.FileSystemLoader(searchpath=working_directory)
    templateEnv = jinja2.Environment(loader=templateLoader)
    template = templateEnv.get_template(bootstrap_template)
    filename = "/tmp/" + bootstrap_file
    
    # ias_file_output = {
    #                 "DEP_Notify_hash": gethash(s3_bucket, "setupassistant", "DEPNotify-beta-1.2.pkg", ),
    #                 "DEP_Notify_signed_URL": Create_Signed_URL(s3_bucket, "setupassistant/DEPNotify-beta-1.2.pkg", expirytime),
    #                 "caffeinate_hash": gethash(s3_bucket, "userland", "caffeinate.py"),
    #                 "caffeinate_script": Create_Signed_URL(s3_bucket, "userland/caffeinate.py", expirytime),
    #                 "enable_filevault_hash": gethash(s3_bucket, "userland", "enable_encryption.py"),
    #                 "enable_filevault": Create_Signed_URL(s3_bucket, "userland/enable_encryption.py", expirytime),
    #                 "install_sophos_hash": gethash(s3_bucket, "userland", "Sophos_for_deployments-20180821.pkg"),
    #                 "install_sophos": Create_Signed_URL(s3_bucket, "userland/Sophos_for_deployments-20180821.pkg", expirytime),
    #                 "high_sierra_vm_bless_hash": gethash(s3_bucket, "userland", "high_sierra_vm_bless.py"),
    #                 "high_sierra_vm_bless_url": Create_Signed_URL(s3_bucket, "userland/high_sierra_vm_bless.py", expirytime),
    #                 "VMWare_tools_hash": gethash(s3_bucket, "userland", "VMware_Tools.pkg"),
    #                 "VMWare_tools_url": Create_Signed_URL(s3_bucket, "userland/VMware_Tools.pkg", expirytime),
    #                 }
    
    ias_file_output = {}
    with open(bootstrap_template, 'r') as f:
        json_template = json.load(f)
        bad_chars = r"[\s\"\{\}]"
        for sa in json_template['setupassistant']:
            base_filename = os.path.basename(sa['file'])
            key = re.sub(bad_chars, '', sa['hash'])
            ias_file_output[key] = gethash(s3_bucket, "setupassistant",  base_filename)
            key = re.sub(bad_chars, '', sa['url'])
            ias_file_output[key] = Create_Signed_URL(s3_bucket, "setupassistant/{}".format(base_filename), expirytime)
        for ul in json_template['userland']:
            base_filename = os.path.basename(ul['file'])
            key = re.sub(bad_chars, '', ul['hash'])
            ias_file_output[key] = gethash(s3_bucket, "userland",  base_filename)
            key = re.sub(bad_chars, '', ul['url'])
            ias_file_output[key] = Create_Signed_URL(s3_bucket, "userland/{}".format(base_filename), expirytime)

    outputfile = open(filename, 'w')
    complete = template.render(ias_file_output)
    outputfile.write(complete)
    outputfile.close()
    
    print("Uploading {} to {}".format(filename, s3_bucket))
    s3_client.upload_file(filename, s3_bucket, bootstrap_file)
