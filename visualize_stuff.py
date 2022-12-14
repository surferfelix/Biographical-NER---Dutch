'''This script can be used to visualize dictionary data'''

import json
import os
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import numpy as np
import spacy
from spacy.tokens import Doc

# Parser
import argparse

class Read:
    # TODO Currently only works on json objects
    '''Can read files from different sources (dir, single_file)'''
    def __init__(self, path: str):
        self.path = path
    
    def from_directory(self) -> dict: # For our development set
        bio_obj = []
        files = os.listdir(self.path)
        for f in files:
            if not f.startswith('.'):
                with open(f"{self.path}/{f}", 'r') as json_file:
                    a = json.load(json_file)
                    bio_obj.append(a)
        return bio_obj

    def from_file(self) -> list: # For the full evaluation set
        bio_obj = []
        with open(self.path, 'r') as json_file:
            for line in json_file:
                bio_obj.append(json.loads(line)) #Appending dict to list
        return bio_obj

    def from_tsv(self) -> list: # For the training data
        # word\tlabel --> [{text_entities: [{text: word, label: label}]}]
        import csv
        import sys
        ret = [{'text_entities': [], 'text_tokens': [], 'text_sents': []}] # We need to add text sents
        with open(self.path, encoding='windows-1252') as file:
            csv.field_size_limit(sys.maxsize)
            infile = csv.reader(file, delimiter='\t', quotechar='|')
            # TODO Issue here is that we want to chain B I I tags together
            s = [] # Container to hold sentence objects
            for row in infile:
                if row: # We skip sentence endings here, so we need to remember to see if we want it back later
                    word = row[0]
                    label = row[1]
                    info = {'text': word, 'label': label}
                    for dct in ret:
                        dct['text_entities'].append(info)
                        dct['text_tokens'].append(word)
                        s.append(word) 
                elif not row and s: # If not row we clear s
                    dct['text_sents'].append(s)
                    s = []
        return ret

class Counter:
    """Will count instances of key in obj and return a new dictionary object"""
    # Example Counter(bio_obj, 'named_entities') -> {PER: 113}
    # TODO: Make this counter object
    
    def __init__(self, obj, key):
        self.obj = obj
        self.key = key
    
    def from_bio_obj(self):
        '''Takes bio_obj and returns a counter dict'''
        # This currently just works for the 'text_entities' key
        counter_obj = dict()
        # assert type(self.obj[self.key] == list), 'We need to iterate through a list of strings :('
        for i, lst in enumerate(self.obj):
            for dct in lst[self.key]:
                if dct['label'] in counter_obj:
                    counter_obj[dct['label']] += 1
                else:
                    counter_obj[dct['label']] = 1
        return counter_obj

class Interpret:
    '''For other interpretations, such as which people have tag PER for example'
    Requires the bio_obj'''
    from operator import itemgetter
    def __init__(self, obj):
        self.obj = obj
    
    def count_word_rank(self) -> dict:
        '''Counts words and removes stopwords
        :return: dict of with count for each word'''
        stopwords = set()
        with open("stopwords/stopwords.txt") as f:
            infile = f.readlines()
            for line in infile:
                stopwords.add(line.rstrip('\n'))
        # print(f"Removing stopwords\n{stopwords}")
        counter_obj = dict()
        for dct in self.obj:
            for token in dct['text_tokens']:
                token = token.lower()
                if not token in stopwords:
                    if token in counter_obj:
                        counter_obj[token] += 1
                    else:
                        counter_obj[token] = 1
        return counter_obj

    def popular_persons(self, n: int):
        "Will print n most popular persons in bio_object"
        counter_obj = dict()
        for dct in self.obj:
            for lst in dct['text_entities']:
                if "PER" in lst['label']:
                    if lst['text'] in counter_obj:
                        counter_obj[lst['text']] += 1
                    else:
                        counter_obj[lst['text']] = 1
        res = dict(sorted(counter_obj.items(), key = self.itemgetter(1), reverse = True)[:n])
        return res
    
    def popular_locations(self, n: int):
        "Will print n most popular persons in bio_object"
        counter_obj = dict()
        for dct in self.obj:
            for lst in dct['text_entities']:
                if "LOC" in lst['label']:
                    if lst['text'] in counter_obj:
                        counter_obj[lst['text']] += 1
                    else:
                        counter_obj[lst['text']] = 1
        res = dict(sorted(counter_obj.items(), key = self.itemgetter(1), reverse = True)[:n])
        return res

    def popular_time(self, n: int):
        "Will print n most popular persons in bio_object"
        counter_obj = dict()
        for dct in self.obj:
            for lst in dct['text_entities']:
                if "TIME" in lst['label']:
                    if lst['text'] in counter_obj:
                        counter_obj[lst['text']] += 1
                    else:
                        counter_obj[lst['text']] = 1
        res = dict(sorted(counter_obj.items(), key = self.itemgetter(1), reverse = True)[:n])
        return res

    def popular_organizations(self, n: int):
        "Will print n most popular persons in bio_object"
        counter_obj = dict()
        for dct in self.obj:
            for lst in dct['text_entities']:
                if "ORG" in lst['label']:
                    if lst['text'] in counter_obj:
                        counter_obj[lst['text']] += 1
                    else:
                        counter_obj[lst['text']] = 1
        res = dict(sorted(counter_obj.items(), key = self.itemgetter(1), reverse = True)[:n])
        return res
    
    def popular_misc(self, n: int):
        "Will print n most popular persons in bio_object"
        counter_obj = dict()
        for dct in self.obj:
            for lst in dct['text_entities']:
                if "MISC" in lst['label']:
                    if lst['text'] in counter_obj:
                        counter_obj[lst['text']] += 1
                    else:
                        counter_obj[lst['text']] = 1
        res = dict(sorted(counter_obj.items(), key = self.itemgetter(1), reverse = True)[:n])
        return res

    def count_words(self):
        count = 0
        for dct in self.obj:
            for word in dct['text_tokens']:
                count+=1
        return count

    def count_bionet_sources(self):
        pass
            
    
    def concatenate_bios(self):
        '''Will interpret the bio-obj and concatenate sequences of BI tags to form 'whole' tag representations
        :return: a new bio object with only whole tagged items, 
        in which case word represents the FULL entity, and label the tag for that entity'''
        obj = self.obj # I want to test if new variable helps with runtime
        storage_obj = {'text_entities': [{}], "text_tokens": []} #{'text_entities': [word: tag, label: label]}
        window = 10 # We assume no entity will have more than 10 tokens
        for dct in obj:
            for i, entity in enumerate(dct['text_entities']):
                tl = [] # We join the objects in here
                labs = []
                if entity['label'].startswith('B'): # We know it is the onset of an entity
                    tl.append(entity['text'])
                    for l in range(window):
                        try:
                            if dct['text_entities'][i+l]['label'].startswith('I'):
                                txt = dct['text_entities'][i+l]['text']
                                lab = entity['label']
                                if txt:
                                    tl.append(txt)
                                    labs.append(lab)
                        except IndexError:
                            continue # We are at the end of the file
                    entity = ' '.join(tl)
                    if labs:
                        l = labs[0][2:]
                        ret = {'word': entity, 'label': l}
                        storage_obj['text_entities'].append(ret)
                        storage_obj['text_tokens'].append(entity)
        return [storage_obj]
            

class Compare:
    '''Will take two bio_obj and compare them''' 
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def overlap(self, lemmatize = True, verbose = True):
        '''A function for calculating the overlapping words in x and y
        calculates score -> overlap/mintotaltok(obj1/2)*100
        :param lemmatize: should we lemmatize before calculating overlap?'''
        # Prepare part #TODO: Think about splitting this bit?
        obj1 = self.overlap_help(self.x)
        obj2 = self.overlap_help(self.y)
        if lemmatize:
            obj1 = self.lemmatize_help(obj1)
            obj2 = self.lemmatize_help(obj2, verbose = False)
        if not lemmatize and verbose:
            print('Lemmatizer OFF')
        intersection = len(list(obj1.intersection(obj2)))
        obj1_size = len(list(obj1))
        obj2_size = len(list(obj2))
        ret = f"The intersection between x of \nlength {obj1_size} and y of \nlength {obj2_size} is \n{intersection}"
        score = intersection / obj1_size*100
        print(f"The score we will give is {score}")
        return score
        
    def overlap_help(self, obj) -> set:
        ret = set()
        for dct in obj:
            for token in dct['text_tokens']:
                ret.add(token)
        return ret
    
    def lemmatize_help(self, obj, verbose = True) -> set:
        if verbose:
            print('Lemmatizer ON')
            print('Warning: Using the lemmatizer might take longer to run')
        ret = set()
        nlp = self.load_spacy()
        doc = Doc(nlp.vocab, list(obj))
        for token in nlp(doc):
            ret.add(token.lemma_)
        return ret

    def load_spacy(self):
        nlp = spacy.load('nl_core_news_lg')
        return nlp

class Visualize:
    '''This class can take a dictionary with {str: int}
        and visualize it to your liking
        :type obj: dict
        :type path: string
        :path: path to write to'''
    def __init__(self, obj: dict, path: str):
        self.path = path
        self.obj = obj
    
    def as_donut(self):
        '''Creates and saves a donut plot'''
        values = []
        sources = []

        # Populating the lists
        for source, value in self.obj.items():
            values.append(value)
            sources.append(source)
        
        # Visualizing the data
        plt.pie(values, labels = sources, frame = False, autopct='%1.1f%%')
        my_circle = plt.Circle( (0,0), 0.7, color='white')
        # p = plt.gcf()
        p.gca().add_artist(my_circle)
        plt.savefig(self.path)
    
    def as_wordcloud(self):
        '''Will take dict to generate a wordcloud
        :return: a wordcloud'''
        wc = WordCloud(background_color="white",width=1000,height=1000, 
                        max_words=200,relative_scaling=0.5,normalize_plurals=False).generate_from_frequencies(self.obj)
        wc.to_file(self.path)

    def as_circular_barplot(self):
        '''Will take dict to create a circular barplot'''
        ax = plt.subplot(111, polar=True)
        plt.axis('off')

        # Draw bars
        bars = ax.bar(
            x=angles, 
            height=heights, 
            width=width, 
            bottom=lowerLimit,
            linewidth=2, 
            edgecolor="white",
            color="#61a4b2",
        )

        # little space between the bar and the label
        labelPadding = 4

        # Add labels
        for bar, angle, height, label in zip(bars,angles, heights, df["Name"]):

            # Labels are rotated. Rotation must be specified in degrees :(
            rotation = np.rad2deg(angle)

            # Flip some labels upside down
            alignment = ""
            if angle >= np.pi/2 and angle < 3*np.pi/2:
                alignment = "right"
                rotation = rotation + 180
            else: 
                alignment = "left"

            # Finally add the labels
            ax.text(
                x=angle, 
                y=lowerLimit + bar.get_height() + labelPadding, 
                s=label, 
                ha=alignment, 
                va='center', 
                rotation=rotation, 
                rotation_mode="anchor")

    def as_barplot(self):
        '''Will make a barplot from the counter object'''
        data = self.obj
        # Sorting the dictionary object by value
        sorted_obj = sorted(self.obj.items(), key = lambda x:x[1]) # List of tuples [(John, 22), (Alex, 23)]
        values = []
        sources = []
        for tup in sorted_obj:
            sources.append(tup[0])
            values.append(tup[1])

        x_pos = np.arange(len(sources))

        # Create bars
        plt.bar(x_pos, values)

        # Create names on the x-axis
        plt.xticks(x_pos, sources, color='orange', rotation = 90)
        plt.yticks(color='orange')
        plt.subplots_adjust(bottom=0.4, top = 0.99)
        plt.savefig(self.path)


def train_comparisons(bio):
    '''Takes bio object of Bionet file and will compare to all items in trainset'''
    loc = '../data/train/AITrainingset1.0/Data'
    for path in os.listdir(loc):
        if path.endswith('.txt') and not path.startswith('.') and not path.startswith('vocab'):
            a = Read(f"{loc}/{path}")
            bio_obj_1 = a.from_tsv()
            
            b = Interpret(bio_obj_1)
            word_count = b.count_words()

            c = Compare(bio, bio_obj_1)
            ret = c.overlap(lemmatize = True)
        
            print(f"In the set {path}")
            print(f'The word count is {word_count}')
            print(ret)

def create_wordclouds_for_all_train_files(dir):
    """Takes a path to a directory with trainfiles and will create wordclouds for all of them"""
    loc = '../data/train/AITrainingset1.0/Data'
    for path in os.listdir(loc):
        if path.endswith('.txt') and not path.startswith('.') and not path.startswith('vocab'):
            a = Read(f"{loc}/{path}")
            bio_obj_1 = a.from_tsv()
            
            b = Interpret(bio_obj_1)
            ranked = b.count_word_rank()

            vis = Visualize(ranked, f"wordclouds/WordCloud_{path.rstrip('.txt')}.png")
            vis.as_wordcloud()


def create_popular_entity_wordclouds_for_all_bios(path, ent = 'PER'):
    loc = path
    if path.endswith("jsonl"):
        a = Read(loc)
        bio_obj_1 = a.from_file()
        b = Interpret(bio_obj_1)
        bio_obj_2 = b.concatenate_bios()
        # print(bio_obj_1)
        # print(bio_obj_2)
        
        c = Interpret(bio_obj_2)
        ranked = c.count_word_rank()

        vis = Visualize(ranked, f"../wordclouds/WordCloud_Entities_{path.rstrip('.jsonl')}.png")
        vis.as_wordcloud()

def create_popular_entity_wordclouds_for_all_train_files(path, ent = 'PER'):
    loc = path
    for path in os.listdir(loc):
        if path.endswith('.txt') and not path.startswith('.') and not path.startswith('vocab'):
            a = Read(f"{loc}/{path}")
            bio_obj_1 = a.from_tsv()
            b = Interpret(bio_obj_1)
            bio_obj_2 = b.concatenate_bios()
            print(bio_obj_2)
            
            c = Interpret(bio_obj_2)
            ranked = c.count_word_rank()

            vis = Visualize(ranked, f"wordclouds/WordCloud_{path.rstrip('.txt')}.png")
            vis.as_wordcloud()

def generate_barplot_from_scores(bio):
    '''Takes a loaded bio obj and compares to items in train set to generate scores
    , will draw a barplot to a file'''
    gendict = dict() # This is the dict we use to draw the barplot from
    loc = '../data/train/AITrainingset1.0/Data'
    for path in os.listdir(loc):
        if path.endswith('.txt') and not path.startswith('.') and not path.startswith('vocab'):
            a = Read(f"{loc}/{path}")
            bio_obj_1 = a.from_tsv()
            
            b = Interpret(bio_obj_1)
            word_count = b.count_words()

            c = Compare(bio, bio_obj_1)
            ret = c.overlap(lemmatize = False)

            if not path in gendict:
                gendict[path] = ret

            print(f"In the set {path}")
            print(f'The word count is {word_count}')
            print(ret)
    writepath = 'wordclouds/barplot_with_overlap_scores.png'
    vis = Visualize(gendict, writepath)
    vis.as_barplot()


if __name__ == '__main__':
    path = '../data/full/AllBios.jsonl'
    create_popular_entity_wordclouds_for_all_bios(path)
    # path = '../data/full/AllBios.jsonl'
    # a= Read(path)
    # bio_obj = a.from_file()
    # b = Interpret(bio_obj)
    # bio_obj_2 = b.concatenate_bios()
    # print(bio_obj)
            
    # c = Interpret(bio_obj_2)
    # ranked = c.count_word_rank()

    # vis = Visualize(ranked, f"wordclouds/WordCloud_AllBios.png")
    # vis.as_wordcloud()