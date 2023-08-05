# -*- coding: utf-8 -*-

def query(args):
    from aliyun.rest import simple_rest_factory
    from json import loads
    from time import sleep
    from urllib import quote
    #from pprint import pprint
    post = simple_rest_factory('post')
    data = {'statement': args}
    print "Submitting query..."
    result = loads(post.request('/query/', data))
    print "Done.\n"

    get = simple_rest_factory('get')
    while True:
        result = loads(get.request('/status/%s/' % (quote(result['job_name'].encode('utf-8')).replace('/', '%252F'),)))
        #pprint(result)
        print result['status']
        if result['is_done']:
            break
        sleep(1)

    return "Job:[%s] is done. Return status:[%s]" % (result['job_name'], result['status'])

def myfunc(args):
    print "qwerasdfasdfasdfasf"
    return "from moye myfunc"

def go_moye(args):
    return "I am ready to GO!"
