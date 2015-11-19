import types

from ._registry import register_output
from .base_output import OutputInterface

class GreedyDict(dict):
    def __setitem__(self, key, value):
        print('memorysetitem')
        print(key)
        print(type(value))
        #print(value)
        if isinstance(value, types.GeneratorType):
            value = [val for val in value]
            #for val in value:
            #    if type(val) == type(('a',3)):
            #        print('mem '+str(key)+' | '+str(type(val[1]))+' | '+' | '+str(val))
        super(GreedyDict, self).__setitem__(key, value)

@register_output
class InMemoryOutput(OutputInterface):
    def __init__(self, iterable=None, hash_field=None,
                 tokenized_corpora=None,
                 vectorized_corpora=None, modeled_corpora=None):
        super(InMemoryOutput, self).__init__()

        self.corpus = GreedyDict()

        if iterable:
            self.import_from_iterable(iterable, hash_field)

        self.tokenized_corpora = tokenized_corpora if tokenized_corpora else GreedyDict()
        self.vectorized_corpora = vectorized_corpora if vectorized_corpora else GreedyDict()
        self.modeled_corpora = modeled_corpora if modeled_corpora else GreedyDict()

    def import_from_iterable(self, iterable, field_to_hash):
        """
        iterable: generally a list of dicts, but possibly a list of strings
            This is your data.  Your dictionary structure defines the schema
            of the elasticsearch index.
        """
        if field_to_hash:
            self.hash_field=field_to_hash
            for item in iterable:
                if isinstance(item, basestring):
                    item = {field_to_hash: item}
                id = hash(item[field_to_hash])
                self.corpus[id] = {"_source": item}
        else:
            raise ValueError("A field_to_hash is required for import_from_iterable")

    # TODO: generalize for datetimes
    # TODO: validate input data to ensure that it has valid year data
    def get_date_filtered_data(self, field_to_get, start, end, filter_field="year"):
        return self.get_filtered_data(field_to_get,
                                      "{}<=int({}['_source']['{}'])<={}".format(start, "{}",
                                                                                 filter_field, end))

    def get_filtered_data(self, field_to_get, filter=""):
        if not filter:
            for doc_id, doc in self.corpus.items():
                yield doc_id, doc["_source"][field_to_get]
        else:
            for doc_id, doc in self.corpus.items():
                if eval(filter.format(doc)):
                    yield doc_id, doc["_source"][field_to_get]

    def save(self, filename):
        saved_data = {"iterable": self.corpus,
                      "hash_field": self.hash_field,
                      "modeled_corpora": self.modeled_corpora,
                      "vectorized_corpora": self.vectorized_corpora,
                      "tokenized_corpora": self.tokenized_corpora}
        return super(InMemoryOutput, self).save(filename, saved_data)
