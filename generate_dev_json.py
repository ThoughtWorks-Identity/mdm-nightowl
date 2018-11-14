import os
import sys
from sys import argv
from jinja2 import *
import boto3
import hashlib

def Create_Signed_URL(bucket, item, expirytime):
    s3Client = boto3.client('s3')
    s3Resource = boto3.resource('s3')

    return s3Client.generate_presigned_url('get_object', Params = {'Bucket': bucket, 'Key': item}, ExpiresIn = expirytime)

#Hashing function borrowed from the installapplications generate json code. Which makes sense as I want a hash which works with InstallApplications
#Tweaked by me to include some boto3 magic.

def gethash(bucket, folder, filename):
    hash_function = hashlib.sha256()
    s3 = boto3.client('s3')
    print("downloading {}/{}/{}".format(bucket, folder, filename))
    s3.download_file(bucket, "{}/{}".format(folder, filename), filename)

    if not os.path.isfile(filename):
        return 'NOT A FILE'

    fileref = open(filename, 'rb')
    while 1:
        chunk = fileref.read(2**16)
        if not chunk:
            break
        hash_function.update(chunk)
    fileref.close()
    os.remove(filename)

    return hash_function.hexdigest()


def main():
    #Variables
    bucket = "tw-dep-installapplications-dev"
    expirytime = 60*60*24*7
    working_directory = os.path.dirname(os.path.abspath(__file__))
    env = Environment(loader=FileSystemLoader(working_directory))
    template = env.get_template('bootstrap_dev.template')
    filename = "bootstrap_dev.json"

    ias_file_output = {
                    "DEP_Notify_hash": gethash(bucket, "setupassistant", "DEPNotify-beta-1.2.pkg", ),
                    "DEP_Notify_signed_URL": Create_Signed_URL(bucket, "setupassistant/DEPNotify-beta-1.2.pkg", expirytime),
                    "caffeinate_hash": gethash(bucket, "userland", "caffeinate.py"),
                    "caffeinate_script": Create_Signed_URL(bucket, "userland/caffeinate.py", expirytime),
                    "enable_filevault_hash": gethash(bucket, "userland", "enable_encryption.py"),
                    "enable_filevault": Create_Signed_URL(bucket, "userland/enable_encryption.py", expirytime),
                    "install_sophos_hash": gethash(bucket, "userland", "Sophos_for_deployments-20180821.pkg"),
                    "install_sophos": Create_Signed_URL(bucket, "userland/Sophos_for_deployments-20180821.pkg", expirytime),
                    "high_sierra_vm_bless_hash": gethash(bucket, "userland", "high_sierra_vm_bless.py"),
                    "high_sierra_vm_bless_url": Create_Signed_URL(bucket, "userland/high_sierra_vm_bless.py", expirytime),
                    "VMWare_tools_hash": gethash(bucket, "userland", "VMware_Tools.pkg"),
                    "VMWare_tools_url": Create_Signed_URL(bucket, "userland/VMware_Tools.pkg", expirytime),
                    }

    outputfile = open(filename, 'w')
    outputfile.write(template.render(ias_file_output))
    outputfile.close

    print("all done")

if __name__ == "__main__":
    main()
