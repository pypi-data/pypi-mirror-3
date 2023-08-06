import pprint

from scalymongo import Document, Connection

class FindExample(Document):
    structure = {
        'name': basestring,
        'age': int,
        'crap': {basestring: int},
    }

    __database__ = 'test'
    __collection__ = __file__


def find():
    return conn.models.FindExample.find()

def render(cursor):
    print '=' * 80
    f = list(cursor)
    print [type(x) for x in f]
    pprint.pprint(f)

def main():

    docs = [
        {'name': 'Alice', 'age': 32},
        {'name': 'Bob', 'age': 32},
        {'name': 'Carl', 'age': 41},
        {'name': 'Donna', 'age': 35},
        {'name': 'Earl', 'crap': {1:2, 2:3}},
    ]
    docs = [conn.models.FindExample(doc) for doc in docs]
    for doc in docs:
        doc.save()

    print 'all'
    render(find())
    print '[2:3]'
    render(find()[2:3])
    print 'limit(1)'
    render(find().limit(1))
    print '[0:1]'
    render(find()[0:1])
    print 'skip(2)'
    render(find().skip(2))


if __name__ == '__main__':
    conn = Connection('localhost')
    conn.models.FindExample.remove({})
    main()
    conn.models.FindExample.remove({})
