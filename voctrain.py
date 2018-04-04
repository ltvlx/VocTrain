import pandas as pd
import codecs
import numpy as np

class VocabularyTrainer:
    sheets = {}
    sizes = {}
    n_words_total = 0
    a_i = -1              # current word
    n_correct = 0
    n_incorrect = 0

    a_sh_names = []     # three lists which form a single table of all sheet names
    a_sh_index = []     # indexes of words in those sheets and coefficients of words
    a_sh_coeff = []     # This big structure is used to draw words from sheets with probabilities proportional to their coefficients

    def __init__(self, f_inp):
        with pd.ExcelFile(f_inp) as xls:
            for name in xls.sheet_names:
                self.sheets[name] = pd.read_excel(xls, name)
                self.sizes[name] = len(self.sheets[name].index)
                self.n_words_total += self.sizes[name]
        print("Total number of words in your dictionary is %d"%self.n_words_total)

        # making unified list of coeffs
        for key in self.sheets:
            for i in self.sheets[key].index:
                self.a_sh_names.append(key)
                self.a_sh_index.append(i)
                self.a_sh_coeff.append((self.sheets[key].at[i, 'coeff'])**2)
        # normalization
        s = sum(self.a_sh_coeff)
        self.a_sh_coeff = [x/s for x in self.a_sh_coeff]



    def save_data(self, f_out):
        # Updating coefficients after training words
        for key in self.sheets:
            for i in self.sheets[key].index:
                self.sheets[key].at[i, 'coeff'] = self.sheets[key].at[i, 'incorrect'] / self.sheets[key].at[i, 'correct']

        # writing data back to file
        with pd.ExcelWriter(f_out) as writer:
            for name in self.sheets:
                self.sheets[name].to_excel(writer, sheet_name=name)

    # def get_word_little_known(self):
    #     return np.random.choice(range(self.n_words_total), p=self.a_sh_coeff)

    def get_definition(self):
        self.a_i = np.random.choice(range(self.n_words_total), p=self.a_sh_coeff)
        _i = self.a_sh_index[self.a_i]
        _s = self.a_sh_names[self.a_i]

        return self.sheets[_s].at[_i, 'definition']        

    def check_answer(self, user_answer):

        _i = self.a_sh_index[self.a_i]
        _s = self.a_sh_names[self.a_i]

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





# def get_words_random(sheets, sizes, n=5):
#     assert n>0
#     categories = list(sizes)
#     w_sum = sum(sizes.values())
#     probs = [sizes[x] / w_sum for x in sizes]

#     for _ in range(n):
#         s_name = np.random.choice(categories, p=probs)
#         i = np.random.randint(sizes[s_name])
#         definition = sheets[s_name].at[i, 'definition']
#         word = sheets[s_name].at[i, 'word']
#         print()
#         print(definition)
#         user_word = input("german word is: ")
#         print()
#         if is_correct(word, user_word):
#             print("Correct!")
#             sheets[s_name].at[i, 'correct'] += 1
#         else:
#             print("Incorrect! You said '%s', right words was '%s'"%(user_word, word))
#             sheets[s_name].at[i, 'incorrect'] += 1




# def get_words_unknown(sheets, n=5):
#     _snames = []
#     _sindex = []
#     _scoeff = []
#     for key in sheets:
#         for i in sheets[key].index:
#             _snames.append(key)
#             _sindex.append(i)
#             _scoeff.append((sheets[key].at[i, 'coeff'])**2)

#     s = sum(_scoeff)
#     _scoeff = [x/s for x in _scoeff]

#     for _ in range(n):
#         i = np.random.choice(range(len(_scoeff)), p=_scoeff)
#         sheets = check_word(sheets, _snames[i], _sindex[i])
    
#     for key in sheets:
#         for i in sheets[key].index:
#             sheets[key].at[i, 'coeff'] = sheets[key].at[i, 'incorrect'] / sheets[key].at[i, 'correct']
#     return sheets


# def check_word(sheets, s_name, i):
    # definition = sheets[s_name].at[i, 'definition']
    # word = sheets[s_name].at[i, 'word']
    # print()
    # print(definition)
    # user_word = input("german word is: ")
    # print()
    # if is_correct(word, user_word):
    #     print("Correct!")
    #     sheets[s_name].at[i, 'correct'] += 1
    # else:
    #     print("Incorrect! You said '%s', right words was '%s'"%(user_word, word))
    #     sheets[s_name].at[i, 'incorrect'] += 1
    # return sheets




####################################################################################

# a = VocabularyTrainer('words.xlsx')

# for _ in range(3):
#     # i = a.get_word_little_known()
#     print(a.get_definition())
#     user_word = input("german word is: ")
#     print(a.check_answer(user_word))
