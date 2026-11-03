import boto3
import json
import os
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

def load_aws_secrets(secret_name="prod/orbit", region_name="us-east-2"):
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=region_name)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        raise e

    secret = get_secret_value_response["SecretString"]
    secrets_dict = json.loads(secret)

    for key, value in secrets_dict.items():
        os.environ[key] = value