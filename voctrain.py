import pandas as pd
import codecs
import numpy as np

class VocabularyTrainer:
    __sheets = {}
    __n_total = 0

    __n_cor = 0
    __n_inc = 0

    __q_i = 0           # index of words being questioned
    __a_names = []      # cumulative list of all sheet names
    __a_index = []      # cumulative list of all indexes

    __k_train = 0 # Train mode 0 == 'allwords', 1 == 'badwords'

    def __init__(self, f_inp, key_train):
        """
        Vocabulary trainer class  
        'f_inp' is a path to *.xlsx file with your vocabulary.  
        'key_train' is a key for training mode  
           0 for all words training  
           1 for bad words training
        """
        assert (key_train == 0) or (key_train == 1)
        self.__k_train = key_train

        with pd.ExcelFile(f_inp) as xls:
            for name in xls.sheet_names:
                self.__sheets[name] = pd.read_excel(xls, name)
                self.__n_total += len(self.__sheets[name].index)
                if ('correct' in self.__sheets[name]) and ('incorrect' in self.__sheets[name]):
                    self.__sheets[name]['correct'] = self.__sheets[name]['correct'].fillna(1)
                    self.__sheets[name]['incorrect'] = self.__sheets[name]['incorrect'].fillna(1)
                else:
                    self.__sheets[name]['correct'] = 0
                    self.__sheets[name]['incorrect'] = 0

                self.__sheets[name]['coeff'] = 1.0
                for i in self.__sheets[name].index:
                            _cor = self.__sheets[name].at[i, 'correct']
                            _inc = self.__sheets[name].at[i, 'incorrect']
                            self.__sheets[name].at[i, 'coeff'] = get_coeff(_cor, _inc)

        print("Total number of words in your dictionary is %d"%self.__n_total)

        if self.__k_train == 0:
            self.__init_training_aw()
        elif self.__k_train == 1:
            self.__init_training_bw()


    def save_data(self, f_out):
        """
        Writes 'self.__sheets' back to excel file
        """
        with pd.ExcelWriter(f_out) as writer:
            for name in self.__sheets:
                df = self.__sheets[name].drop(['coeff'], axis=1)
                df.to_excel(writer, sheet_name=name)


    def check_answer(self, user_answer):
        """
        Checks if the 'user_answer' == 'word'
        Modifies the corresponding 'correct', 'incorrect', and 'coeff' values of 'self.__sheets' dataframe
        """
        _i = self.__a_index[self.__q_i]
        _s = self.__a_names[self.__q_i]

        word = self.__sheets[_s].at[_i, 'word']               
        user_answer = user_answer.strip()
        
        if is_correct(word, user_answer):
            self.__sheets[_s].at[_i, 'correct'] += 1
            self.__n_cor += 1
            self.__update_coeff()
            return True
        else:
            self.__sheets[_s].at[_i, 'incorrect'] += 1
            self.__n_inc += 1
            self.__update_coeff()
            return False


    def get_definition(self):
        if self.__k_train == 0:
            return self.__get_definition_aw()
        elif self.__k_train == 1:
            return self.__get_definition_bw()


    def set_answer(self, user_answer):
        if self.__k_train == 0:
            return self.__set_answer_aw(user_answer)
        elif self.__k_train == 1:
            return self.__set_answer_bw(user_answer)


    def get_status(self):
        if self.__k_train == 0:
            return "This session stats: %d✔ %d✘ %d❓"%(self.__n_cor, self.__n_inc, self.__n_left)
        elif self.__k_train == 1:
            return "This session stats: %d✔ %d✘"%(self.__n_cor, self.__n_inc)


    def get_most_unknown(self, n):
        if n <= 0:
            print("get_most_unknown() can not print less then 1 word")
            return

        df = pd.DataFrame(columns=['word', 'definition', 'coeff'])
        for name in self.__sheets:
            df1 = self.__sheets[name][['word', 'definition', 'coeff']]
            df = df.append(df1, ignore_index=True)
        
        if n > len(df.index):
            print()
            n = len(df.index)
        
        df = df.sort_values(by=['coeff'], ascending=False)[:n].reset_index(drop=True)
        result = 'The worst known words:\n\n'
        for i in range(n):
            result += "%d. %s\n%s\n\n"%(i+1, df.at[i, 'word'], df.at[i, 'definition'])

        return result[:-2]


    def get_least_trained(self, n):
        if n <= 0:
            print("get_least_trained() can not print less then 1 word")
            return

        df = pd.DataFrame(columns=['word', 'definition', 'total'])
        for name in self.__sheets:
            df1 = self.__sheets[name][['word', 'definition', 'correct', 'incorrect']]
            df1 = df1.assign(total = lambda x: x.correct + x.incorrect)
            df1 = df1.drop(['correct', 'incorrect'], axis=1)
            df = df.append(df1, ignore_index=True)

        if n > len(df.index):
            print()
            n = len(df.index)
        
        df = df.sort_values(by=['total'])[:n].reset_index(drop=True)
        result = 'The least trained known words:\n\n'
        for i in range(n):
            result += "%s (%d)\n%s\n\n"%(df.at[i, 'word'], df.at[i, 'total'], df.at[i, 'definition'])

        return result[:-2]


    def __get_word_info(self):
        _i = self.__a_index[self.__q_i]
        _s = self.__a_names[self.__q_i]

        w_row = self.__sheets[_s].loc[_i].dropna()
        cols = [x for x in list(w_row.keys()) if x not in ['correct', 'incorrect', 'definition', 'coeff', 'word']]

        res = w_row['word']

        if 'forms' in cols:
            res += ', ' + w_row['forms'] + '\n'
            cols.remove('forms')

        for field in cols:
            res += field + str(w_row[field]) + '\n'
        return res


    def __update_coeff(self):
        _i = self.__a_index[self.__q_i]
        _s = self.__a_names[self.__q_i]
        _cor = self.__sheets[_s].at[_i, 'correct']
        _inc = self.__sheets[_s].at[_i, 'incorrect']
        self.__sheets[_s].at[_i, 'coeff'] = get_coeff(_cor, _inc)


    #########################################################################################
    # Mode 0. Revision of all the words

    def __init_training_aw(self):
        self.__n_left = self.__n_total

        # making unified list of coeffs
        for _s in self.__sheets:
            for _i in self.__sheets[_s].index:
                self.__a_names.append(_s)
                self.__a_index.append(_i)
    

    def __get_definition_aw(self):
        if self.__n_left == 0:
            return "You have checked all the words! Save and exit"
        self.__q_i = np.random.randint(self.__n_left)

        _i = self.__a_index[self.__q_i]
        _s = self.__a_names[self.__q_i]

        return self.__sheets[_s].at[_i, 'definition']


    def __set_answer_aw(self, user_answer):
        if self.__n_left == 0:
            return "You have checked all the words! Save and exit"

        if self.check_answer(user_answer):
            res = "Correct!\n" + self.__get_word_info()
            self.__a_names.pop(self.__q_i)
            self.__a_index.pop(self.__q_i)
            self.__n_left -= 1
        else:
            res = "Incorrect!\n" + self.__get_word_info()
        return res
            

    #########################################################################################
    # Mode 1. Working with badly known words

    def __init_training_bw(self):
        self.__a_probs = []       # cumulative list of all probabilities based on coeff

        # making unified list of coeffs
        for _s in self.__sheets:
            for _i in self.__sheets[_s].index:
                self.__a_names.append(_s)
                self.__a_index.append(_i)
                _cor = self.__sheets[_s].at[_i, 'correct']
                _inc = self.__sheets[_s].at[_i, 'incorrect']
                self.__sheets[_s].at[_i, 'coeff'] = get_coeff(_cor, _inc)
                self.__a_probs.append(get_prob(get_coeff(_cor, _inc)))
        s = sum(self.__a_probs)
        self.__a_probs = [x/s for x in self.__a_probs]        


    def __recalc_probs(self):
        for i in range(self.__n_total):
            _i = self.__a_index[i]
            _s = self.__a_names[i]
            self.__a_probs[i] = get_prob(self.__sheets[_s].at[_i, 'coeff'])

        s = sum(self.__a_probs)
        self.__a_probs = [x/s for x in self.__a_probs]    


    def __get_definition_bw(self):
        self.__q_i = np.random.choice(range(self.__n_total), p=self.__a_probs)
        _i = self.__a_index[self.__q_i]
        _s = self.__a_names[self.__q_i]

        return self.__sheets[_s].at[_i, 'definition']


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
    



