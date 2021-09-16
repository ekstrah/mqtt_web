import argparse

parser = argparse.ArgumentParser(description='MQTT Subscriber API that handles mongodb and mqtt-sub')
group1 = parser.add_argument_group("Handling Topic Words")
parser.add_argument('--topic', help="topic words eg; foo/bar", type=str)

args = parser.parse_args()
if args.topic == None:
    args.topic = "#"
print(args.topic)