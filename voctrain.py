import pandas as pd
import codecs
import numpy as np

class VocabularyTrainer:
    sheets = {}
    sizes = {}
    n_words_total = 0
    n_correct = 0
    n_incorrect = 0

    k_train = -1
    training_types = ['allwords', 'badwords']


    def __init__(self, f_inp, key_train = 1):
        with pd.ExcelFile(f_inp) as xls:
            for name in xls.sheet_names:
                self.sheets[name] = pd.read_excel(xls, name)
                self.sizes[name] = len(self.sheets[name].index)
                self.n_words_total += self.sizes[name]
        print("Total number of words in your dictionary is %d"%self.n_words_total)

        if key_train == 1:
            self.init_badwords_training()


    def save_data(self, f_out):
        # writing data back to file
        with pd.ExcelWriter(f_out) as writer:
            for name in self.sheets:
                self.sheets[name].to_excel(writer, sheet_name=name)


    def check_answer(self, user_answer):
        _i = self.a_index[self.a_i]
        _s = self.a_names[self.a_i]

        word = self.sheets[_s].at[_i, 'word']               

        if user_answer.strip() == '':
            self.sheets[_s].at[_i, 'incorrect'] += 1
            self.n_incorrect += 1            
            result = "You gave no answer,\nthe right was '%s'"%word
        else:
            if is_correct(word, user_answer):
                self.sheets[_s].at[_i, 'correct'] += 1
                self.n_correct += 1
                result = "Correct!\n'%s'"%word
            else:
                self.sheets[_s].at[_i, 'incorrect'] += 1
                self.n_incorrect += 1
                result =  "Incorrect!\nYou said '%s', right words was '%s'"%(user_answer, word)

        self.sheets[_s].at[_i, 'coeff'] = self.sheets[_s].at[_i, 'incorrect'] / self.sheets[_s].at[_i, 'correct']
        self.recalc_probs()
        return result



    #########################################################################################
    # Mode 1. Working with badly known words

    def init_badwords_training(self):
        self.a_i = 0          # index of current word
        self.a_names = []     # three lists which form a single table of all sheet names
        self.a_index = []     # indexes of words in those sheets and coefficients of words
        self.a_coeff = []

        # making unified list of coeffs
        for _s in self.sheets:
            for _i in self.sheets[_s].index:
                self.a_names.append(_s)
                self.a_index.append(_i)
                self.a_coeff.append(self.sheets[_s].at[_i, 'incorrect'] / self.sheets[_s].at[_i, 'correct'])
        s = sum(self.a_coeff)
        self.a_coeff = [x/s for x in self.a_coeff]        
        print(self.a_coeff)

    def recalc_probs(self):
        for i in range(self.n_words_total):
            _i = self.a_index[i]
            _s = self.a_names[i]
            # self.a_coeff[i] = (self.sheets[_s].at[_i, 'coeff'])**2
            self.a_coeff[i] = self.sheets[_s].at[_i, 'coeff']

        # normalization
        s = sum(self.a_coeff)
        self.a_coeff = [x/s for x in self.a_coeff]    
        print(self.a_coeff)


    def get_definition_bw(self):
        self.a_i = np.random.choice(range(self.n_words_total), p=self.a_coeff)
        _i = self.a_index[self.a_i]
        _s = self.a_names[self.a_i]

        return self.sheets[_s].at[_i, 'definition']        




def is_correct(word, uword):
    g_lett = {'ß': 'ss', 'ä': 'ae', 'ü': 'ue', 'ö': 'oe'}

    uword = uword.strip().lower()
    word = word.replace('|', '').lower()
    if word == uword:
        return True
    else:
        if max([word.find(x) for x in g_lett.keys()]) != -1:
            for x in g_lett:
                word = word.replace(x, g_lett[x])
                uword = uword.replace(x, g_lett[x])
            if word == uword:
                return True
            else:
                return False
        else:
            return False






