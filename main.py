import logging

import boto3


def connect_backend(prefix: str = 'terraform-backend'):
    bucket = find_bucket(prefix)

    if bucket == '':
        bucket = create_bucket(prefix)

    return create_backend(bucket)


def find_bucket(prefix: str = 'terraform-backend'):
    s3 = boto3.client('s3')
    response = s3.list_buckets()
    matched_buckets = []

    logging.debug(response)

    for bucket in response['Buckets']:
        if bucket["Name"].startswith(prefix):
            matched_buckets.append(bucket)

    if len(matched_buckets) < 1:
        print('No bucket found')
        return ''

    if len(matched_buckets) > 1:
        print('Multiple buckets found: ', matched_buckets)
        return ''

    return matched_buckets.pop()


def create_bucket(prefix: str = 'terraform-backend'):
    print('create bucket')
    return prefix


def create_backend(bucket: str = 'terraform-backend'):
    return bucket


def apply():
    return


def main():
    connect_backend()
    apply()


main()
