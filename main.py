import os
import re
import subprocess
from typing import TextIO
import boto3
from pygit2 import Repository


def find_bucket(prefix: str = 'terraform-backend') -> str:
    print('finding s3 bucket')

    s3 = boto3.client('s3')
    response = s3.list_buckets()
    matched_buckets = []

    for bucket in response['Buckets']:
        if bucket["Name"].startswith(prefix):
            matched_buckets.append(bucket["Name"])

    if len(matched_buckets) < 1:
        print('No bucket found')
        return ''

    if len(matched_buckets) > 1:
        print('Multiple buckets found: ', matched_buckets)

    return matched_buckets.pop()


def create_bucket():
    # todo - accept prefix
    # todo - return bucket name
    # todo - test
    print('creating bucket')

    apply(os.path.dirname(os.path.realpath(__file__)) + '/s3')


def create_backend(bucket: str, key: str, region: str = 'us-east-2'):
    print('creating backend.tf')

    f: TextIO = open('backend.tf', 'w')
    f.write('terraform {\n')
    f.write('  backend "s3" {\n')
    f.write('    bucket = "' + bucket + '"\n')
    f.write('    key    = "' + key + '.json"\n')
    f.write('    region = "' + region + '"\n')
    f.write('  }\n')
    f.write('}\n')
    f.close()


def apply(directory: str = './'):
    # todo - load .tfvars
    # todo - protect against github reruns
    print('applying terraform configuration')

    start_directory: str = os.getcwd()

    os.chdir(directory)
    os.system('terraform init')
    os.system('terraform validate')
    os.system('terraform plan -out=terraform.tfplan')
    os.system('terraform apply --auto-approve terraform.tfplan')
    os.chdir(start_directory)


def get_repo_name() -> str:
    result = subprocess.check_output('git remote get-url origin', shell=True, text=True).strip()
    url = result.removesuffix('.git')
    name = re.sub('.*/', '', url)
    return name


def main():
    prefix: str = 'terraform-backend'
    bucket: str = find_bucket(prefix)
    repo: str = get_repo_name()
    branch: str = Repository('.').head.shorthand
    key: str = repo + '/' + branch
    os.environ["TF_INPUT"] = "false"
    os.environ["TF_IN_AUTOMATION"] = "true"
    os.environ["TF_VAR_name"] = repo
    os.environ["TF_VAR_branch"] = branch

    if bucket == '':
        # this block might need a locking mechanism
        create_bucket()  # todo - return bucket name to avoid second find
        bucket: str = find_bucket(prefix)

    create_backend(bucket, key)

    # todo - switch function based on github job name
    # todo - allow overrides for explicit calls and local execution
    apply()

    # todo - rich output
    # todo - display clickable URLs


main()
