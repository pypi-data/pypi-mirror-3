"""
Persistent Dictionary Class

Provides persistent dictionary support. Loads the full file into memory, leaves 
it there for full speed dict access, and then writes the full dict back on 
close (with an atomic commit).

Useful when lookup and mutation speed are more important than the time spent on 
the initial load and the final write-back.

Similar to the "F" mode in the gdbm module: "The F flag opens the database in 
fast mode. Writes to the database will not be flushed".

"""
import pickle
import marshal
#import json
import ujson as json
import csv
import os
import shutil
#import gc

#import operator
import ordereddict
import bidict
import numpy

from botnee import debug

import logging

#import botnee_config

LOADERS = (
        marshal.loads, 
        json.loads, 
        pickle.loads, 
        csv.reader
            )

class PersistentDict(ordereddict.OrderedDict):
    ''' Persistent dictionary with an API compatible with shelve and anydbm.
    
    The dict is kept in memory, so the dictionary operations run as fast as
    a regular dictionary.
    
    Write to disk is delayed until close or flush (similar to gdbm's fast mode).
    
    Input file format is automatically discovered.
    Output file format is selectable between pickle, marshal json, and csv.
    All serialization formats are backed by fast C implementations.
    '''
    
    def __init__(self, params, verbose=False, logger=None):
        ordereddict.OrderedDict.__init__(self)
        self.flag = params['flag']          # r=readonly, c=create, or n=new
        self.mode = params['mode']          # None or an octal triple like 0644
        self.format = params['format']      # 'csv', 'json', 'pickle', 'marshal'
        self.filename = params['filename']
        self.persistent = params['persistent']
        if 'ignore_on_load' in params:
            self.ignore_on_load = params['ignore_on_load']
        else:
            self.ignore_on_load = []
        
        if self.persistent and self.flag != 'n' \
                           and os.access(self.filename, os.R_OK):
            mode = 'rb' if self.format in ['pickle', 'marshal'] else 'r'
            fileobj = open(self.filename, mode)
            with fileobj:
                self.load(fileobj, verbose, logger)
        #dict.__init__(self, *args, **kwds)
    
    def flush(self, verbose=True, logger=None):
        'Write dict to disk'
        if not self.persistent:
            return
        with debug.Timer(self.__module__, None, verbose, logger):
            if self.flag == 'r':
                return
            filename = self.filename
            tempname = filename + '.tmp'
            mode = 'wb' if self.format in ['pickle', 'marshal'] else 'w'
            fileobj = open(tempname, mode)
            try:
                self.dump(fileobj)
            except Exception:
                os.remove(tempname)
                raise
            finally:
                fileobj.close()
            shutil.move(tempname, self.filename)    # atomic commit
            if self.mode is not None:
                os.chmod(self.filename, self.mode)
    
    def close(self):
        self.flush()
    
    def __enter__(self):
        return self
    
    def __exit__(self, *exc_info):
        if self.persistent:
            self.close()
    
    def dump(self, fileobj):
        """
        Dumps to disk
        """
        types = {}
        dtypes = {}
        #hashes = {}
        file_dict = {}
        
        caster = unicode
        
        for key, value in self.items():
            if 'pseudo' in key:
                continue
            if key in self.ignore_on_load:
                continue
            
            module = value.__class__.__module__
            if module == '__builtin__':
                types[key] = value.__class__.__name__
            else:
                types[key] = module + '.' + value.__class__.__name__
            
            if type(value) in [numpy.array, numpy.ndarray]:
                try:
                    #file_dict[key] = caster(value.tostring())
                    file_dict[key] = caster(value.tolist())
                except:
                    debug.debug_here()
                dtypes[key] = caster(value.dtype)
                #hashes[key] = hash(tuple(value.tolist()))
            elif isinstance(value, numpy.generic):
                file_dict[key] = caster(value)
                dtypes[key] = caster(value.dtype)
            #elif type(value) is bidict.bidict:
            #    file_dict[key] = dict(value)
            #    file_dict[key + '_inv'] = dict(value.inv)
            elif type(value) in [ordereddict.OrderedDict, bidict.bidict, dict]:
                file_dict[key] = dict(value)
                #hashes[key] = hash(tuple(value.items()))
            elif type(value) in [list, tuple, set, frozenset]:
                file_dict[key] = value
                #hashes[key] = hash(tuple(value))
            else:
                file_dict[key] = value
                #hashes[key] = hash(value)
                dtypes[key] = caster(type(value))
        
        file_dict['types'] = types
        file_dict['dtypes'] = dtypes
        #file_dict['hashes'] = hashes
        
        if self.format == 'csv':
            csv.writer(fileobj).writerows(self.items())
        #elif self.format == 'json':
        #    json.dump(self, fileobj, separators=(',', ':'))
        elif self.format == 'json':
            try:
                json.dump(file_dict, fileobj)
            except:
                debug.debug_here()
            #strobj = json.dumps(self)
            #fileobj.write(strobj)
        elif self.format == 'pickle':
            pickle.dump(dict(self), fileobj, 2)
        elif self.format == 'marshal':
            try:
                marshal.dump(file_dict, fileobj, 2)
            except ValueError as e:
                debug.debug_here()
                raise e
        else:
            raise NotImplementedError('Unknown format: ' + repr(self.format))
    
    def load(self, fileobj, verbose=False, logger=None):
        # try formats from most restrictive to least restrictive
        with debug.Timer(self.__repr__(), None, verbose, logger):
            for loader in LOADERS:
                #debug.debug_here()
                msg = 'Loading %s (%s)' % (self.filename, loader.__module__)
                debug.print_verbose(msg, verbose, logger)
                fileobj.seek(0)
                file_dict = {}
                try:
                    s = fileobj.read();
                    debug.print_verbose("File read, calling loader", verbose, logger)
                    #file_dict = loader(fileobj)
                    #gc.disable()
                    file_dict = loader(s)
                    #gc.enable()
                    debug.print_verbose('File loaded', verbose, logger)
                    for key, value in file_dict['types'].items():
                        skip = False
                        for item in self.ignore_on_load:
                            if key.startswith(item):
                                debug.print_verbose(key + ' ignored', verbose, logger)
                                skip = True
                                break
                        if not skip:
                            self.process_item(file_dict, key, value, verbose, logger)
                    return
                except ValueError:
                    #pass
                    #raise
                    continue
        # Shouldn't get here!
        raise ValueError('File not in a supported format')
    
    def process_item(self, file_dict, key, value, verbose=False, logger=None):
        """
        Processes a single item from the loaded file
        """
        base = self.__class__
        basecall = super(base, self)
        
        if key not in ['types', 'dtypes']:
            msg = '(%s, type=<%s>)' % (key, value)
            with debug.Timer(msg, None, verbose, self.logger):
                if value in ['numpy.ndarray', 'numpy.float64']:
                    #value = 'numpy.array'
                    #debug.debug_here()
                    try:
                        basecall.__setitem__(key, 
                            #numpy.fromstring(file_dict[key], 
                            numpy.array(eval(file_dict[key]),
                                dtype = file_dict['dtypes'][key] ))
                    except Exception as e:
                        #debug.debug_here()
                        msg = "Failed to load %s from disk: %s" % (key, e)
                        debug.print_verbose(msg, verbose, logger,
                                            logging.WARNING)
                        basecall.__setitem__(key, None)
                else:
                    try:
                        #if 'hash_map' in key:
                        #    ordered_list = sorted(file_dict[key].iteritems(), 
                        #            key=operator.itemgetter(1))
                        #    eval('basecall.__setitem__(key, %s(ordered_list))' % value)
                        #else:
                        #debug.debug_here()
                        
                        eval('basecall.__setitem__(key, %s(file_dict[key]))' % value)
                        
                    except Exception as e:
                        #debug.debug_here()
                        msg = "Failed to load %s from disk: %s" % (key, e)
                        debug.print_verbose(msg, verbose, logger,
                                            logging.WARNING)
                        basecall.__setitem__(key, None)
                
                if 0: #botnee_config.DEBUG:
                    with debug.Timer('Checking hashes', None, verbose, logger):
                        try:
                            if value in ['numpy.ndarray']:
                                hv = hash(tuple(self[key].tolist()))
                            elif value in ['ordereddict.OrderedDict', 'bidict.bidict', 'dict']:
                                hv = hash(tuple(self[key].items()))
                            elif value in ['list', 'set', 'tuple', 'frozenset']:
                                hv = hash(tuple(self[key]))
                            else:
                                hv = hash(self[key])
                            assert hv == file_dict['hashes'][key]
                        except KeyError:
                            pass
                        except AttributeError:
                            pass
                        except AssertionError:
                            #print key, value
                            #debug.debug_here()
                            pass

