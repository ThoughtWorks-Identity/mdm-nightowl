import os
import sys
reload(sys)
sys.setdefaultencoding('utf8')
from sys import argv
from jinja2 import *
import boto3
import hashlib

def Create_Signed_URL(bucket, item, expirytime):
    s3Client = boto3.client('s3')
    s3Resource = boto3.resource('s3')
    presigned_item = s3Client.generate_presigned_url('get_object', Params = {'Bucket': bucket, 'Key': item}, ExpiresIn = expirytime)
    return presigned_item

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
    bucket = "tw-dep-installapplications-test"
    expirytime = 60*60*24*7
    working_directory = os.path.dirname(os.path.abspath(__file__))
    env = Environment(loader=FileSystemLoader(working_directory))
    template = env.get_template('bootstrap_prod.template')
    filename = "bootstrap_prod.json"

    ias_file_output = {
                    "DEP_Notify_hash": gethash(bucket, "setupassistant", "DEPNotify-1.0.4.pkg", ),
                    "DEP_Notify_signed_URL": Create_Signed_URL(bucket, "setupassistant/DEPNotify-1.0.4.pkg", expirytime),
                    "caffeinate_hash": gethash(bucket, "userland", "caffeinate.py"),
                    "caffeinate_script": Create_Signed_URL(bucket, "userland/caffeinate.py", expirytime),
                    "enable_filevault_hash": gethash(bucket, "userland", "enable_encryption.py"),
                    "enable_filevault": Create_Signed_URL(bucket, "userland/enable_encryption.py", expirytime),
                    "install_sophos_hash": gethash(bucket, "userland", "Sophos_for_deployments-20180207.pkg"),
                    "install_sophos": Create_Signed_URL(bucket, "userland/Sophos_for_deployments-20180207.pkg", expirytime),
                    }

    outputfile = open(filename, 'w')
    outputfile.write(template.render(ias_file_output))
    outputfile.close

    print("all done")

if __name__ == "__main__":
    main()
