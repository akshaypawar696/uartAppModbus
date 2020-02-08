import modbus_tk.defines as cst
from modbus_tk import modbus_rtu
from modbus_tk import modbus_tcp
import sys,time,serial,socket,sqlite3,datetime,threading,schedule,configparser 

try:
	host = socket.gethostbyname("www.google.com")
	s = socket.create_connection((host, 80), 2)
	s.close()
	print('YOU ARE ONLINE........')
except:
	sys.exit("YOU ARE OFLINE........")

def hold(slaveId, reg, startAdd, length):
	global master
	try:
		r = master.execute(slaveId, reg, startAdd, length)
		data = str(list(r))
		print(datetime.datetime.now())
		print(data)
		print('')
	except:
		print(" ********************** TIME_OUT *********************** ")
		
def result():
	global interval
	global delay
	threading.Timer(interval, result).start()
	config = configparser.ConfigParser()
	config.read('queryScript.INI')
	flag = config['DEFAULT']['flag']
	#print('flag',str(flag))
	queryList = []
	
	if(str(flag) == '1'):
		global master
		conn2 = sqlite3.connect('/home/lenovo/Desktop/ap/akshayp/db_configurations.db')
		cursor = conn2.execute("select mode_name, active_flag from tbl_commode_set")
		conn2.commit()
		for row in cursor:
			if(row[0] == 'RTU'):
				RTU = row[1]
			elif(row[0] == 'TCP'):
				TCP = row[1]
		if(TCP == 1):
			cursor = conn2.execute("SELECT ip_address, port_no from tbl_tcp_settings")
			conn2.commit()
			for row in cursor:
				pass
				#print(row)		
			master = modbus_tcp.TcpMaster(host = row[0], port = row[1])
		elif(RTU == 1):
			cursor = conn2.execute("SELECT baudrate, parity, stop_bit,data_bit,date_of_entry from tbl_rtu")
			conn2.commit()
			for row in cursor:
				pass
			master = modbus_rtu.RtuMaster(serial.Serial(port='/dev/ttyUSB0',bytesize=int(row[3]),parity=row[1],baudrate=int(row[0])))
		master.set_timeout(5)
		master.set_verbose(True)
		cursor = conn2.execute("SELECT slave_id, fun_code, start_addr, length from tbl_query_set")
		conn2.commit()
		for row in cursor:
			queryList.append(row)
	conn2.close()
	for row in queryList:
		hold(row[0], row[1], row[2], row[3])
		time.sleep(delay)
	print(' ')
	print('- **************************** X **************************** -')
	print(' ')

if __name__ == '__main__':	
	global interval
	global delay
	conn2 = sqlite3.connect('/home/lenovo/Desktop/ap/akshayp/db_configurations.db')
	cursor = conn2.execute("SELECT starttime, interval, delay from query_time")
	conn2.commit()
	for row in cursor:
		starttime = row[0]		
		interval = int(row[1])
		delay = int(row[2])
	conn2.close()
	print(starttime, interval, delay)
	starttime = str(starttime)
	if starttime == '00:00':
		result()
	else:
		schedule.every().day.at(starttime).do(result) 
		while True: 
			schedule.run_pending() 
			time.sleep(1) 
