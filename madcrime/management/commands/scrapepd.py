from django.core.management.base import BaseCommand
from madcrime.models import Incident
from mechanize import Browser
from BeautifulSoup import BeautifulSoup
import urllib
import urllib2
import time, datetime
from django.utils.encoding import smart_str, smart_unicode

class Command(BaseCommand):
    help = 'Scrapes Madison Police Department Data'

    def handle(self, *args, **options):
        print ('\nStarting scrape at %s\n' % str(datetime.datetime.now()))
        
        # set some varibles to make life easier
        prefixIncidents = 'http://www.cityofmadison.com/incidentReports/'
        countIncidents = 0
        addressSuffix = ', Madison, Wis.'
        
        # use selectors to whittle
        # down to the content
        mech = Browser()
        urlIncidents = 'http://www.cityofmadison.com/incidentReports/incidentList.cfm?a=71&page=1'
        pageIncidents = mech.open(urlIncidents)
        htmlIncidents = pageIncidents.read()
        soupIncidents = BeautifulSoup(htmlIncidents)
        tableIncidents = soupIncidents.find('table', {'id': 'list'})
        rowsIncidents = tableIncidents.findAll('tr')[1:]
        
        # get length for our loop
        lengthIncidents = len(rowsIncidents)
        
        for row in rowsIncidents:
                
            # whittle through content
            cells = row.findAll('td')
            dateIncidents = cells[0].string
            linkIncidents = prefixIncidents + cells[1].a['href']
            caseIncidents  = cells[2].text.encode('utf-8')

            # save content to django models
            try:
                obj = Incident.objects.get(caseIncidents = caseIncidents)
                obj.dateIncidents = dateIncidents
                obj.linkIncidents = linkIncidents
                obj.caseIncidents = caseIncidents
                obj.save()
            except Incident.DoesNotExist:
                obj = Incident(dateIncidents = dateIncidents, linkIncidents=linkIncidents, caseIncidents = caseIncidents)
                obj.save()
                        	
        	# use selectors to whittle
        	# down to the content
        	mech = Browser()
        	urlDetails = linkIncidents
        	pageDetails = mech.open(urlDetails)
        	htmlDetails = pageDetails.read()
        	soupDetails = BeautifulSoup(htmlDetails)
        	
        	# hits incident detail table and returns the contents
        	tableDetails = soupDetails.find('table', {'id': 'incidentdetail'})
        	
        	# finds the tbody that contains the data
        	bodyDetails = tableDetails.find('tbody')
        
        	# find all of the rows in the table
        	rowsDetails = bodyDetails.findAll('tr')

            # create an empty dict
        	models = {}

        	# determine how many rows in the table
        	lengthDetails = len(rowsDetails)
        
        	# set the count
        	countDetails = 0
        
        	# each row do this
        	while (countDetails < lengthDetails):
        	   for item in rowsDetails:
        	       
        	       # create pairs
        	       labelDetails = item.find('th').text.encode('utf-8')
        	       dataDetails = item.find('td').text.encode('utf-8')
        	       
        	       # add to dict
        	       models[labelDetails] = dataDetails
        	       
        	       # repeat loop
        	       countDetails = countDetails + 1
        	   
        	   #print models
        	   if models.has_key('Incident Date'):
        	       dateDetails = models['Incident Date']
        	       obj.dateDetails = dateDetails
        	       obj.save()
        	       
        	   if models.has_key('Incident Type'):
        	       typeDetails = models['Incident Type']
        	       obj.typeDetails = typeDetails
        	       obj.save()
        	       
        	   if models.has_key('Address'):
        	       addressDetails = models['Address']
        	       obj.addressDetails = addressDetails + addressSuffix
        	       obj.save()
        	    
        	   if models.has_key('Suspect(s)'):
        	       suspectDetails = models['Suspect(s)']
        	   else:
        	       suspectDetails = 'None'
        	   obj.suspectDetails = suspectDetails
        	   obj.save()

        	   if models.has_key('Arrested'):
        	       arrestedDetails = models['Arrested']
        	       obj.arrestedDetails = arrestedDetails
        	       obj.save()

        	   if models.has_key('Victim'):
        	       victimDetails = models['Victim']
        	       obj.victimDetails = victimDetails
        	       obj.save()
        	       
        	   if models.has_key('Details'):
        	       detailsDetails = models['Details']
        	       obj.detailsDetails = detailsDetails[:3000]
        	       obj.save()
        	   

        print 'Scraper is finished'
        	   
  