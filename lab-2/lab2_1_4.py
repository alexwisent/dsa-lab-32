# 4. Сумма и количество чисел в введенной произвольной последовательности
# (ввод заканчивается пустой строкой или некорректным числом)
print("Задание 4: сумма и количество введённых целых чисел")
print("Вводите целые числа. Для завершения введите пустую строку или любой нечисловой текст.")

total_sum = 0
count = 0

while True:
    line = input("→ ").strip()
    if not line:
        break
    try:
        number = int(line)
        total_sum += number
        count += 1
    except ValueError:
        print("Ошибка: введено не целое число. Ввод завершён.")
        break

if count > 0:
    print("\nСумма всех чисел:", total_sum)
    print("Количество чисел:", count)
    print("Среднее арифметическое:", round(total_sum / count, 2))
else:
    print("Вы не ввели ни одного числа.")