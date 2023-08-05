# Copyright (c) 2008-2011 Simplistix Ltd
# See license.txt for license details.

from calendar import timegm
from datetime import datetime, timedelta, date
from new import classobj

@classmethod
def add(cls,*args,**kw):
    if 'tzinfo' in kw or len(args)>7:
        raise TypeError('Cannot add tzinfo to %s' % cls.__name__)
    if args and (isinstance(args[0], cls.__bases__[0]) or
                 (isinstance(args[0], datetime) and issubclass(cls, ttimec))):
        inst = args[0]
        if getattr(inst, 'tzinfo', None):
            raise ValueError(
                'Cannot add %s with tzinfo set' % inst.__class__.__name__
                )
        cls._q.append(inst)
    else:
        cls._q.append(cls(*args,**kw))

@classmethod
def set_(cls,*args,**kw):
    if 'tzinfo' in kw or len(args)>7:
        raise TypeError('Cannot set tzinfo on %s' % cls.__name__)
    if args and (isinstance(args[0], cls.__bases__[0]) or
                 (isinstance(args[0], datetime) and issubclass(cls, ttimec))):
        inst = args[0]
        if getattr(inst, 'tzinfo', None):
            raise ValueError(
                'Cannot set %s with tzinfo set' % inst.__class__.__name__
                )
    if cls._q:
        cls._q=[]
    cls.add(*args,**kw)

def __add__(self,other):
    r = super(self.__class__,self).__add__(other)
    if self._ct:
        r = self._ct(r)
    return r

@classmethod
def instantiate(cls):
    r = cls._q.pop(0)
    if not cls._q:
        cls._gap += cls._gap_d
        n = r+timedelta(**{cls._gap_t:cls._gap})
        if cls._ct:
            n = cls._ct(n)
        cls._q.append(n)
    return r

@classmethod
def now(cls,tz=None):
    r = cls._instantiate()
    if tz is not None:
        if cls._tzta:
            r = r - cls._tzta.utcoffset(r)
        return tz.fromutc(r.replace(tzinfo=tz))
    return r

@classmethod
def utcnow(cls):
    r = cls._instantiate()
    if cls._tzta is not None:
        r = r - cls._tzta.utcoffset(r)
    return r
    
def test_factory(n,type,default,args,kw,tz=None,**to_patch):    
    q = []
    to_patch['_q']=q
    to_patch['_tzta']=tz
    to_patch['add']=add
    to_patch['set']=set_
    to_patch['__add__']=__add__
    class_ = classobj(n,(type,),to_patch)
    if args==(None,):
        pass
    elif args or kw:
        q.append(class_(*args,**kw))
    else:
        q.append(class_(*default))
    return class_
    
def correct_date_method(self):
    return self._date_type(
        self.year,
        self.month,
        self.day
        )

@classmethod
def correct_datetime(cls,dt):
    return cls(
        dt.year,
        dt.month,
        dt.day,
        dt.hour,
        dt.minute,
        dt.second,
        dt.microsecond,
        dt.tzinfo,
        )

def test_datetime(*args,**kw):
    tz = None
    if len(args) > 7:
        tz = args[7]
        args = args[:7]
    else:
        tz = kw.pop('tzinfo', None)
    if 'delta' in kw:
        gap = kw.pop('delta')
        gap_delta = 0
    else:
        gap = 0
        gap_delta = 10
    delta_type = kw.pop('delta_type','seconds')
    date_type = kw.pop('date_type',date)
    return test_factory(
        'tdatetime',datetime,(2001,1,1,0,0,0),args,kw,tz,
        _ct=correct_datetime,
        _instantiate=instantiate,
        now=now,
        utcnow=utcnow,
        _gap = gap,
        _gap_d = gap_delta,
        _gap_t = delta_type,
        date = correct_date_method,
        _date_type = date_type,
        )
    
@classmethod
def correct_date(cls,d):
    return cls(
        d.year,
        d.month,
        d.day,
        )

def test_date(*args,**kw):
    if 'delta' in kw:
        gap = kw.pop('delta')
        gap_delta = 0
    else:
        gap = 0
        gap_delta = 1
    delta_type = kw.pop('delta_type','days')
    return test_factory(
        'tdate',date,(2001,1,1),args,kw,
        _ct=correct_date,
        today=instantiate,
        _gap = gap,
        _gap_d = gap_delta,
        _gap_t = delta_type,
        )

class ttimec(datetime):

    def __new__(cls, *args, **kw):
        if args or kw:
            return super(ttimec, cls).__new__(cls, *args, **kw)
        else:
            return float(timegm(cls.instantiate().utctimetuple()))

def test_time(*args,**kw):
    if 'tzinfo' in kw or len(args)>7:
        raise TypeError("You don't want to use tzinfo with test_time")
    if 'delta' in kw:
        gap = kw.pop('delta')
        gap_delta = 0
    else:
        gap = 0
        gap_delta = 1
    delta_type = kw.pop('delta_type','seconds')
    return test_factory(
        'ttime',ttimec,(2001,1,1,0,0,0),args,kw,
        _ct=None,
        instantiate=instantiate,
        _gap = gap,
        _gap_d = gap_delta,
        _gap_t = delta_type,
        )

