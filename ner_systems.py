"""This file will contain several NER systems that we can test on biographical data"""

from visualize_stuff import Read # We import the read module here so we don't need to rebuild it.
# Because sentencepiece in flair does not support python=3.10 yet, we had to change to python version 3.9

class Preprocess_for_Models():
    def __init__(self):
        pass

    def text_to_sentence(): # We will need this information to pass it onto flair
        pass

class Evaluate_Model():
    '''Takes a model, and evaluates performance'''
    def __init__(self):
        pass

def spacy_model():
    pass

def flair_model(s):
    """s: the sentence"""
    from flair.data import Sentence
    from flair.models import SequenceTagger
    sentence = Sentence(s)
    Tagger = SequenceTagger.load('ner')
    tagger.predict(sentence)

    # Flair requires a sentence so we need to preprocess them first

def stanza_model(): # This model has already been added to the original data, so we don't need to load it here :)
    pass

def BERT_model(): # This will be the main purpose of our study, finetuning this model for the domain
    pass

def main(path):
    '''Performs experiment'''
    r = Read(path)
    bio_obj = r.from_directory() # Currently for dev
    


if __name__ == '__main__':
    train = ''
    dev = '../data/development/json'
    test = ''
    validate = ''
    main(dev)