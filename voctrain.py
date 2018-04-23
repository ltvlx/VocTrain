import pandas as pd
import codecs
import numpy as np

class VocabularyTrainer:
    sheets = {}
    n_words_total = 0

    l_cor = [0]
    l_inc = [0]

    a_i = -1 # index of words being questioned

    k_train = 0 # Train mode
    training_types = ['allwords', 'badwords']


    def __init__(self, f_inp, key_train):
        """
        Vocabulary trainer class  
        'f_inp' is a path to *.xlsx file with your vocabulary.  
        'key_train' is a key for training mode  
           0 for all words training  
           1 for bad words training
        """
        assert (key_train == 0) or (key_train == 1)
        self.k_train = key_train

        with pd.ExcelFile(f_inp) as xls:
            for name in xls.sheet_names:
                self.sheets[name] = pd.read_excel(xls, name)
                self.n_words_total += len(self.sheets[name].index)
                if ('correct' in self.sheets[name]) and ('incorrect' in self.sheets[name]):
                    self.sheets[name]['correct'] = self.sheets[name]['correct'].fillna(1)
                    self.sheets[name]['incorrect'] = self.sheets[name]['incorrect'].fillna(1)
                else:
                    self.sheets[name]['correct'] = 0
                    self.sheets[name]['incorrect'] = 0

                self.sheets[name]['coeff'] = 1.0
                for i in self.sheets[name].index:
                            _cor = self.sheets[name].at[i, 'correct']
                            _inc = self.sheets[name].at[i, 'incorrect']
                            self.sheets[name].at[i, 'coeff'] = get_coeff(_cor, _inc)

        print("Total number of words in your dictionary is %d"%self.n_words_total)

        if self.k_train == 0:
            self.__init_training_aw()
        elif self.k_train == 1:
            self.__init_training_bw()


    def save_data(self, f_out):
        """
        Writes 'self.sheets' back to excel file
        """
        with pd.ExcelWriter(f_out) as writer:
            for name in self.sheets:
                df = self.sheets[name].drop(['coeff'], axis=1)
                df.to_excel(writer, sheet_name=name)


    def check_answer(self, user_answer):
        """
        Checks if the 'user_answer' == 'word'
        Modifies the corresponding 'correct', 'incorrect', and 'coeff' values of 'self.sheets' dataframe
        """
        _i = self.a_index[self.a_i]
        _s = self.a_names[self.a_i]

        word = self.sheets[_s].at[_i, 'word']               
        user_answer = user_answer.strip()
        
        if is_correct(word, user_answer):
            self.sheets[_s].at[_i, 'correct'] += 1
            self.l_cor.append(self.l_cor[-1] + 1)
            self.l_inc.append(self.l_inc[-1])
            self.__update_coeff()
            return True
        else:
            self.l_cor.append(self.l_cor[-1])
            self.l_inc.append(self.l_inc[-1] + 1)
            self.sheets[_s].at[_i, 'incorrect'] += 1
            self.__update_coeff()
            return False


    def get_definition(self):
        if self.k_train == 0:
            return self.__get_definition_aw()
        elif self.k_train == 1:
            return self.__get_definition_bw()


    def set_answer(self, user_answer):
        if self.k_train == 0:
            return self.__set_answer_aw(user_answer)
        elif self.k_train == 1:
            return self.__set_answer_bw(user_answer)


    def get_status(self):
        if self.k_train == 0:
            return "This session stats: %d✔ %d✘ %d❓"%(self.l_cor[-1], self.l_inc[-1], self.n_words_left)
        elif self.k_train == 1:
            return "This session stats: %d✔ %d✘"%(self.l_cor[-1], self.l_inc[-1])
                    

    def get_most_unknown(self, n):
        if n <= 0:
            print("get_most_unknown() can not print less then 1 word")
            return

        df = pd.DataFrame(columns=['word', 'definition', 'coeff'])
        for name in self.sheets:
            df1 = self.sheets[name][['word', 'definition', 'coeff']]
            df = df.append(df1, ignore_index=True)
        
        if n > len(df.index):
            print()
            n = len(df.index)
        
        df = df.sort_values(by=['coeff'], ascending=False)[:n].reset_index(drop=True)
        result = 'The worst known words:\n\n'
        for i in range(n):
            result += "%d. %s\n%s\n\n"%(i+1, df.at[i, 'word'], df.at[i, 'definition'])

        return result[:-2]


    def __get_word_info(self):
        _i = self.a_index[self.a_i]
        _s = self.a_names[self.a_i]

        w_row = self.sheets[_s].loc[_i].dropna()
        cols = [x for x in list(w_row.keys()) if x not in ['correct', 'incorrect', 'definition', 'coeff', 'word']]

        res = w_row['word']

        if 'forms' in cols:
            res += ', ' + w_row['forms'] + '\n'
            cols.remove('forms')

        for field in cols:
            res += field + str(w_row[field]) + '\n'
        return res


    def __update_coeff(self):
        _i = self.a_index[self.a_i]
        _s = self.a_names[self.a_i]
        _cor = self.sheets[_s].at[_i, 'correct']
        _inc = self.sheets[_s].at[_i, 'incorrect']
        self.sheets[_s].at[_i, 'coeff'] = get_coeff(_cor, _inc)


    #########################################################################################
    # Mode 0. Revision of all the words

    def __init_training_aw(self):
        self.a_i = 0          # index of current word
        self.a_names = []     # three lists which form a single table of all sheet names
        self.a_index = []     # indexes of words in those sheets and coefficients of words
        self.n_words_left = self.n_words_total

        # making unified list of coeffs
        for _s in self.sheets:
            for _i in self.sheets[_s].index:
                self.a_names.append(_s)
                self.a_index.append(_i)
    

    def __get_definition_aw(self):
        if self.n_words_left == 0:
            return "You have checked all the words! Save and exit"
        self.a_i = np.random.randint(self.n_words_left)

        _i = self.a_index[self.a_i]
        _s = self.a_names[self.a_i]

        return self.sheets[_s].at[_i, 'definition']      


    def __set_answer_aw(self, user_answer):
        if self.n_words_left == 0:
            return "You have checked all the words! Save and exit"

        if self.check_answer(user_answer):
            res = "Correct!\n" + self.__get_word_info()
            self.a_names.pop(self.a_i)
            self.a_index.pop(self.a_i)
            self.n_words_left -= 1
        else:
            res = "Incorrect!\n" + self.__get_word_info()
        return res
            

    #########################################################################################
    # Mode 1. Working with badly known words

    def __init_training_bw(self):
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


    def __recalc_probs(self):
        for i in range(self.n_words_total):
            _i = self.a_index[i]
            _s = self.a_names[i]
            self.a_probs[i] = get_prob(self.sheets[_s].at[_i, 'coeff'])

        s = sum(self.a_probs)
        self.a_probs = [x/s for x in self.a_probs]    


    def __get_definition_bw(self):
        self.a_i = np.random.choice(range(self.n_words_total), p=self.a_probs)
        _i = self.a_index[self.a_i]
        _s = self.a_names[self.a_i]

        return self.sheets[_s].at[_i, 'definition']        


    def __set_answer_bw(self, user_answer):
        if self.check_answer(user_answer):
            res = "Correct!\n" + self.__get_word_info()
        else:
            res = "Incorrect!\n" + self.__get_word_info()
        self.__recalc_probs()
        return res





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
    if (_corr + _incorr) <= 1:
        # word was asked one time or less
        return 5.0
    else:
        return _incorr - _corr * 0.6

def get_prob(_coeff):
    # Function that defines 'prob = f(coeff)'
    return pow(2.71828182846, _coeff)
    



