import re

from django.conf import settings

from completion.backends.base import BaseBackend
from completion.constants import MIN_LENGTH, REDIS_CONNECTION
from completion.utils import clean_phrase, create_key, partial_complete

from redis import Redis


class RedisAutocomplete(BaseBackend):
    """
    Pretty proof-of-concept-y -- autocomplete across partial matches of a title
    string.  Does not handle siteification, pub_date filtering.
    
    Check out:
    http://antirez.com/post/autocomplete-with-redis.html
    http://stackoverflow.com/questions/1958005/redis-autocomplete/1966188#1966188
    """
    def __init__(self, connection=REDIS_CONNECTION, prefix='autocomplete:',
                 terminator='^'):
        host, port, db = connection.split(':') # host:port:db
        self.host = host
        self.port = int(port)
        self.db = int(db)
        
        self.prefix = prefix
        self.terminator = terminator
        
        self.client = self.get_connection()
    
    def get_connection(self):
        return Redis(host=self.host, port=self.port, db=self.db)
    
    def flush(self):
        self.client.flushdb()
    
    def get_object_data(self, obj):
        return '%s:%s' % (str(obj._meta), obj.pk)
    
    def autocomplete_keys(self, title):
        key = create_key(title)
        
        current_key = key[:MIN_LENGTH]
        for char in key[MIN_LENGTH:]:
            yield (current_key, char, ord(char))
            current_key += char
        
        yield (current_key, self.terminator, 0)
    
    def store_object(self, obj, data):
        """
        Given a title & some data that needs to be stored, make it available
        for autocomplete via the suggest() method
        """
        title = data['title']
        
        # store actual object data
        obj_data = self.get_object_data(obj)
        self.client.set('objdata:%s' % obj_data, data['data'])
        
        # create tries using sorted sets and add obj_data to the lookup set
        for partial_title in partial_complete(title):
            # store a reference to our object in the lookup set
            self.client.sadd(create_key(partial_title), obj_data)
            
            for (key, value, score) in self.autocomplete_keys(partial_title):
                self.client.zadd('%s%s' % (self.prefix, key), value, score)
    
    def remove_object(self, obj, data):
        title = data['title']
        keys = []

        obj_data = self.get_object_data(obj)
        
        #...how to figure out if its the final item...
        for partial_title in partial_complete(title):
            # get a list of all the keys that would have been set for the tries
            autocomplete_keys = list(self.autocomplete_keys(partial_title))
            
            # flag for whether ours is the last object at this lookup
            is_last = False
            
            # grab all the members of this lookup set
            partial_key = create_key(partial_title)
            objects_at_key = self.client.smembers(partial_key)
            
            # check the data at this lookup set to see if ours was the only obj
            # referenced at this point
            if obj_data not in objects_at_key:
                # something weird happened and our data isn't even here
                continue
            elif len(objects_at_key) == 1:
                # only one object stored here, remove the terminal flag
                zset_key = '%s%s' % (self.prefix, partial_key)
                self.client.zrem(zset_key, '^')
                
                # see if there are any other references to keys here
                is_last = self.client.zcard(zset_key) == 0
            
            if is_last:
                for (key, value, score) in reversed(autocomplete_keys):
                    key = '%s%s' % (self.prefix, key)
                    
                    # another lookup ends here, so bail
                    if '^' in self.client.zrange(key, 0, -1):
                        self.client.zrem(key, value)
                        break
                    else:
                        self.client.delete(key)
                
                # we can just blow away the lookup key
                self.client.delete(partial_key)
            else:
                # remove only our object's data
                self.client.srem(partial_key, obj_data)
        
        # finally, remove the data from the data key
        self.client.delete('objdata:%s' % obj_data)
    
    def suggest(self, phrase, limit, models):
        """
        Wrap our search & results with prefixing
        """
        phrase = create_key(phrase)
        
        # perform the depth-first search over the sorted sets
        results = self._suggest('%s%s' % (self.prefix, phrase), limit)
        
        # strip the prefix off the keys that indicated they matched a lookup
        prefix_len = len(self.prefix)
        cleaned_keys = map(lambda x: x[prefix_len:], results)
        
        # lookup the data references for each lookup set
        obj_data_lookups = []
        for key in cleaned_keys:
            obj_data_lookups.extend(self.client.smembers(key))
        
        seen = set()
        data = []
        
        if models:
            valid_models = set([str(model_class._meta) for model_class in models])
        
        # grab the data for each object
        for lookup in obj_data_lookups:
            if lookup in seen:
                continue
            
            seen.add(lookup)
            
            if models:
                model_class, obj_pk = lookup.split(':')
                if model_class not in valid_models:
                    continue
            
            data.append(self.client.get('objdata:%s' % lookup))
        
        return data
    
    def _suggest(self, text, limit):
        """
        At the expense of key memory, depth-first search all results
        """
        w = []
        
        for char in self.client.zrange(text, 0, -1):
            if char == self.terminator:
                w.append(text)
            else:
                w.extend(self._suggest(text + char, limit))
            
            if limit and len(w) >= limit:
                return w[:limit]
        
        return w
