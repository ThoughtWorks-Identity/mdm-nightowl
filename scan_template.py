import json
import os
from pprint import pprint

def main():
	template_dict = {}
	bucket = "tw-dep-installapplications-dev"

	with open('bootstrap_dev.template', 'r') as f:
		template = json.load(f)
		for sa in template['setupassistant']:
			base_filename = os.path.basename(sa['file'])
			template_dict[sa['hash']] = 'gethash(bucket, "setupassistant",  base_filename)'
			template_dict[sa['url']] = 'Create_Signed_URL(bucket, "userland/{}".format(base_filename), expirytime)'
		for ul in template['userland']:
			base_filename = os.path.basename(ul['file'])
			template_dict[ul['hash']] = 'gethash(bucket, "setupassistant",  base_filename)'
			template_dict[ul['url']] = 'Create_Signed_URL(bucket, "userland/{}".format(base_filename), expirytime)'
	pprint(template_dict)

if __name__ == "__main__":
    main()