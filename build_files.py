import argparse
import ConfigParser
import os

import builder
from builder.skeleton import skeleton_handler
from helpers import common_utils

def load_config(config_path): 
	config_load = ConfigParser.ConfigParser()
	config_load.readfp(open(config_path))

	return config_load


def find_skeleton(component_type, component_name):
	return_path = ""
	components_dir = "skeletons" + os.sep + component_type + "s" + os.sep + component_name.strip(component_type + "_") + os.sep
	for subdir, dirs, files in os.walk(components_dir):
		for file in files:
			filepath = components_dir + file
			# if config.get(section, value).strip('"').strip("'") in filepath:
			if component_name in filepath:
				return_path = filepath
	return return_path



def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output', dest='verbose', default=False)
	parser.add_argument('-d', '--debug', action='store_true', help='Enable debugging output', dest='debug', default=False)
	parser.add_argument('-f', '--framework', help='The name of the framework to build for', dest='selected_framework')
	parser.add_argument('-e', '--encoder', help='The name of the encoder module to use for the client', dest='selected_encoder')
	parser.add_argument('-t', '--transport', help='The name of the transport module to use for the client', dest='selected_transport')
	parser.add_argument('-c', '--config', help='the/path/to/the/config file to use for the builder routine', dest='config_path')
	parser.add_argument('-b', '--buildpath', help='the/path/to place the built files into', dest='build_path')

	args = parser.parse_args()

	# Let's hardcode some values for right now...right
	# MASSIVE DEBUG / TODO / LOOK FOR ME

	args.selected_transport = "transport_imgur"
	args.selected_encoder = "encoder_lsbjpg"
	args.config_path = "sample_builder_config.config.sample"
	args.selected_framework = "cobalt_strike"


	# Let's load our config file
	global config
	config = load_config(args.config_path)

	# Create the builder object
	build = builder.Builder()

	# Let's assign the proper builder variables
	build.encoder = str(args.selected_encoder)
	build.transport = str(args.selected_transport)
	build.framework = str(args.selected_framework)
	build.build_path = str(args.build_path)

	# Run any tasks required to prepare the builder before hand.
	build.prep_builder()

	print "Building file(s) for %s, with %s and %s at %s" %(args.selected_framework, args.selected_transport, args.selected_encoder, args.build_path)

	# Let's start with building an encoder, which should be simple enough?
	encoder_skeleton = find_skeleton('encoder', str(args.selected_encoder).strip('"').strip("'"))
	build_skeleton = skeleton_handler.SkeletonHandler(encoder_skeleton)
	print "CURRENT TARGET SKELTON: " + build_skeleton.target_skeleton
	#built_encoder = build_skeleton.LoadSkeleton()
	build_skeleton.LoadSkeleton()
	print "Current encoder contents, before loop: " + "\n" + build_skeleton.GetCurrentFile()
	for item in config.items('encoder_options'):
		key = item[0]
		value = item[1]
		build_skeleton.target_var = key
		build_skeleton.regex_replacement_value_marker = '```\[var:::'+build_skeleton.target_var+'\]```'
		build_skeleton.new_value = value
		build_skeleton.ReplaceString()
		print "Current encoder contents, after loop: " + "\n" + build_skeleton.GetCurrentFile()
	# our newly minted encoder can now be accessed with `built_encoder.GetCurrentFile()`
	encoder_destination = args.build_path + os.sep + "encoder" + os.sep + args.selected_encoder + ".py"
	build.build_client_file(build_skeleton.GetCurrentFile(), build.build_destination)


main()
