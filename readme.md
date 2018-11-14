Automating generating pre-signed URLS for installapplications
---

We're using [installapplications](https://github.com/erikng/installapplications) to get over limitations in the `installapplication` MDM command - and to allow for some smarter more dynamic MDM setup workflows.

Scripts and packages are hosted in S3. We don't want these items to be public, so restrict access using AWS pre-signed URLS.

### Pre-signed URLS

This code includes a `boto3` function to generate pre-signed URLs when fed a suitable

Apple configuration profiles and Munki manifests are structured XML.

[Jinja](http://jinja.pocoo.org/) is a Python templating engine. You provide a template, and in my basic example I'm marking the tags I want to change  

`{{ Like_This }}`  

Then we define our signed URLS

You'll need to install the Jinja libraries to use this code. This can be done using python easy_install... (but you should really use a virtualenv!)


There's no proper error handling I'm afraid, it was just designed to be a quick and dirty fix for a problem I needed to solve!

### As a Lambda

The scripts use a lambda architecture, using Serverless Framework. The Lambda functions will be run periodically to generate signed bootstrap files.


### S3 bucket

There are S3 buckets for each of dev and prod in the AWS Identity MDM accounts. These are manually created and populated with the required packages.
