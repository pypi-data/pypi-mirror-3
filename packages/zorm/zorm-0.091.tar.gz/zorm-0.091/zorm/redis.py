#coding:utf-8
from intstr import IntStr

redis_keyer = IntStr(
'!"#$%&()+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ\\^_`abcdefghijklmnopqrstuvwxyz{|}~'
)

REDIS_KEY_ID = 'RedisKeyId'
REDIS_KEY = 'RedisKey'
REDIS_ID_KEY = 'RedisIdKey'

_EXIST = set()

class RedisKey(object):
    def __init__(self, redis):
        self.redis = redis

    def __getattr__(self, attr):
        redis = self.redis
        def _(name=''):
            key = attr+name
            if key in _EXIST:
                raise Exception('redis key is already defined %s'%key)
            _EXIST.add(key)
            if redis:
                _key = redis.hget(REDIS_KEY, key)
                if _key is None:
                    id = redis.incr(REDIS_KEY_ID)
                    _key = redis_keyer.encode(id)+"'"+name
                    p = redis.pipeline()
                    p.hset(REDIS_KEY, key, _key)
                    p.hset(REDIS_ID_KEY, _key, key)
                    p.execute()
                return _key

        return _


from zorm.config import redis
redis_key = RedisKey(redis)

if __name__ == '__main__':
    pass
