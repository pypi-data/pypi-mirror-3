from __init__ import Stache, render
import timeit

def bare(output, template, data):
    return Stache().render(template, data)

def test(method=bare):
    yield method, 'a10c', 'a{{b}}c', dict(b=10)
    yield method, 'a10c', 'a{{b}}c', dict(b=10)
    yield method, 'ac', 'a{{b}}c', dict(c=10)
    yield method, 'a10c', 'a{{b}}c', dict(b='10')
    yield method, 'acde', 'a{{!b}}cde', dict(b='10')
    yield method, 'aTrue', 'a{{b}}', dict(b=True)
    yield method, 'a123', 'a{{b}}{{c}}{{d}}', dict(b=1,c=2,d=3)
    yield method, 'ab', 'a{{#b}}b{{/b}}', dict(b=True)
    yield method, 'a', 'a{{^b}}b{{/b}}', dict(b=True)
    yield method, 'a', 'a{{#b}}b{{/b}}', dict(b=False)
    yield method, 'ab', 'a{{^b}}b{{/b}}', dict(b=False)
    yield method, 'ab', 'a{{^b}}b{{/b}}', dict(b=[])
    yield method, 'abbbb', 'a{{#b}}b{{/b}}', dict(b=[1,2,3,4])
    yield method, 'a1234', 'a{{#b}}{{.}}{{/b}}', dict(b=[1,2,3,4])
    yield method, 'a a=1 a=2 a=0 ', 'a {{#b}}a={{a}} {{/b}}', dict(a=0,b=[{'a':1},{'a':2},{'c':1}])
    yield method, '1', '{{#a}}{{#b}}{{c}}{{/b}}{{/a}}', dict(a={'b':{'c':1}})
    yield method, '12', '{{#a}}{{#b}}{{c}}{{/b}}{{/a}}', dict(a={'b':[{'c':1}, {'c':2}]})
    yield method, '12', '{{#a}}{{#b}}{{c}}{{/b}}{{/a}}', dict(a=[{'b':{'c':1}},{'b':{'c':2}}])
    yield method, '132', '{{#a}}{{#b}}{{c}}{{/b}}{{/a}}', dict(a=[{'b':[{'c':1}, {'c':3}]},{'b':{'c':2}}])
    yield method, '132456', '{{#a}}{{#b}}{{c}}{{/b}}{{/a}}', dict(a=[{'b':[{'c':1}, {'c':3}]},{'b':{'c':2}},{'b':[{'c':4}, {'c':5}]},{'b':{'c':6}}])
    yield method, '1', '{{#a}}{{#a}}{{c}}{{/a}}{{/a}}', dict(a={'a':{'c':1}})
    yield method, 'delim{{}}', '{{=<% %>=}}<%a%>{{}}', dict(a='delim')
    yield method, '<3><3><3>', '<{{id}}><{{# has_a? }}{{id}}{{/ has_a? }}><{{# has_b? }}{{id}}{{/ has_b? }}>', {'id':3,'has_a?':True, 'has_b?':True}


def verify(output, template, data):
    print "%s with %s" % (template, data)
    result = Stache().render(template, data)
    print "Result: %s\n" % result
    assert result == output

def bencher(output, template, data):
    t = timeit.Timer("Stache().render('%s', %s)" % (template, data), "from __main__ import Stache")
    print "%.2f\tusec/pass\t%s with %s" % (1000000 * t.timeit(number=10000)/10000, template, data)

if __name__ == '__main__':
    print 'starting tests'
    for x in test(verify): x[0](*x[1:])
    print 'finished tests'
    print 'starting individual benchmarks'
    for x in test(bencher): x[0](*x[1:])
    print 'starting combined benchmark'
    t = timeit.Timer("for x in test(bare): x[0](*x[1:])", "from __main__ import test, bare")
    print "%.2f\tusec/pass" % (1000000 * t.timeit(number=10000)/10000)
