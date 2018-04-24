import voctrain as vt



a = vt.VocabularyTrainer('words_basic.xlsx', 1)
print(a.get_status())


# for _ in range(3):
#     print('\n', a.get_definition())
#     user_word = input("german word is: ")
#     print(a.set_answer(user_word))

print(a.get_least_trained(10))