# aws-transcribe

Simple AWS Template for an API transcribing mp3 and wav files and checking if provided sentences appear in it.

## Requirements

* AWS CLI already configured with at least PowerUser permission

* [Python 3 installed](https://www.python.org/downloads/)

* [Docker installed](https://www.docker.com/community-edition)
* [SAM Local installed](https://github.com/awslabs/aws-sam-local)


### Build Your Application

When you make a change to the code, you can run the following command to install dependencies
and convert your Lambda function source code into an artifact that can be deployed and run on Lambda.

```bash
sam build
```

## Deployment

First and foremost, we need a S3 bucket where we can upload our Lambda functions packaged as ZIP before we deploy anything - If you don't have a S3 bucket to store code artifacts then this is a good time to create one:

```bash
aws s3 mb s3://BUCKET_NAME
```

Now build your Lambda function

```bash
sam build --use-container
```

Provided you have a S3 bucket created, run the following command to package our Lambda function to S3:

```bash
sam package \
    --output-template-file packaged.yaml \
    --s3-bucket BUCKET_NAME
```

Next, the following command will create a Cloudformation Stack and deploy your SAM resources.

```bash
sam deploy \
    --template-file packaged.yaml \
    --stack-name transcribeAudio \
    --capabilities CAPABILITY_IAM
```
