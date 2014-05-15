from threading import *
import time

def f():
	for i in range(10):
		print('asdfasdf')
		time.sleep(.001)

def g():
	time.sleep(.0005)
	for i in range(10):
		print('fdsa')
		time.sleep(.001)
print()
Thread(target=f).start()
Thread(target=g).start()