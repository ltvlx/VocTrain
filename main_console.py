import voctrain as vt



a = vt.VocabularyTrainer('words_A2-1_c5.xlsx', 1)
print(a.get_status())


for _ in range(1):
    print('\n', a.get_definition())
    user_word = input("german word is: ")
    print(a.check_answer(user_word))

print(a.get_most_unknown(10))