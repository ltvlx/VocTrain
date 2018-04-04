import voctrain as vt



a = vt.VocabularyTrainer('words_11.xlsx')


for _ in range(3):
    # i = a.get_word_little_known()
    print()
    print(a.get_definition_bw())
    user_word = input("german word is: ")
    print(a.check_answer(user_word))