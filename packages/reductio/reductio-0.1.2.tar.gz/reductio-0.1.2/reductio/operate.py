from reductio import config
from reductio import network
from reductio import process
import itertools
import sys
import os
import shutil
from importlib import import_module

def _exists(filename):
    "Test whether a file exists."
    return os.access(filename, os.F_OK)

class ShardFileStorage(object):
    """
    Reads and writes data in sharded files that can be distributed.

    This takes output from a map or reduce function, and writes it
    into outgoing files that will be sharded by key and distributed to
    the different workers.
    
    If the output files already exist, it will append to them, so that merging
    data sets is easy.

    This can be written to as a file-like object. Data written to it in this
    way will go to the unformatted text file "result.txt" in its directory,
    which can be used as final output or passed to a reducer on the same
    machine.
    
    All text is read and written as UTF-8.
    """
    def __init__(self, input_name, output_name,
                 homedir=config.HOMEDIR,
                 partitions=config.PARTITIONS):
        self.partitions = partitions
        self.homedir = homedir
        self.input_dir = homedir + os.path.sep + input_name
        self.output_name = output_name
        self.output_dir = homedir + os.path.sep + output_name
        for dir in (self.input_dir, self.output_dir):
            if not _exists(dir):
                os.makedirs(dir)
                print "Created directory %r" % dir

        self.output_files = [None] * self.partitions
        self.result_file = None
    
    def __iter__(self):
        return self.iterlines()

    def input_files(self):
        """
        Get the filenames for files that are inputs to this operation."
        """
        for filename in os.listdir(self.input_dir):
            if filename.endswith('.txt'):
                yield os.path.join(self.input_dir, filename)

    def iterlines(self):
        """
        Returns an iterator over lines in the input files. Skips blank lines.
        """
        for filename in self.input_files():
            infile = open(filename)
            for line in infile:
                if line.strip('\n'):
                    yield line.decode('utf-8')

    def get_partition(self, key):
        return hash(key) % self.partitions

    def write_to_file(self, index, data):
        if self.output_files[index] is None:
            filename = self.output_dir + os.path.sep + "%d.txt" % index
            self.output_files[index] = open(filename, 'a')
        self.output_files[index].write(data)

    def write_pair(self, key, value):
        """
        Write a key-value pair to the appropriate output file, so later it
        can be sent to another worker.
        """
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        partition = self.get_partition(key)
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        self.write_to_file(partition, "%s\t%s\n" % (key, value))

    def write(self, data):
        """
        Write unstructured data to the file `result.txt`.
        """
        if self.result_file is None:
            filename = self.output_dir + os.path.sep + 'result.txt'
            self.result_file = open(filename, 'a')
        if isinstance(data, unicode):
            data = data.encode('utf-8')
        self.result_file.write(data)

    def do_scatter(self):
        """
        Distributes the output files to other servers, where they will
        become input files.
        """
        connections = network.get_connections()
        for (filename, connection) in zip(
            self.input_files(),
            itertools.cycle(connections)
        ):
            source_path = os.path.join(self.input_dir, filename)
            target_path = os.path.join(
                self.output_name,
                config.HOSTNAME+'_'+filename
            )
            network.send_file(connection, source_path, target_path)

    def do_sort(self):
        for file in self.input_files():
            target_file = os.path.join(self.output_dir, os.path.basename(file))
            process.sort(file, target_file)
    
    def do_sort_unique(self):
        for file in self.input_files():
            target_file = os.path.join(self.output_dir, os.path.basename(file))
            process.sort(file, target_file, unique=True)

    def do_initialize(self, input_generator):
        input_generator(self)

    def do_delete(self):
        target_dir = os.path.normpath(self.input_dir)
        if not target_dir.startswith(self.homedir):
            raise ValueError(
                "%r doesn't seem to be a subdirectory of %r. "
                "Refusing to delete it, to be safe."
                % (target_dir, self.homedir)
            )
        shutil.rmtree(target_dir)

    def do_transform(self, transformer):
        r"""
        A "transform" is a kind of map operation that makes no assumptions about
        its data other than the fact that it's Unicode text.
        
        The cases where you need a transform are when

        - your input data isn't in reductio's key-value form, or
        - you want to produce output that isn't in reductio's key-value form.

        As such, a transform function gets the raw text of each line, plus a
        file-like object that you can write to (or output key/value pairs to,
        because it's in fact this object).
        
        If you want to use this data in future
        steps of reductio, your output should be lines in the form:

            <key>\t<value>\n
        
        You are not required to produce one line of output per line of input.
        """
        for line in input_stream:
            transformer(line, self)

    def do_map(self, mapper):
        """
        This function makes it convenient to write a pure mapping function, as
        a generator that takes in (key, value) pairs and yields (key, value)
        pairs.
        """
        for line in self:
            key, value = line.strip('\n').split('\t', 1)
            for result_key, result_value in mapper(key, value):
                self.write_pair(result_key, result_value)
    
    def do_reduce(self, reducer):
        """
        A reducer differs from a mapper in that it groups its incoming data by
        key, and gives the reduce function a generator of the associated values.

        Unlike some map-reduce frameworks, this will never decide to reduce in
        multiple stages. It just gives you an iterator and assumes you can
        handle things from there.
        
        This means your reduce function does *not* have to be prepared to
        take its own output as input. Try taking advantage of this by performing
        your next "map" operation right here!
        """
        for key, pairs in itertools.groupby(
            pair_iterator(self),
            _key_selector
        ):
            values = (_value_selector(pair) for pair in pairs)
            for out_key, out_value in reducer(key, values):
                self.write_pair(out_key, out_value)

def pair_iterator(input_stream):
    """
    Extract tab-delimited (key, value) pairs from a file.
    """
    for line in input_stream:
        line = input_stream.next().strip('\n')
        if line:
            key, value = line.split('\t', 1)
            yield key, value

def _key_selector(pair):
    return pair[0]

def _value_selector(pair):
    return pair[1]

def run_scatter(source, target):
    """
    Send output files to other workers, where they will become input files.
    """
    storage = ShardFileStorage(source, target)
    storage.do_scatter()

def run(command, *args):
    name = 'do_'+command
    if command in ('scatter', 'sort', 'sort_unique', 'delete'):
        if len(args) != 2:
            raise ValueError(
                "Wrong number of arguments. "
                "Expected (operation, source, target)."
        )
        [source, target] = args
        storage = ShardFileStorage(source, target)
        operator = getattr(storage, name)
        operator()
    else:
        if len(args) != 3:
            raise ValueError(
                "Wrong number of arguments. "
                "Expected (operation, function, source, target). "
                "Got: %r" % ([command]+list(args))
            )
        function_path, source, target = args
        module_name, function_name = function_path.rsplit('.', 1)
        storage = ShardFileStorage(source, target)
        if hasattr(storage, name):
            module = import_module(module_name)
            func = getattr(module, function_name)
            operator = getattr(storage, name)
            if func is None:
                raise ValueError("Cannot find %r in %r." % (function_name, module))
            operator(func)
        else:
            raise ValueError("There is no command called %r.\n" % command)

if __name__ == '__main__':
    run(*sys.argv[1:])

