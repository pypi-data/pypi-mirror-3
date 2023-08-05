import webbrowser
import paths

def launch_help() :
	webbrowser.open('file://'+paths.get_share_location()+'help/index.html')
