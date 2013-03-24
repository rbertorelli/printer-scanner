#!/usr/bin/python

import socket
from urllib import urlopen
import re
from BeautifulSoup import BeautifulSoup
import datetime
import sys
import cPickle

#test an ip for 10 seconds before moving on
socket.setdefaulttimeout(10)

class crawler(object):
	def __init__(self, *args): 
		# check args in case class imported into another file
		if len(args) == 1:
			if args[0] == 'n':
				self.ip_list = self.createIPList()
				self.ip_list_old = cPickle.load(open('ip addresses.p'))
				self.update = 1
			else:
				raise ValueError('Incorrect option')
		elif len(args) == 0:

			self.ip_list = cPickle.load(open('ip addresses.p'))
			self.update = 0
		else:
			raise ValueError('Incorrect arguments')


	def createIPList(self,base='10.154.',botm='10',top='11'):

		output = []
		for x in (botm,top):
			for i in xrange(0,256):
				output.append(base+x+'.'+str(i))
		return output


	def findLevel(self,site,printer):

		level_tags = re.compile('\>(.*?)\<')
		level_tags_2 = re.compile('\\t(.*?)\\n')
		if printer == '1320':
			#1320: surrounded by <font class="sclf"></font> - there are two, though
			level = level_tags.findall(str(site.findAll('font', {"class": "sclf"})))[-2]
		elif printer == '2015':
			#Very much like 2035 & 2055 but html slightly different
			level = level_tags_2.findall(str(site.findAll('td',{"class": "SupplyName width10"})))[0].strip()
		
		else:
			#2035, & 2055: surrounded by <td class="supplyName width10"></td>
			level = level_tags.findall(str(site.findAll('td',{"class": "supplyName width10"})))[0]
		return level

	def getPrinterName(self,model,site):
		if model == '1320':
			title_string = re.compile('\Name:(.*?)\\n')
			name = title_string.findall(site)[0].strip()

		elif model == '2015':
			title_string = re.compile('\">(.*?)\&')
			name_div = str(site.findAll('div',{'class':'userId'})[0])
			name = title_string.findall(name_div)[0]

		elif model == '2035':
			name_div = str(site.findAll('div',{'class':'userId'})[0])
			title_string = re.compile('\>(.*?)\&')
			name = title_string.findall(name_div)[0]

		elif model == '2055':
			title_string = re.compile('\n(.*?)\&')
			name_div = str(site.findAll('div',{'class':'userId'})[0])
			name = title_string.findall(name_div)[0].strip()

		elif model == '3505':
			pass
		elif model == '3800':
			pass
		return name

	def html_write(self):
		found_ips = []

		date = datetime.datetime.now()

		day = str(date.day)
		month = str(date.month)
		year = str(date.year)

		#create html file & header

		html_file_name = 'printer log ' + year + '-' + month + '-' + day +'.html'

		html_log = open(html_file_name,'w')
		html_log.write('<html>\n<head>\n<title>\nPrinter Log:'+year+'-'+month+'-'+day+'\n</title>\n</title<body bgcolor=gray><table>\n<tr><td><b>IP</b></td><td><b>Name<b></td><td><b>Black</b></td><td><font color=cyan><b>Cyan</b></font></td><td><font color=magenta><b>Magenta</b></font></td><td><font color=yellow><b>Yellow</b></font></td></tr>')

		#loop through all ips

		for i in self.ip_list:
			try:
				soup = BeautifulSoup(urlopen('http://' +i))
				model = soup.title.string
				if '1320' in re.findall('\d+',model):
					print '1320 found at ' + i
					url = 'http://' + i + '/hp/device/info_suppliesStatus.html'
					soup = BeautifulSoup(urlopen(url))

					# get printer name
					name = self.getPrinterName('1320', str(BeautifulSoup(urlopen('http://'+i+'/configpage.htm'))))
			
					# get level and log
					level = self.findLevel(soup,'1320')
					html_log.write('<tr><td>'+i+'</td><td>'+name+'</td><td>'+level+'</td></tr>\n')

				elif '2015' in re.findall('\d+',model):
					print '2015 found at ' + i
					url = 'http://' + i + '/hp/device/info_suppliesStatus.html'
					soup = BeautifulSoup(urlopen(url))

					# Get printer name
					name = self.getPrinterName('2015', BeautifulSoup(urlopen('http://'+i)))
			
					# Get level and log
					level = self.findLevel(soup,'2015')
					html_log.write('<tr><td>'+i+'</td><td>'+name+'</td><td>'+level+'</td></tr>\n')

				elif '2035' in re.findall('\d+',model):
					print '2035 found at ' + i
					url = 'http://' + i + '/SSI/supply_status.htm'
					soup = BeautifulSoup(urlopen(url))

					#Get printer name
					name = self.getPrinterName('2035',soup)
			
					# Get level and log
					level = self.findLevel(soup,'2035')
					html_log.write('<tr><td>'+i+'</td><td>'+name+'</td><td>'+level+'</td></tr>\n')

				elif '2055' in re.findall('\d+',model):
					print '2055 found at ' + i
					url = 'http://' + i + '/hp/device/supply_status.htm'
					soup = BeautifulSoup(urlopen(url))

					# Get printer name
					name = self.getPrinterName('2055',BeautifulSoup(urlopen('http://' + i)))
			
					# Get level and log
					level = self.findLevel(soup,'2055')
					html_log.write('<tr><td>'+i+'</td><td>'+name+'</td><td>'+level+'</td></tr>\n')

				elif '3505' in re.findall('\d+',model):
					print '3505 found at '+i
					url='http://'+i+'/hp/device/this.LCDispatcher?nav=hp.Supplies'
					soup = BeautifulSoup(urlopen(url))
					toner_html_block = soup.findAll('span',{'class':'hpConsumableBlockHeaderText'})
					toner_level_pattern = re.compile('\Text">(.*?)\<')
					levels = toner_level_pattern.findall(str(toner_html_block))
					html_log.write('<tr><td>'+i+'</td><td>3505</td><td>'+levels[0]+'</td><td>'+levels[1]+'</td><td>'+levels[2]+'</td><td>'+levels[3]+'</td></tr>\n')

				elif '3800' in re.findall('\d+',model):
					print '3800 found at ' + i
					url = 'http://' + i + '/hp/device/this.LCDispatcher?nav=hp.Supplies'
					soup = BeautifulSoup(urlopen(url))

					toner_html_block = soup.findAll('span',{'class':'hpConsumableBlockHeaderText'})
					toner_level_pattern = re.compile('\\n(.*?)\</')

					levels = [toner_level_pattern.findall(str(j))[0] for j in toner_html_block if toner_level_pattern.findall(str(j)) != ['']]
					html_log.write('<tr><td>'+i+'</td><td>3505</td><td>'+levels[0]+'</td><td>'+levels[1]+'</td><td>'+levels[2]+'</td><td>'+levels[3]+'</td></tr>\n')			

				else:
					print re.findall('\d+',model)[0] + ' found at ' + i
					html_log.write('<tr><td>'+i+'</td><td>'+re.findall('\d+',model)[0] +'</td><td>N/A</td></tr>\n')
				if self.update == 1:
					found_ips.append(i)
			
			#if timeout error

			except IOError:
				html_log.write('<tr><td>'+i+'</td><td>Not accessible</td></tr>\n')

		html_log.write('\n</table>\n</body>\n</html>')
		html_log.close()
		
		#update IP list
		if len(found_ips) > 0:
			self.ip_list_old.extend([i for i in set(found_ips) - set(self.ip_list_old)])
			cPickle.dump(self.ip_list_old,open('ip addresses.p','w'))
		return
	

def main():
	if len(sys.argv) == 2: #one option
		if sys.argv[1] == '-n': #the correct one
			bot = crawler('n')
		else:
			raise ValueError('Incorrect arguments')
	elif len(sys.argv) == 1: #default
		bot = crawler()
	else:
		raise ValueError('Only one argument allowed: -n')

	bot.html_write()
	
	return

if __name__ == '__main__':
	main()