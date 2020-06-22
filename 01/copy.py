import threading
import time
import os.path

start_time = 0
lock = threading.Lock()

def log_write(f_in_name, f_out_name, mode):
	try:
		if mode == 0:
			log_file.write(str(round(time.time() - start_time, 2)))
			log_file.write("\tStart copying %s to %s\n" % (f_in_name, f_out_name))
		elif mode == 1:
			log_file.write(str(round(time.time() - start_time, 2)))
			log_file.write("\t%s is copied completely\n" % f_out_name)
	except ValueError:
		print("you put 'exit' before log write")
		pass


def rw_in_1k(f_in_object, f_out_object, size=10000):
	while True:
		piece = f_in_object.read(size)
		if not piece: break
		f_out_object.write(piece)


def total_process(str_in, str_out):
	f_input = open(str_in, mode='rb')
	f_output = open(str_out, mode='wb')
	log_write(str_in, str_out, 0)
	rw_in_1k(f_input, f_output)
	log_write(str_in, str_out, 1)
	f_input.close()
	f_output.close()



if __name__ == '__main__':
	start_time = time.time()
	log_file = open("log.txt", mode='a')
	while True:
		in_str = input("Intput the file name: ")
		if in_str == "exit":
			log_file.close()
			break
		elif os.path.exists(in_str) == False:
			print("No such file...")
			continue
		out_str = input("Input the new name: ")
		copy_thread = threading.Thread(target=total_process, args=(in_str, out_str))
		copy_thread.start()
