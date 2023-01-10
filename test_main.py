from main import *
import os
import inspect
import shutil

test_root: str = os.getcwd()
test_directory: str = test_root + '/.test/'
test_hcl: str = 'resource "random_pet" "this" {}\n'


def setup():
    try:
        os.mkdir(test_directory)
    except FileExistsError:
        print(test_directory + ' already exists')


def teardown():
    os.chdir(test_root)

    # noinspection PyBroadException
    try:
        shutil.rmtree(test_directory)
        shutil.rmtree('.terraform')
        os.remove('terraform.tfplan')
        os.remove('backend.tf')
    except Exception:
        pass


def create_test_directory() -> str:
    calling_function: str = inspect.stack()[1].function
    directory: str = test_directory + calling_function

    try:
        os.mkdir(directory)
    except FileExistsError:
        print(directory + ' already exists')

    f = open(directory + '/main.tf', 'w')
    f.write(test_hcl)
    f.close()

    return directory


def test_apply():
    directory: str = create_test_directory()

    apply(directory)
    os.chdir(directory)
    assert os.system('terraform plan --detailed-exitcode') == 0
    os.chdir(test_root)


def test_terraform_returns():
    # noinspection PyBroadException
    try:
        terraform(directory=create_test_directory())
    except Exception:
        pass  # we are only testing current working directory behavior

    assert os.getcwd() == test_root
    os.chdir(test_root)


def test_backend_is_valid():
    os.chdir(create_test_directory())
    os.system('terraform init')
    create_backend('this', 'that')
    assert os.system('terraform validate') == 0
    os.chdir(test_root)


def test_backend_is_formatted():
    os.chdir(create_test_directory())
    create_backend('this', 'that')
    assert os.system('terraform fmt -check') == 0
    os.chdir(test_root)


def test_get_repo_name():
    assert get_repo_name() == 'action-terraform'


def test_get_mode():
    assert get_mode('main') == 'plan'
    assert get_mode('blah') == 'plan'
    assert get_mode('check') == 'check'
    assert get_mode('main', 'apply') == 'apply'
    assert get_mode('apply', 'blah') == 'apply'
    assert get_mode('blah', 'apply') == 'apply'
