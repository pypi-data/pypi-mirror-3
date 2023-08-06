import urllib, urllib2, cookielib
from HTMLParser import HTMLParser
class Jobmine:

    def login(self, userid, pwd):

        self.url = "https://jobmine.ccol.uwaterloo.ca/psp/SS/?cmd=login"
        self.form_data = {'userid' : userid, 'pwd' : pwd}
        self.jar = cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.jar))
        self.form_data = urllib.urlencode(self.form_data)
        self.resp = self.opener.open(self.url, self.form_data)

    def get_apps(self):

        self.resp = self.opener.open('https://jobmine.ccol.uwaterloo.ca/psc/SS/EMPLOYEE/WORK/c/UW_CO_STUDENTS.UW_CO_APP_SUMMARY.GBL?pslnkid=UW_CO_APP_SUMMARY_LINK&amp%3bFolderPath=PORTAL_ROOT_OBJECT.UW_CO_APP_SUMMARY_LINK&amp%3bIsFolder=false&amp%3bIgnoreParamTempl=FolderPath%2cIsFolder&PortalActualURL=https%3a%2f%2fjobmine.ccol.uwaterloo.ca%2fpsc%2fSS%2fEMPLOYEE%2fWORK%2fc%2fUW_CO_STUDENTS.UW_CO_APP_SUMMARY.GBL%3fpslnkid%3dUW_CO_APP_SUMMARY_LINK%26amp%253bFolderPath%3dPORTAL_ROOT_OBJECT.UW_CO_APP_SUMMARY_LINK%26amp%253bIsFolder%3dfalse%26amp%253bIgnoreParamTempl%3dFolderPath%252cIsFolder&PortalContentURL=https%3a%2f%2fjobmine.ccol.uwaterloo.ca%2fpsc%2fSS%2fEMPLOYEE%2fWORK%2fc%2fUW_CO_STUDENTS.UW_CO_APP_SUMMARY.GBL%3fpslnkid%3dUW_CO_APP_SUMMARY_LINK&PortalContentProvider=WORK&PortalCRefLabel=Applications&PortalRegistryName=EMPLOYEE&PortalServletURI=https%3a%2f%2fjobmine.ccol.uwaterloo.ca%2fpsp%2fSS%2f&PortalURI=https%3a%2f%2fjobmine.ccol.uwaterloo.ca%2fpsc%2fSS%2f&PortalHostNode=WORK&NoCrumbs=yes&PortalKeyStruct=yes')
        self.parser = MyHTMLParser()
        self.parser.feed(self.resp.read()) 
        return self.parser.lst

class MyHTMLParser(HTMLParser):

    lst = {} 
    item = None
    job_id = None
    def handle_starttag(self, tag, attr):

        if tag == 'span' and len(attr) == 2:
            if 'UW_CO_APPS_VW2_UW_CO_JOB_ID$' in attr[1][1]:
                self.item = 'job_id'
            elif 'UW_CO_JOBINFOVW_UW_CO_PARENT_NAME$26$$' in attr[1][1]: 
                self.item = 'job_name'
            elif 'UW_CO_JOBSTATVW_UW_CO_JOB_STATUS$30$$' in attr[1][1]:
                self.item = 'job_status'
            elif 'UW_CO_APPSTATVW_UW_CO_APPL_STATUS$31$$' in attr[1][1]:
                self.item = 'app_status'
            elif 'UW_CO_JOBAPP_CT_UW_CO_MAX_RESUMES$35$$' in attr[1][1]:
                self.item = 'app_number'
            else:
                self.item = None
        else:
            self.item = None

    def handle_data(self, data):

        if self.item == 'job_id' and data.strip():
            self.lst[int(data)] = {}
            self.job_id = int(data)
        elif self.item == 'job_name' and data.strip():
            self.lst[self.job_id]['job_name'] = data
        elif self.item == 'job_status' and data.strip():
            self.lst[self.job_id]['job_status'] = data
        elif self.item == 'app_status' and data.strip():
            self.lst[self.job_id]['app_status'] = data
        elif self.item == 'app_number' and data.strip():
            self.lst[self.job_id]['app_number'] = data
