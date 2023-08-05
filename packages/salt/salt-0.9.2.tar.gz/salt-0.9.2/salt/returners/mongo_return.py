'''
Return data to a mongodb server

This is the default interface for returning data for the butter statd subsytem
'''

import logging
import pymongo

log = logging.getLogger(__name__)

__opts__ = {
            'mongo.host': 'salt',
            'mongo.port': 27017,
            'mongo.db': 'salt',
            'mongo.user': '',
            'mongo.password': '',
           }

def returner(ret):
    '''
    Return data to a mongodb server
    '''
    conn = pymongo.Connection(
            __opts__['mongo.host'],
            __opts__['mongo.port'],
            )
    db = conn[__opts__['mongo.db']]

    user = __opts__.get('mongo.user')
    password = __opts__.get('mongo.password')
    if user and password:
        db.authenticate(user, password)

    col = db[ret['id']]
    back = {}
    if type(ret['return']) == type(dict()):
        for key in ret['return']:
            back[key.replace('.', '-')] = ret['return'][key]
    else:
        back = ret['return']
    log.debug( back )
    col.insert({ret['jid']: back})
