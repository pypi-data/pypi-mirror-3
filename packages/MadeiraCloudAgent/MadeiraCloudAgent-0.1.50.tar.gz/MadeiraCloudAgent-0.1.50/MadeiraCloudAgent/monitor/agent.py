#!/usr/bin/env python

import sys, time
import MadeiraCloudAgent.psutil as psutil
import httplib, urllib, urllib2
import re,os

class Madeira():
	
	def decodeUsage(self,string):	
		substring = str(string).split('(')[1]
		substring_type = re.findall("[a-z]+\_[a-z]+|[a-z]+",substring)
		substring_value =  re.findall("\d+\.\d+|\d+",substring)
		return substring_type, substring_value
	
	def getParams(self,param,name,data):	
		data_type,data_value = self.decodeUsage(data)
		for i in range(0,len(data_type)):
			param[name +"_" + data_type[i]] = data_value[i]
		return param
	
	def updateKey(self):
		try:
			response = urllib2.urlopen('http://169.254.169.254/latest/meta-data/instance-id')
			instance_id = response.read()
			profilereader = open("/usr/local/madeiracloud/profile.madeira")
			userid = ''
			for line in profilereader:
				userinfo = line.split('=')
				if userinfo[0].strip()=='userid':
					userid = userinfo[1].strip()				
			data = open('/usr/local/madeiracloud/profile.madeira').read()
			data = re.sub('^access_key.*','access_key='+userid+"-"+instance_id, data) 
			open('/usr/local/madeiracloud/profile.madeira', 'wb').write(data)
		except Exception,msg:
			print msg
		
		
	def run(self):
		setting = {}
		setting['disk_path'] = '/'
		setting['CPU_interval'] = 0.0
		processlist = []
		last_net_bytes_send = 0
		last_net_bytes_recv = 0
		self.updateKey()
		t = time.time()
		last_io_read = 0
		last_io_write = 0
		last_io_read_time = 0
		last_io_write_time = 0
		last_cpu_user = 0
		last_cpu_nice = 0
		last_cpu_system = 0
		last_cpu_idle = 0
		last_cpu_iowait = 0
		last_cpu_irq = 0
		last_cpu_softirq = 0
		last_cpu_steal = 0
		last_cpu_guest = 0
		last_cpu_total = 0
		
		while True:
			try:
				start_time = time.time()
				if start_time - t > 3600:
					self.updateKey()
						
				profilereader = open("/usr/local/madeiracloud/profile.madeira")
				for line in profilereader:
					userinfo = line.split('=')
					if userinfo[0].strip()=='userid':
						userid = userinfo[1].strip() 
					if userinfo[0].strip()=='access_key':
						access_key = userinfo[1].strip()
				
				
				param = {}	
				param['key']= access_key
				param['userid']=userid
				param['CPU'] = "%.4f" % (float(psutil.cpu_percent(interval=float(setting['CPU_interval'])))/100)
				mem = psutil.phymem_usage()
				param = self.getParams(param, "mem", mem)	
				vmem = psutil.virtmem_usage()
				param = self.getParams(param, "vmem", vmem)
				net = psutil.network_io_counters()
				param = self.getParams(param, "net", net)
				#disk = psutil.disk_usage(setting['disk_path'])
				#param = self.getParams(param, "disk", disk)	
				"""
				p = psutil.get_process_list()
				for eachP in processlist:
					rss = 0.0;
					vms = 0.0;
					cpu = 0.0;
					for r in p:
						if eachP in str(r):
							cpu = cpu + r.get_cpu_percent(interval=float(setting[eachP+'-CPU_interval']))
							rss1,vms1 = r.get_memory_info()
							rss = rss + rss1
							vms = vms + vms1
					param[eachP+"-CPU"] = cpu
					param[eachP+"-RSS"] = rss
					param[eachP+"-VMS"] = vms			
				"""
				io_read,io_write,c,d,io_read_time,io_write_time = psutil.disk_io_counters(perdisk=False)
				cpu_user, cpu_nice, cpu_system, cpu_idle, cpu_iowait, cpu_irq, cpu_softirq,cpu_steal,cpu_guest = psutil.cpu_times()
				cpu_total = cpu_user + cpu_nice + cpu_system + cpu_idle + cpu_iowait + cpu_irq + cpu_softirq + cpu_steal + cpu_guest
				
				if last_net_bytes_send==0 and last_net_bytes_send==0 and last_io_read == 0 and last_io_write == 0:
						last_net_bytes_send = param['net_bytes_sent']
						last_net_bytes_recv = param['net_bytes_recv']
						last_io_read = io_read
						last_io_write = io_write
						last_io_read_time = io_read_time
						last_io_write_time = io_write_time
						last_cpu_user = cpu_user
						last_cpu_nice = cpu_nice
						last_cpu_system = cpu_system
						last_cpu_idle = cpu_idle
						last_cpu_iowait = cpu_iowait
						last_cpu_irq = cpu_irq
						last_cpu_softirq = cpu_softirq
						last_cpu_steal = cpu_steal
						last_cpu_guest = cpu_guest
						last_cpu_total = cpu_total
		
						param['b_s_ps'] = 0
						param['b_r_ps'] = 0
						param["io_r"] = 0
						param["io_w"] = 0
						param["io_rt"] = 0
						param["io_wt"] = 0
						param['CPU_us'] = 0
						param['CPU_ni'] = 0
						param['CPU_sy'] = 0
						param['CPU_id'] = 0
						param['CPU_wa'] = 0
						param['CPU_hi'] = 0
						param['CPU_si'] = 0
						param['CPU_st'] = 0
						param['CPU_gu'] = 0
				else:
						param['b_s_ps'] = (long(param['net_bytes_sent']) - long(last_net_bytes_send))/5
						param['b_r_ps'] = (long(param['net_bytes_recv']) - long(last_net_bytes_recv))/5
						last_net_bytes_send = param['net_bytes_sent']
						last_net_bytes_recv = param['net_bytes_recv']
						param["io_r"] = (long(io_read) - long(last_io_read))/5
						param["io_w"] = (long(io_write) - long(last_io_write))/5
						if param["io_r"] != 0:
							param["io_sr"] = (long(io_read_time) - long(last_io_read_time))/ (5 * param["io_r"])
						else:
							param["io_sr"] = (long(io_read_time) - long(last_io_read_time)) / 5
						if param["io_w"] != 0:
							param["io_sw"] = (long(io_write_time) - long(last_io_write_time))/ (5 * param["io_w"])
						else:
							param["io_sw"] = (long(io_write_time) - long(last_io_write_time))/ 5
						cpu_interval = cpu_total - last_cpu_total
						param['CPU_us'] = "%.4f" % (float((cpu_user - last_cpu_user) / cpu_interval))
						param['CPU_ni'] = "%.4f" % (float((cpu_nice - last_cpu_nice) / cpu_interval))
						param['CPU_sy'] = "%.4f" % (float((cpu_system - last_cpu_system) / cpu_interval))
						param['CPU_id'] = "%.4f" % (float((cpu_idle - last_cpu_idle) / cpu_interval))
						param['CPU_wa'] = "%.4f" % (float((cpu_iowait - last_cpu_iowait) / cpu_interval))
						param['CPU_hi'] = "%.4f" % (float((cpu_irq - last_cpu_irq) / cpu_interval))
						param['CPU_si'] = "%.4f" % (float((cpu_softirq - last_cpu_softirq) / cpu_interval))
						param['CPU_st'] = "%.4f" % (float((cpu_steal - last_cpu_steal) / cpu_interval))
						param['CPU_gu'] = "%.4f" % (float((cpu_guest - last_cpu_guest) / cpu_interval))
						last_cpu_user = cpu_user
						last_cpu_nice = cpu_nice
						last_cpu_system = cpu_system
						last_cpu_idle = cpu_idle
						last_cpu_iowait = cpu_iowait
						last_cpu_irq = cpu_irq
						last_cpu_softirq = cpu_softirq
						last_cpu_steal = cpu_steal
						last_cpu_guest = cpu_guest
						last_cpu_total = cpu_total
						last_io_read = io_read 
						last_io_write = io_write
						last_io_read_time = io_read_time
						last_io_write_time = io_write_time
					
				param['mem_p'] = float(param['mem_used']) / float(param['mem_total'])	
				param['mem_p'] = "%.4f" % float(param['mem_p'])
				param['mem_f'] = param['mem_free']
				param['mem_t'] = param['mem_total']
				param['mem_ca_p'] = "%.4f" % (float(psutil.cached_phymem())/float(param['mem_t']))
				param['mem_bu_p'] = "%.4f" % (float(psutil.phymem_buffers())/float(param['mem_t']))
				if float(param['vmem_total']) ==0:
					param['vmem_p'] = 0
				else:				
					param['vmem_p'] = float(param['vmem_used']) / float(param['vmem_total'])
					
				param['vmem_p'] = "%.4f" % float(param['vmem_p'])		
				param['vmem_f'] = param['vmem_free']
				param['vmem_t'] = param['vmem_total']
				
				param['d_p'] = ""#"%.2f" % float(param['disk_percent'])
				param['d_f'] = ""#param['disk_free']
				param['d_t'] = ""#param['disk_total']
				param['d_d'] = ""
				
				param['format'] = 0
				
				data = psutil.disk_partitions()
				disk = "";
				for d in data:
					disk = disk + d[1] + ";"
					diskdata =  psutil.disk_usage(d[1])
					param = self.getParams(param, "disk", diskdata)	
					param['d_f'] = param['d_f'] + param['disk_free'] + ";" 
					param['d_p'] = param['d_p'] + "%.4f" % (float(param['disk_percent'])/100) + ";"
					param['d_t'] = param['d_t'] + param['disk_total'] + ";"
					param['d_d'] = param['d_d'] + d[0] + ";"
					del param['disk_free']
					del param['disk_percent']
					del param['disk_total']
					del param['disk_used']
				disk = disk.strip(';')
				param['d_f'] = param['d_f'].strip(';')
				param['d_t'] = param['d_t'].strip(';')
				param['d_p'] = param['d_p'].strip(';')
				param['d_d'] = param['d_d'].strip(';')
				
				param['disk'] = disk
				del param['net_bytes_sent']
				del param['net_bytes_recv']
				del param['net_packets_recv']
				del param['net_packets_sent']
				del param['mem_used']
				del param['mem_free']
				del param['mem_total']
				del param['mem_percent']
				del param['vmem_percent']
				del param['vmem_total']
				del param['vmem_free']
				del param['vmem_used']
				
					
				tmp = re.findall("\d+\.\d+|\d+", str(os.getloadavg()))
				param['load'] = "%.2f" % float(tmp[0])
				param['time'] = time.time()
				#param['load'][1] = "%.2f" % float(param['load'][1])
				#param['load'][2] = "%.2f" % float(param['load'][2])
				
				#param['load'] = param['load'][0]+"-"+param['load'][1]+"-"+ param['load'][2]
				#print param['load']
				#print param
								
				#param['method'] = 'record_instance_data'
				url = '?method=record_instance_data';
				for key in param.keys():
					url = url+"&"+key+"="+str(param[key])
				#url = url.replace("/","$")
				del processlist[:]
				#paramss = urllib.urlencode(param)
				#headers = {"Content-type": "application/x-www-form-urlencoded","Accept": "text/plain"}
				conn = httplib.HTTPSConnection("api.madeiracloud.com")				
				conn.request("GET", "/monitor/"+url)
				response = conn.getresponse()
				command = response.read()
				command = command.strip()
				conn.close()
				toDo = {}
				#setting['CPU_interval'] = 0.0
				ary = command.split(';')
				for opt in ary:
					if opt.strip() == '':
						continue
					tmp = opt.split(':')
					if(len(tmp)==1):
						continue
					toDo[tmp[0]] = tmp[1]
				#print toDo
				if "Stop" in command:
					os.system("service madeiracloud stop")
				'''		
				if 'Process' in command:
					p = toDo['Process'].split(',')
					for eachP in p:
						if eachP not in processlist and eachP.strip() != '':
							processlist.append(eachP)
							setting[eachP+"-CPU_interval"] = 0.0
					
				if 'Setting' in command:		
					s = toDo['Setting'].split(',')
					for eachS in s:
						if eachS.strip() == '':
							continue
						tmp = eachS.split('=')
						if tmp[0] in setting:
							if tmp[0] == 'disk_path':
								if os.path.exists(tmp[1]):
									setting[tmp[0]] = tmp[1]
									continue
								else:
									continue
							setting[tmp[0]] = tmp[1]
				'''
				#print i
				end_time = time.time()
				diff = end_time - start_time
				sleep_time = 4.5 - diff
				time.sleep(sleep_time)
			except Exception, msg:		
				try:
					conn = httplib.HTTPSConnection("api.madeiracloud.com")
					conn.request("GET", "/monitor/?method=errorReport&msg="+str(msg)+"&key="+access_key)
					response = conn.getresponse()
					response.read()
					conn.close()		
					time.sleep(120)
					continue
				except Exception, msg1:	
					continue

if __name__ == "__main__":
	daemon = Madeira()
	daemon.run()
	'''
	if len(sys.argv) == 2:
		if 'start' == sys.argv[1]:			
			daemon.start()			
		elif 'stop' == sys.argv[1]:
			daemon.stop()
		elif 'restart' == sys.argv[1]:
			daemon.restart()
		else:
			print "Unknown command"
			sys.exit(2)
		sys.exit(0)
	else:
		print "usage: %s start|stop|restart" % sys.argv[0]
		sys.exit(2)
	'''