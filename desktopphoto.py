# Reddit desktop photo bot

import requests
import requests.auth
import json
import operator
import os
import datetime
import subprocess

def get_access_token(sensitive):
	client_auth = requests.auth.HTTPBasicAuth(sensitive[0], sensitive[1])
	post_data = {"grant_type": "password", "username": sensitive[2], "password": sensitive[3]}
	headers = {"User-Agent": sensitive[4]}

	response = requests.post("https://www.reddit.com/api/v1/access_token", auth=client_auth, \
    	data = post_data, headers=headers).json()
	return response['access_token']

def get_top_post(access_token, sensitive, today):

	headers = {"User-Agent": sensitive[4]}
	headers["Authorization"] = "bearer %s" % access_token
	headers['sort'] = 'top'
	headers['t'] = 'day'

	response = requests.get("https://oauth.reddit.com/r/earthporn", headers=headers).json()

	data = [i['data'] for i in response['data']['children']]
	data = sorted(data, key=lambda x:x['score'], reverse=True)

	print "\n\nToday's top post is:"
	print data[0]['title']
	print "\nWith a score of: " + str(data[0]['score']) + "\n\n"

	r = requests.get(data[0]['url'])

	print "Saving to desktop..."
	
	filename = os.path.join(os.path.expanduser('~'), "Desktop", "%s.jpg" % today)

	with open(filename, 'wb') as photo:
		photo.write(r.content)

def set_as_desktop(desktops, today):

	if desktops > 1:
		script = """osascript -e 'set N to %d
			set theFile to POSIX file ((system attribute "HOME") & "/Desktop/%s.jpg")
			repeat with k from 18 to (18 + N - 1)
				tell application "System Events" to key code k using {control down}
				delay 1
				tell application "Finder" to set desktop picture to theFile
				delay 1
			end repeat'
			""" % (desktops, today)
			
		print "Setting to all %d of these desktops..." % desktops		

	elif desktops == 1:
		# Works for 1 desktop/space
		script = "osascript -e 'tell application \"Finder\" to set desktop picture to " \
			"POSIX file ((system attribute \"HOME\") & \"/Desktop/%s.jpg\")'" % today
	
		print "Setting to this one and only desktop..."
	
	subprocess.Popen(script, shell=True)



def main():
	with open("sensitive.txt", "r") as fp:
		sensitive = [line.strip("\n") for line in fp]
	
	today = datetime.datetime.now().strftime("%d-%y")
	
	access_token = get_access_token(sensitive)
	get_top_post(access_token, sensitive, today)

	desktops = 4  # Set this int to the number of desktops to set
	
	set_as_desktop(desktops, today)	

if __name__ == "__main__":
	main()