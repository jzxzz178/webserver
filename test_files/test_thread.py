import threading
import time


class MyThread(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name

    def run(self):
        for i in range(5):
            print(f"Поток {self.name}: Итерация {i + 1} \n")
            time.sleep(1)  # Задержка на 1 секунду


# Создание двух экземпляров класса MyThread
thread1 = MyThread('FIRST')
thread2 = MyThread('SECOND')

# Запуск обоих потоков
thread1.start()
thread2.start()

# Ожидание завершения обоих потоков
thread1.join()
thread2.join()

print("Главный поток завершен")
