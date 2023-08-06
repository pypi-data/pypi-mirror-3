# -*- coding: utf8 -*-
from taxonome.taxa.base import Name
import csv

class NoopTracker:
    """This tracker doesn't do anything."""
    name_event = name_transform = start_taxon = reset = lambda *args: None

noop_tracker = NoopTracker()

class MultiTracker:
    """Holds a list of trackers, and calls the relevant methods of each of them
    when its methods are called."""
    def __init__(self, *args):
        self._trackers = args
    
    def __getattr__(self, name):
        methods = [getattr(t, name) for t in self._trackers if hasattr(t, name)]
        def dispatch(*args, **kwargs):
            for m in methods:
                m(*args, **kwargs)
        return dispatch

def prepare_tracker(tracker):
    if isinstance(tracker, (list, tuple)):
        return MultiTracker(*tracker)
    return tracker

def coroutine(func):
    """Decorator to prime coroutines"""
    def start(*args,**kwargs):
        cr = func(*args,**kwargs)
        next(cr)
        return cr
    return start

RESET = object()
@coroutine
def csvchainwriter(writer):
    """Coroutine to write lines to a csv file, incrementing a chain number until
    it's sent a reset signal."""
    chain = 0
    while True:
        line = (yield)
        if line is RESET:
            chain = 0
        else:
            writer.writerow((chain,) + tuple(line))
            chain += 1

def _flatten_name(name):
    if isinstance(name, Name):
        return name.plain, str(name.authority)
    return name, None

class CSVTracker(NoopTracker):
    """This writes events to a CSV file."""
    def __init__(self, fileobj, header=True):
        writer = csv.writer(fileobj)
        if header:
            writer.writerow(["sequence", "From name", "From authority", "To name", "To authority", "Event"])
        self.push = csvchainwriter(writer).send
        
    def name_event(self, name, event):
        self.push(_flatten_name(name) + (None, None, event))
    
    def name_transform(self, name, newname, event):
        self.push(_flatten_name(name) + _flatten_name(newname) + (event,))
    
    def reset(self):
        self.push(RESET)

class CSVListMatches(NoopTracker):
    """Writes the original name and final match to a CSV file."""
    fromname = None
    toname = None
    
    def __init__(self, fileobj, header=True):
        self.writer = csv.writer(fileobj)
        if header:
            self.writer.writerow(["Name","Authority","Matched to",None])
        
    def name_event(self, name, event):
        if not self.fromname:
            self.fromname = name
        self.toname = None
    
    def name_transform(self, name, newname, event):
        if not self.fromname:
            self.fromname = name
        self.toname = newname
    
    def reset(self):
        if self.fromname:
            self.writer.writerow(_flatten_name(self.fromname) + _flatten_name(self.toname))
        self.fromname = None
        self.toname = None

class Counter(NoopTracker):
    """Count the number of names seen so far. Callback with the number after
    every n (default 10).
    """
    def __init__(self, callback, every=10):
        self.callback = callback
        self.every = every
        self.n = 0
    
    def start_taxon(self, tax):
        self.n += 1
        if self.n % self.every == 0:
            self.callback(self.n)

class CSVTaxaTracker(NoopTracker):
    """Produces a list of the existing taxa data with the new names."""
    taxon = None
    newname = None
    
    def __init__(self, fileobj, fieldnames, header=True, include_unmatched=False):
        fieldnames = ["Name", "Authority", "Original name", "Original authority"]+fieldnames
        self.writer = csv.DictWriter(fileobj, fieldnames, extrasaction='ignore')
        if header:
            self.writer.writeheader()
        
        self.include_unmatched = include_unmatched
    
    def start_taxon(self, tax):
        self.taxon = tax
    
    def name_transform(self, name, newname, event):
        self.newname = newname
    
    def reset(self):
        if self.taxon and (self.newname or self.include_unmatched):
            d = dict(self.taxon.info)
            d['Original name'], d['Original authority'] = _flatten_name(self.taxon.name)
            d['Name'], d['Authority']= _flatten_name(self.newname)
            self.writer.writerow(d)
        
        self.taxon = None
        self.newname = None
