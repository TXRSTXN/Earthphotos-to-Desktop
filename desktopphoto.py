# Reddit desktop photo bot

import requests, json, os, datetime, time, subprocess

def get_access_token(sensitive):
	client_auth = requests.auth.HTTPBasicAuth(sensitive[0], sensitive[1])
	post_data = {"grant_type": "password", "username": sensitive[2], "password": sensitive[3]}
	headers = {"User-Agent": sensitive[4]}

	response = requests.post("https://www.reddit.com/api/v1/access_token", auth=client_auth, \
    	data = post_data, headers=headers).json()
	return response['access_token']

def get_top_post(access_token, sensitive):

	headers = {"User-Agent": sensitive[4]}
	headers["Authorization"] = "bearer %s" % access_token
	headers['sort'] = 'top'
	headers['t'] = 'day'

	response = requests.get("https://oauth.reddit.com/r/earthporn", headers=headers).json()

	data = [i['data'] for i in response['data']['children']]
	data = sorted(data, key=lambda x:x['score'], reverse=True)
	return data

def save_photo_file(data, today):
	print "Attempting to save file..."

	directory = os.getcwd() + "/photos"
	if not os.path.exists(directory):
   		os.makedirs(directory)

	list_of_filetypes = ["jpg", "jpeg", "gif", "png"]

	for pic in data:
		filetype = pic['url'].lower().split(".")[-1]	
		if filetype not in list_of_filetypes:
			print "Unable to use " + pic['title'] + " due to filetype error."
		else:
			try:
				r = requests.get(pic['url'])
				print "\n\nUsing " + pic['title']
				print "With a score of: " + str(data[0]['score']) + "\n\n"
				break
			except:
				print "Unable to use " + pic['title'] + " due to download error."
			
	filename = os.getcwd() + "/photos/%s.%s" % (today, filetype)

	with open(filename, 'wb') as photo:
		photo.write(r.content)
	return filename
	
def set_as_desktop(filename, desktops, today):
	if desktops > 1:
		script = """osascript -e 'set N to %d
			set theFile to POSIX file ("%s")
			repeat with k from 18 to (18 + N - 1)
				tell application "System Events" to key code k using {control down}
				delay 1
				tell application "Finder" to set desktop picture to theFile
				delay 1
			end repeat'
			""" % (desktops, filename)
			
		print "Setting to all %d of these desktops. Stand back...\n" % desktops		

	elif desktops == 1:
		# Works for 1 desktop/space
		script = "osascript -e 'tell application \"Finder\" to set desktop picture to " \
			"POSIX file (\"%s\")'" % filename
	
		print "Setting to this one and only desktop..."
	
	time.sleep(2)
	subprocess.Popen(script, shell=True)



def main():
	
	script_directory = os.path.dirname(os.path.realpath(__file__))

	with open(os.path.join(script_directory, "sensitive.txt"), "r") as fp:
		sensitive = [line.strip("\n") for line in fp]
	
	today = datetime.datetime.now().strftime("%d-%y")
	
	access_token = get_access_token(sensitive)
	data = get_top_post(access_token, sensitive)
	filename = save_photo_file(data, today)
	desktops = 4  # Set this int to the number of desktops to set
	
	set_as_desktop(filename, desktops, today)	

if __name__ == "__main__":
	main()