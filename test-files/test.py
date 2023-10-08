import threading

import test_client1
import test_client2
import test_client3

if __name__ == '__main__':
    t1 = threading.Thread(target=test_client1.go)
    t2 = threading.Thread(target=test_client2.go)
    t3 = threading.Thread(target=test_client3.go)

    t1.start()
    t2.start()
    t3.start()
