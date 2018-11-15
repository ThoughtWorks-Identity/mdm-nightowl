Automating generating pre-signed URLS for installapplications
---

We're using [installapplications](https://github.com/erikng/installapplications) to get over limitations in the `installapplication` MDM command - and to allow for some smarter more dynamic MDM setup workflows.

Scripts and packages are hosted in S3. We don't want these items to be public, so we restrict access using AWS pre-signed URLS.

### Pre-signed URLs

This code includes a `boto3` function to generate pre-signed URLs.

### As a Lambda

The scripts use a Lambda architecture, using Serverless Framework. The Lambda functions will be run periodically to generate signed bootstrap files.

### S3 bucket

There are S3 buckets for each of dev and prod. These are manually created and populated with the required packages.
