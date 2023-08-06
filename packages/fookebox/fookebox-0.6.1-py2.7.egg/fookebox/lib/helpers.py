"""Helper functions

Consists of functions to typically be used within templates, but also
available to Controllers. This module is available to templates as 'h'.
"""
# Import helpers as desired, or define your own, ie:
#from webhelpers.html.tags import checkbox, password

def event_type_name(event_type):
	names = ['Jukebox', 'Live band', 'DJ']
	return names[event_type]
