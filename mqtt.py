import modbus_tk.defines as cst
from os.path import dirname, abspath
from modbus_tk import modbus_rtu, modbus_tcp
import gc, os, sys, glob, sqlite3, datetime, platform, subprocess, time, serial, configparser


while True:
    data  = {}
    queryresultlist = []
    count = 0
    finalresultdict = {}
    conn2 = sqlite3.connect('/home/lenovo/Desktop/ap/akshayp/db_configurations.db')
    cursor = conn2.execute("select mode_name,active_flag from tbl_commode_set")
    conn2.commit()
    for row in cursor:
        if(row[0] == 'RTU'):
            RTU = row[1]
        elif(row[0] == 'TCP'):
            TCP = row[1]
    if(TCP == 1):
        #print('@@@@@@   INSIDE  MQTT TCP   @@@@@@')
        cursor = conn2.execute("SELECT ip_address, port_no from tbl_tcp_settings")
        conn2.commit()
        for row in cursor:
            pass
            #print(row)		
        master = modbus_tcp.TcpMaster(host = row[0], port = row[1])
        master.set_timeout(5)
        master.set_verbose(True)
    elif(RTU == 1):
        #print('@@@@@@   INSIDE MQTT RTU   @@@@@@')
        cursor = conn2.execute("SELECT baudrate, parity, stop_bit,data_bit,date_of_entry from tbl_rtu")
        conn2.commit()
        for row in cursor:
            pass
        master = modbus_rtu.RtuMaster(serial.Serial(port=usbport,bytesize=int(row[3]),parity=row[1],baudrate=int(row[0])))
        master.set_timeout(5)
        master.set_verbose(True)
    cursor = conn2.execute("SELECT slave_id,fun_code,start_addr,length,querygroup from tbl_query_set")
    conn2.commit()
    temp = 1
    try:
        for row in cursor:
            mydict = {}
            ap = {}
            count += 1
            #print('@@@@@@@@@@@@@@@@@@=>',count)
            r = master.execute(row[0], row[1], row[2], row[3])
            if temp != row[4]:
                count = 1
            data = list(r)
            queryresultlist = []
            queryresultlist = data
            templist = []
            for i in range(row[2],(row[2]+row[3])):
                templist.append('g' + str(row[4]) + '_' + 'q' + str(count) + '_' + 'r' + str(i))
            mydict = dict(zip(templist,queryresultlist))
            #print('==>>',mydict)
            finalresultdict.update(mydict)
            temp = row[4]
    except:
        print('Inside MQTT Exception.......')
        flash('Something Went Wrong...')
        pass
    conn2.close()

    import paho.mqtt.client as mqtt
    def on_connect( client, userdata, flags, rc):
        print ("Connected with Code :" +str(rc))
        client.subscribe("Test/#")
    def on_message( client, userdata, msg):
        print ( str(msg.payload) )
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.username_pw_set("chnilruw", "DANzI3YqEtn1")
    client.connect("hairdresser.cloudmqtt.com", 15829, 60)
    client.loop_start()
    print(datetime.datetime.now(),' => ',str(finalresultdict))
    client.publish(str(datetime.datetime.now()),str(finalresultdict))
    client.loop_stop()
    client.disconnect()
    time.sleep(15)