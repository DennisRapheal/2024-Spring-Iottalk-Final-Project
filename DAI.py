
import time, random, requests
import DAN
import crawl

#ServerURL = 'http://yourServerIP:9999'     #with non-secure connection;
ServerURL = 'https://2.iottalk.tw'
#Reg_addr = None 
Reg_addr = "AABB3388" + str( random.randint(100,999 ) )  #None #if None, Reg_addr = MAC address
DAN.profile['dm_name']='SmartDorm'
# DAN.profile['dm_name']='Dummy_Device'
DAN.profile['df_list'] = ['siren_idf', 
                          'light_idf', 
                          'ac_idf',
                          '4_idf',
                          '5_idf',
                          '6_idSf',
                        'distance_odf',
                        '2_odf',
                        '3_odf']
DAN.profile['d_name']= str( random.randint(1,999))+'.LTW'  ##  who are you? �A�O�� 

DAN.device_registration_with_retry(ServerURL, Reg_addr)
#DAN.deregister()  #if you want to deregister this device, uncomment this line
#exit()            #if you want to deregister this device, uncomment this line

def pushIDF(IdfName, data):
    DAN.push(IdfName,data)
    time.sleep(0.2)


             

