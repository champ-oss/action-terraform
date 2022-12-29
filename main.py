import logging

import boto3


def connect_backend(prefix: str = 'terraform-backend'):
    bucket = find_bucket(prefix)

    if bucket == '':
        bucket = create_bucket(prefix)

    create_backend(bucket)
    return


def find_bucket(prefix: str = 'terraform-backend'):
    logging.info('finding s3 bucket')

    s3 = boto3.client('s3')
    response = s3.list_buckets()
    matched_buckets = []

    for bucket in response['Buckets']:
        if bucket["Name"].startswith(prefix):
            matched_buckets.append(bucket)

    if len(matched_buckets) < 1:
        logging.info('No bucket found')
        return ''

    if len(matched_buckets) > 1:
        logging.error('Multiple buckets found: ', matched_buckets)
        exit()

    return matched_buckets.pop()


def create_bucket(prefix: str = 'terraform-backend'):
    logging.info('creating bucket')
    return prefix


def create_backend(bucket: str = 'terraform-backend'):
    logging.info('creating backend.tf')
    return bucket


def apply():
    logging.info('applying terraform configuration')
    return


def main():
    logging.basicConfig(level=logging.INFO)
    connect_backend()
    apply()


main()
