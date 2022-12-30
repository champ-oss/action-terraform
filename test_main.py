from main import *
import os
import inspect
import shutil

test_root = os.path.dirname(os.path.realpath(__file__))
test_directory = '.test'
test_hcl = 'resource "random_pet" "this" {}'


def setup():
    try:
        os.mkdir(test_directory)
    except FileExistsError:
        print(test_directory + ' already exists')


def teardown():
    os.chdir(test_root)
    shutil.rmtree(test_directory)


def create_test_directory():
    calling_function = inspect.stack()[1].function
    directory = '.test/' + calling_function

    try:
        os.mkdir(directory)
    except FileExistsError:
        print(directory + ' already exists')

    f = open(directory + '/main.tf', 'w')
    f.write(test_hcl)
    f.close()

    return directory


def test_apply():
    directory = create_test_directory()
    apply(directory)
    os.chdir(directory)
    assert os.system('terraform plan --detailed-exitcode') == 0
    os.chdir(test_root)


def test_apply_returns():
    directory = create_test_directory()
    start_directory = os.getcwd()

    # noinspection PyBroadException
    try:
        apply(directory)
    except Exception:
        pass  # we are only testing current working directory behavior

    assert os.getcwd() == start_directory
    os.chdir(test_root)
