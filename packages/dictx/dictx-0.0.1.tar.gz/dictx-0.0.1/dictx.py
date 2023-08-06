#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""dict wrapper for chained operations"""
#
# XXX logical combination of keys and vals is broken
# 

def identity(x):
    return x

def none_to_empty_str(x):
    return '' if x is None else x

def empty_str_to_none(x):
    return None if x=='' else x

def applym(funcs, v):
    for f in funcs:
        v=f(v)
    return v

def selector(keys):
    """dwimly convert key set specifier to pred: key --> bool"""

    if not keys:
        pred=lambda k: True
    elif isinstance(keys, basestring):
        key_set=set(keys.split())
        pred=lambda k: k in key_set
    elif isinstance(keys, (list,tuple,set)):
        pred=lambda k: k in keys
    elif callable(keys):
        pred=keys
    else:
        raise RuntimeError('keys must be a space-separated string, iterable or a callable')

    return pred

def mapper(amap):
    """dwimly convert map arg to a map function"""

    if callable(amap):
        return amap

    if isinstance(amap, dict):
        return lambda x: amap.get(x, x)

    raise RuntimeError('amap must be a callable or a dict ' + str(amap))

class DX(object):
    """dictionary wrapper"""

    def mapv(self, vmap, keys=None, vals=None):
        """map values on items selected by keys and vals"""

        wantk=selector(keys)
        wantv=selector(vals)
        vmapf=mapper(vmap)

        return DX(dict([ (k, vmapf(v) if (wantk(k) or wantv(v)) else v ) for k,v in self.d.items() ]))

    def mapk(self, kmap, keys=None, vals=None):
        """map keys on items selected by keys and vals"""

        wantk=selector(keys)
        wantv=selector(vals)    # xx roll these two into one..
        kmapf=mapper(kmap)

        return DX(dict([ (kmapf(k) if (wantk(k) or wantv(v)) else k, v) for k,v in self.d.items() ]))

    def keep(self, keys=None, vals=None):
        wantk=selector(keys)
        wantv=selector(vals)
        return DX(dict([ (k,v) for k,v in self.d.items() if (wantk(k) or wantv(v)) ]))

    def slice(self, keys):
        """slice dict by keys"""

        return self.keep(keys)

    def lose(self, keys=None, vals=None):
        """take complement"""
        
        wantk=selector(keys)
        wantv=selector(vals)
        return DX(dict([ (k,v) for k,v in self.d.items() if not (wantk(k) and wantv(v)) ]))

    def mapvd(self, **key_to_vmap):
        """dispatched value map. apply different value maps by key"""
        return DX(dict([ (k, key_to_vmap.get(k,identity)(v)) for k,v in self.d.items() ]))

    def rename(self, **alias):
        """rename keys"""
        return self.mapk(alias)

    ####
    def map_v(self, *mappers, **key_to_mapper):
        """transform vals
           a mapper transforma a value to another.
           mappers apply to all vals.
           key_to_mapper applies selectively to matching keys.
        """
        return DX(dict([ (k, key_to_mapper.get(k,identity)(applym(mappers, v))) 
                         for k,v in self.d.items() ]))

    def lose_k(self, keys):
        """ filter out items by keys
        keys: speace-separated string of keys, iterable of keys or pred: k --> bool
        note: to match a single string key with space in it, put it in a list: ['foo bar']
        """
        pred=selector(keys)
        return DX(dict([ (k, v) for k,v in self.d.items() if not pred(k) ]))

    def keep_k(self, keys):
        """slice dict by keys"""
        pred=selector(keys)
        return DX(dict([ (k, v) for k,v in self.d.items() if pred(k) ]))

    def map_items(self, mapper):
        return DX(dict([ mapper(k, v) for k,v in self.d.items() ]))

    ################

    def __init__(self, d):
        self.d=d

    def __repr__(self):
        return repr(self.d)

    def slice_keys(self, keys, reverse=False, **kw):
        """ dict --> dict which is a project to the given subset of keys"""

        if kw.has_key('default'):
            get=lambda d,k: d.get(k, kw['default'])
        else:
            get=lambda d,k: d[k]

        keys=keys.split() if isinstance(keys, basestring) else keys
        if reverse:
            keys=set(self.d.keys()).difference(keys)

        sliced=DX(dict([ (k,get(self.d,k)) for k in keys ]))
        return sliced

    def map_vals(self, val_mapper=lambda v: v):
        """ transform the values 
        """
        return DX(dict([ (k, val_mapper(v)) for k,v in self.d.items()  ]))

    def map_vals2(self, **key_to_val_mapper):
        """ transform the values """
        return DX(dict([ (k, key_to_val_mapper.get(k,identity)(v)) for k,v in self.d.items()  ]))

    def remove_keys(self, pred):
        return self.filter_keys(pred, reverse=True)

    def filter_keys(self, pred, reverse=False):
        """ filter items by key predicate: str --> bool  """
        if isinstance(pred, basestring):
            keys=pred.split()
            pred=lambda k: k in keys
        assert callable(pred)
        if reverse:
            pred2=lambda k: not pred(k)
        else:
            pred2=pred
        return DX(dict([ (k, v) for k,v in self.d.items() if pred2(k) ]))

    def mod_vals(self, **key_val_modifier):
        """ key --> val --> new-val """
        return DX(dict([ (k, key_val_modifier.get(k, identity)(v)) for k,v in self.d.items() ]))

    def mod_keys(self, **key_map):
        """ key --> key --> new-key """
        return DX(dict([ (key_map.get(k,k),v) for k,v in self.d.items() ]))

    def defaults(self, **defaultd):
        """ soft update """
        return DX(dict( defaultd.items() + [ (k,v) for k,v in self.d.items() if v is not None ] ))

    def extend(self, **items):
        return self.defaults(**items)

    def hoge(self, *item_makers):
        """update/create item from existing items"""
        return DX(dict( self.d.items() + [item_maker(self.d) for item_maker in item_makers] ))

    def update(self, *item_makers, **delta):
        """update by delta"""
        return DX(dict( self.d.items() 
                        + [item_maker(self.d) for item_maker in item_makers]
                        + delta.items()))
    # prever update(foo=lambda d: ... )
    # to     update(lambda d: ('foo', ...))

    def dump(self):
        print self.d
        return self

    # xx deprecate. keep().values() will suffice.
    def select(self, keys):
        """ map get over keys: keys --> vals """
        keys=keys.split() if isinstance(keys, basestring) else keys
        try:
            return [ self.d[k] for k in keys ]
        except KeyError, e:
            e.args+=(self.d,)
            raise

def delta(da,db):

    updates,conflicts={},{}

    for k in da.keys():
        a,b=da[k],db.get(k)
        # classify
        if a==b:
            # in sync
            pass
        elif not b:
            # nothing to update
            pass
        elif not a:
            # update
            updates[k]=b
        else:
            # conflict
            conflicts[k]=(a,b)

    return updates, conflicts
