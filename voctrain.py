import pandas as pd
import codecs
import numpy as np

class VocabularyTrainer:
    sheets = {}
    n_words_total = 0
    n_correct = 0
    n_incorrect = 0

    a_i = -1 # index of words being questioned

    k_train = 0 # Train mode
    training_types = ['allwords', 'badwords']


    def __init__(self, f_inp, key_train = 1):
        assert (key_train == 0) or (key_train == 1)
        self.k_train = key_train

        with pd.ExcelFile(f_inp) as xls:
            for name in xls.sheet_names:
                self.sheets[name] = pd.read_excel(xls, name)
                self.n_words_total += len(self.sheets[name].index)
                self.sheets[name]['correct'] = self.sheets[name]['correct'].fillna(1)
                self.sheets[name]['incorrect'] = self.sheets[name]['incorrect'].fillna(1)
                self.sheets[name]['coeff'] = pd.to_numeric(self.sheets[name]['coeff'], downcast='float')
        print("Total number of words in your dictionary is %d"%self.n_words_total)

        if self.k_train == 0:
            self.init_training_aw()
        elif self.k_train == 1:
            self.init_training_bw()


    def save_data(self, f_out):
        """
        Writes 'self.sheets' back to excel file
        """
        with pd.ExcelWriter(f_out) as writer:
            for name in self.sheets:
                self.sheets[name].to_excel(writer, sheet_name=name)


    def check_answer(self, user_answer):
        """
        Checks if the 'user_answer' == 'word'
        Modifies the corresponding 'correct', 'incorrect', and 'coeff' values of 'self.sheets' dataframe
        """
        _i = self.a_index[self.a_i]
        _s = self.a_names[self.a_i]

        word = self.sheets[_s].at[_i, 'word']               
        user_answer = user_answer.strip()
        
        if user_answer == '':
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

        # Modify coeff 
        _cor = self.sheets[_s].at[_i, 'correct']
        _inc = self.sheets[_s].at[_i, 'incorrect']
        self.sheets[_s].at[_i, 'coeff'] = get_coeff(_cor, _inc)

        return result


    def get_definition(self):
        if self.k_train == 0:
            return self.get_definition_aw()
        elif self.k_train == 1:
            return self.get_definition_bw()


    def set_answer(self, user_answer):
        if self.k_train == 0:
            return self.set_answer_aw(user_answer)
        elif self.k_train == 1:
            return self.set_answer_bw(user_answer)


    def get_status(self):
        if self.k_train == 0:
            return "This session stats: %d✔ %d✘ %d❓"%(self.n_correct, self.n_incorrect, self.n_words_left)
        elif self.k_train == 1:
            return "This session stats: %d✔ %d✘"%(self.n_correct, self.n_incorrect)
                    


    #########################################################################################
    # Mode 0. Revision of all the words

    def init_training_aw(self):
        self.a_i = 0          # index of current word
        self.a_names = []     # three lists which form a single table of all sheet names
        self.a_index = []     # indexes of words in those sheets and coefficients of words
        self.n_words_left = self.n_words_total

        # making unified list of coeffs
        for _s in self.sheets:
            for _i in self.sheets[_s].index:
                self.a_names.append(_s)
                self.a_index.append(_i)
    

    def get_definition_aw(self):
        if self.n_words_left == 0:
            return "You have checked all the words! Save and exit"
        self.a_i = np.random.randint(self.n_words_left)

        _i = self.a_index[self.a_i]
        _s = self.a_names[self.a_i]

        return self.sheets[_s].at[_i, 'definition']      


    def set_answer_aw(self, user_answer):
        if self.n_words_left == 0:
            return "You have checked all the words! Save and exit"
        result = self.check_answer(user_answer)

        # TO FIX LATER.
        # check_answer should return True/False  and probably a word
        # Then, another function should print output
        if result.find("Correct") != -1:
            self.a_names.pop(self.a_i)
            self.a_index.pop(self.a_i)
            self.n_words_left -= 1

        print("Words left: %d"%self.n_words_left)
        return result


    #########################################################################################
    # Mode 1. Working with badly known words

    def init_training_bw(self):
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

    def set_answer_bw(self, user_answer):
        result = self.check_answer(user_answer)
        self.recalc_probs()
        return result







def is_correct(word, uword):
    g_lett = {'ß': 'ss', 'ä': 'ae', 'ü': 'ue', 'ö': 'oe'}

    uword = uword.lower()
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
    



