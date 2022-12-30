import os

import boto3


def connect_backend(prefix: str = 'terraform-backend'):
    bucket = find_bucket(prefix)

    if bucket == '':
        bucket = create_bucket(prefix)

    create_backend(bucket)


def find_bucket(prefix: str = 'terraform-backend') -> str:
    print('finding s3 bucket')

    s3 = boto3.client('s3')
    response = s3.list_buckets()
    matched_buckets = []

    for bucket in response['Buckets']:
        if bucket["Name"].startswith(prefix):
            matched_buckets.append(bucket)

    if len(matched_buckets) < 1:
        print('No bucket found')
        return ''

    if len(matched_buckets) > 1:
        print('Multiple buckets found: ', matched_buckets)

    return matched_buckets.pop()


def create_bucket():
    print('creating bucket')
    apply(os.path.dirname(os.path.realpath(__file__)) + '/s3')


def create_backend(bucket: str = 'terraform-backend') -> str:
    print('creating backend.tf')
    return bucket


def apply(directory: str = './'):
    print('applying terraform configuration')
    start_directory = os.getcwd()
    os.chdir(directory)
    os.system('terraform init')
    os.system('terraform validate')
    os.system('terraform plan -out=terraform.tfplan')
    os.system('terraform apply --auto-approve terraform.tfplan')
    os.chdir(start_directory)


def main():
    connect_backend()
    apply()


main()
