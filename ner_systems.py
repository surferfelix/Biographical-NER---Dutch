"""This file will contain several NER systems that we can test on biographical data,
we only use PER and LOC labels because all models classify these, which allows us to make proper
comparisons"""
import stanza
from visualize_stuff import Read  # We import the read module here so we don't need to rebuild it.
from flair.data import Sentence
from flair.models import SequenceTagger
from sklearn.metrics import classification_report
# Because sentencepiece in flair does not support python=3.10 yet, we had to change to python version 3.9

class Run_Models():
    '''Class for running the Stanza, Flair and BERTje models'''
    def __init__(self, bio_obj):
        self.bio_obj = bio_obj
        self.tokens = []
        self.preds = []
        self.gold = [word['label'] for dct in self.bio_obj for word in dct['text_entities'] if not word['text'].startswith("<")]

    def run_flair(self):
        tagger = SequenceTagger.load('flair/ner-dutch-large')
        for dct in self.bio_obj:
            for s in dct["text_sents"]:
                # sentence = ' '.join(s) 
                flair_piece = Sentence(s, use_tokenizer=False)
                tagger.predict(flair_piece)
                tagged_lst = flair_piece.to_tagged_string().split()
                
                for index, token in enumerate(tagged_lst):
                    if not index == len(tagged_lst)-1:
                        check = ["<B-", "<E-", "<I-", "<S-"]
                        if any(tagged_lst[index+1].startswith(i) for i in check):
                            label = tagged_lst[index+1] #[3:6]
                            self.tokens.append(token) # The label always occurs after the token
                            self.preds.append(label)
                            continue
                        elif any((token).startswith(i) for i in check):
                            continue
                        else:
                            label = "O"
                            self.tokens.append(token)
                            self.preds.append(label)
                    if index == len(tagged_lst)-1:
                        if not token.startswith('<'):
                            self.tokens.append(token)
                            self.preds.append('O') 
        og_tokens = [word['text'] for dct in self.bio_obj for word in dct['text_entities'] if not word['text'].startswith("<")] # TODO See if < really is a good way to go about this
        return self.tokens, self.preds, self.gold

    def run_stanza(self):
        ''':return: token, pred, gold'''
        # TODO Implement global variables here as well
        nlp = stanza.Pipeline(lang = "nl", processors= 'tokenize, ner', tokenize_pretokenized=True)
        gold = [word['label'] for dct in self.bio_obj for word in dct['text_entities']]
        tokens = []
        labels = []
        for dct in self.bio_obj:
            doc= nlp(dct['text_sents'])
        for sent in doc.sentences:
            for token in sent.tokens:
                tokens.append(token.text)
                labels.append(token.ner)
        return tokens, labels, gold

    def to_file(self, path = '', name = ''):
        print(set(self.preds))
        print(set(self.gold))


def Evaluate_Model(tok, pred, gold):
    # We first grab only LOC and PER labels, and then clean them out
    clean_pred = []
    clean_gold = []
    # Cleaning the predictions {'<I-ORG>', '<E-PER>', '<S-MISC>', 'O', '<S-ORG>', '<B-PER>', '<I-MISC>', '<I-LOC>', '<S-LOC>', '<S-PER>', '<E-MISC>', '<B-MISC>', '<E-LOC>', '<B-ORG>', '<I-PER>', '<B-LOC>', '<E-ORG>'}
    for label in pred:
        if label.endswith('LOC>'):
            clean_pred.append('LOC')
        elif label.endswith('PER>'):
            clean_pred.append('PER')
        elif label == 'O':
            clean_pred.append(label)
        else:
            clean_pred.append('O')
    # Cleaning the GOLD {'B-TIME', 'B-PER', 'O', 'I-LOC', 'B-LOC', 'I-TIME', 'I-PER'}
    for label in gold:
        if label.endswith('LOC') or label.endswith('PER'):
            # print('Adding slice', label[2:5])
            clean_gold.append(label[2:5])
        else:
            clean_gold.append('O')
    # assert len(clean_gold) == len(clean_pred), 'Gold size is different than pred size'
    print(f'Starting length before cleaning, pred: {len(pred)}, gold: {len(gold)}')
    print(f"Cleaned sizes, pred {len(clean_pred)}, gold: {len(clean_gold)}")
    report = classification_report(y_true = clean_gold, y_pred = clean_pred)
    print(report)
        

def main(path):
    '''Performs experiment'''
    r = Read(path)
    bio_obj = r.from_tsv()
    # [word['label'] for dct in self.bio_obj for word in dct['text_entities']]
    a = Run_Models(bio_obj)
    tok, pred, gold = a.run_flair()
    Evaluate_Model(tok, pred, gold)
    
if __name__ == '__main__':
    train = ''
    dev = '../data/train/AITrainingset1.0/Data/test_NHA.txt'
    test = ''
    validate = ''
    main(dev)