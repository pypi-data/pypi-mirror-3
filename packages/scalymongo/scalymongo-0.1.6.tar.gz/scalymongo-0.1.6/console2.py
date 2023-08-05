import pprint

from scalymongo import Document, IS

class Person(Document):
    structure = {
        'name': IS('Allan', 'Bob')
    }


if __name__ == '__main__':
    Person(name='Allan').validate()
    Person().validate()
