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
                self.sheets[name]['correct'] = self.sheets[name]['correct'].fillna(1)
                self.sheets[name]['incorrect'] = self.sheets[name]['incorrect'].fillna(1)
                self.sheets[name]['coeff'] = pd.to_numeric(self.sheets[name]['coeff'], downcast='float')
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
        """
        Checks the 'user_answer'  
        Modifies 'self.sheets' dataframes  
        Recalculates probabilities 'self.a_probs' based on the updated correct|incorrect information
        """
        # Weak spot now: recalc_probs is a part of bw_training procedures
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

        _cor = self.sheets[_s].at[_i, 'correct']
        _inc = self.sheets[_s].at[_i, 'incorrect']
        self.sheets[_s].at[_i, 'coeff'] = get_coeff(_cor, _inc)

        self.recalc_probs()
        return result



    #########################################################################################
    # Mode 1. Working with badly known words

    def init_badwords_training(self):
        self.a_i = 0          # index of current word
        self.a_names = []     # three lists which form a single table of all sheet names
        self.a_index = []     # indexes of words in those sheets and coefficients of words
        self.a_probs = []

        # making unified list of coeffs
        for _s in self.sheets:
            for _i in self.sheets[_s].index:
                self.a_names.append(_s)
                self.a_index.append(_i)
                _cor = self.sheets[_s].at[_i, 'correct']
                _inc = self.sheets[_s].at[_i, 'incorrect']
                self.sheets[_s].at[_i, 'coeff'] = get_coeff(_cor, _inc)
                self.a_probs.append(get_prob(get_coeff(_cor, _inc)))
        s = sum(self.a_probs)
        self.a_probs = [x/s for x in self.a_probs]        


    def recalc_probs(self):
        for i in range(self.n_words_total):
            _i = self.a_index[i]
            _s = self.a_names[i]
            self.a_probs[i] = get_prob(self.sheets[_s].at[_i, 'coeff'])

        s = sum(self.a_probs)
        self.a_probs = [x/s for x in self.a_probs]    


    def get_definition_bw(self):
        self.a_i = np.random.choice(range(self.n_words_total), p=self.a_probs)
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

def get_coeff(_corr, _incorr):
    # Function that defines 'coeff = f(correct, incorrect)
    return _incorr - _corr * 0.6

def get_prob(_coeff):
    # Function that defines 'prob = f(coeff)'
    return pow(2.71828182846, _coeff)
    



