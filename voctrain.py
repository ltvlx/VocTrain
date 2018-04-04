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




    def init_badwords_training(self):
        self.a_i = 0        # index of current word
        self.a_names = []     # three lists which form a single table of all sheet names
        self.a_index = []     # indexes of words in those sheets and coefficients of words
        self.a_coeff = []     # This big structure is used to draw words from sheets with probabilities proportional to their coefficients

        # making unified list of coeffs
        for key in self.sheets:
            for i in self.sheets[key].index:
                self.a_names.append(key)
                self.a_index.append(i)
                self.a_coeff.append((self.sheets[key].at[i, 'coeff'])**2)
        # normalization
        s = sum(self.a_coeff)
        self.a_coeff = [x/s for x in self.a_coeff]


    def save_data(self, f_out):
        # Updating coefficients after training words
        for key in self.sheets:
            for i in self.sheets[key].index:
                self.sheets[key].at[i, 'coeff'] = self.sheets[key].at[i, 'incorrect'] / self.sheets[key].at[i, 'correct']

        # writing data back to file
        with pd.ExcelWriter(f_out) as writer:
            for name in self.sheets:
                self.sheets[name].to_excel(writer, sheet_name=name)


    def get_definition_bw(self):
        self.a_i = np.random.choice(range(self.n_words_total), p=self.a_coeff)
        _i = self.a_index[self.a_i]
        _s = self.a_names[self.a_i]

        return self.sheets[_s].at[_i, 'definition']        

    def check_answer(self, user_answer):
        _i = self.a_index[self.a_i]
        _s = self.a_names[self.a_i]

        word = self.sheets[_s].at[_i, 'word']               

        if user_answer.strip() == '':
            return "You gave no answer,\nthe right was '%s'"%word

        if is_correct(word, user_answer):
            self.sheets[_s].at[_i, 'correct'] += 1
            self.n_correct += 1
            return("Correct!\n'%s'"%word)
        else:
            self.sheets[_s].at[_i, 'incorrect'] += 1
            self.n_incorrect += 1
            return "Incorrect!\nYou said '%s', right words was '%s'"%(user_answer, word)

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






