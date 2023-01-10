import os
import re
import subprocess
from typing import TextIO
import boto3
from pygit2 import Repository
# noinspection PyPackageRequirements
from decouple import config


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
    s3_directory: str = os.path.dirname(os.path.realpath(__file__)) + '/s3'
    terraform(mode='apply', directory=s3_directory)


def create_backend(bucket: str, key: str, region: str = 'us-east-2'):
    print('creating backend.tf')

    f: TextIO = open('backend.tf', 'w')
    f.write('terraform {\n')
    f.write('  backend "s3" {\n')
    f.write('    bucket = "' + bucket + '"\n')
    f.write('    key    = "' + key + '"\n')
    f.write('    region = "' + region + '"\n')
    f.write('  }\n')
    f.write('}\n')
    f.close()


def terraform(mode: str = 'plan', directory: str = './'):
    # todo - load .tfvars
    # todo - protect against non-head reruns
    start_directory: str = os.getcwd()
    drift: int = 0
    os.chdir(directory)
    os.system('terraform init')

    if mode in ('plan', 'check', 'apply'):
        os.system('terraform validate')

    if mode in ('plan', 'apply'):
        os.system('terraform plan -out=terraform.tfplan')

    if mode == 'apply':
        os.system('terraform apply --auto-approve terraform.tfplan')

    if mode in ('apply', 'check'):
        drift = int(os.system('terraform plan --detailed-exitcode'))

    if mode == 'apply' and drift != 0:
        print('your terraform configuration is not idempotent')
        exit()

    if mode == 'check' and drift != 0:
        print('your terraform configuration has drifted')
        exit()

    if mode == 'destroy':
        os.system('terraform destroy --auto-approve')

    os.chdir(start_directory)


def get_repo_name() -> str:
    result = subprocess.check_output('git remote get-url origin', shell=True, text=True).strip()
    url = result.removesuffix('.git')
    name = re.sub('.*/', '', url)
    return name


def get_mode(job: str, workflow: str = None) -> str:
    valid_modes: tuple = ('plan', 'apply', 'check', 'destroy')

    if job in valid_modes:
        return job

    if workflow in valid_modes:
        return workflow

    return 'plan'


def main():
    prefix: str = config('BACKEND_PREFIX', default='terraform-backend', cast=str)
    workflow: str = config('GITHUB_WORKFLOW', default='main', cast=str)
    job: str = config('GITHUB_JOB', default='main', cast=str)
    mode: str = config('MODE', default=get_mode(job, workflow), cast=str)
    bucket: str = find_bucket(prefix)
    repo: str = get_repo_name()
    branch: str = Repository('.').head.shorthand
    key: str = repo + '/' + branch + '.json'  # .json helps with manually manipluating state files in S3
    os.environ["TF_INPUT"] = "false"
    os.environ["TF_IN_AUTOMATION"] = "true"
    os.environ["TF_VAR_name"] = repo
    os.environ["TF_VAR_branch"] = branch

    if bucket == '':
        # this block might need a locking mechanism
        create_bucket()  # todo - return bucket name to avoid second find
        bucket: str = find_bucket(prefix)

    create_backend(bucket, key)
    terraform(mode)

    # todo - rich output
    # todo - display clickable URLs


main()
