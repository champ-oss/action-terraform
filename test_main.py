from main import *
import os
import inspect

test_directory = '.test'
test_hcl = 'resource "random_pet" "this" {}'


def setup():
    try:
        os.mkdir(test_directory)
    except FileExistsError:
        print(test_directory + ' already exists')


def clean():
    os.remove(test_directory)


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

    # assert hello() == 'hello'
    return


def test_apply_returns():
    # create test dir

    # create test main.tf

    # call apply

    # assert hello() == 'hello'
    return
