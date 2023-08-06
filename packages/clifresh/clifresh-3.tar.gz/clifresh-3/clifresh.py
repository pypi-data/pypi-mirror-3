import os,argparse,json
from refreshbooks import api

CONFIG_FILE_LOCATION = os.path.expanduser("~/.clifresh/clifresh.config")

parser = argparse.ArgumentParser(description='''Log time in the freshbooks
	invoicing tool.
    ''')

subparser = parser.add_subparsers(dest="action")

project_parser = subparser.add_parser("projects")

tasks_parser = subparser.add_parser("tasks")
tasks_parser.add_argument("-p","--project",type=int,required=True)

log_parser = subparser.add_parser("log")
log_parser.add_argument("-p","--project",type=int,required=True)
log_parser.add_argument("-t","--task",type=int,required=True)
log_parser.add_argument("-m","--message",type=str,required=True)
log_parser.add_argument("hours",type=float)

config_parser = subparser.add_parser("config")
config_parser.add_argument("--url")
config_parser.add_argument("--token")

try:
	os.mkdir(os.path.expanduser("~/.clifresh"))
except:pass # if we get an exception, it means the directory exists
configfile = open(CONFIG_FILE_LOCATION,"a+")

try:
	config = json.loads(configfile.read())
	configfile.close()
except ValueError:
	config = {}
	configfile.seek(0)
	configfile.write(json.dumps(config))
	configfile.close()

class Project(object):
	def __init__(self,obj):
		self.id = obj.project_id
		self.name = obj.name
		self.tasks = obj.tasks
	def __str__(self):
		return "%i - %s" % (self.id,self.name)

class Task(object):
	def __init__(self,obj):
		self.id = obj.task_id
		self.name = obj.name
		self.billable = obj.billable
		self.rate = obj.rate
	def __str__(self):
		return "%i - %s" % (self.id,self.name)


def get_project_list(freshbooks):
	projects = freshbooks.project.list().projects.project
	return [Project(project) for project in projects]

def get_project(freshbooks,project_id):
	return freshbooks.project.get(project_id=project_id).project

def get_project_tasks(freshbooks,project=None,project_id=None):
	tasks = freshbooks.task.list(project_id=(project_id or project.id)).tasks.task
	return [Task(task) for task in tasks]

def log_time(freshbooks,project_id,task_id,hours,notes):
	return freshbooks.time_entry.create(time_entry={
		"project_id":project_id,
		"task_id":task_id,
		"hours":hours,
		"notes":notes
	})

def main():
	args = parser.parse_args()

	if args.action == "config":
		if args.url: config['url'] = args.url 
		if args.token: config['token'] = args.token 
		configfile = open(CONFIG_FILE_LOCATION,"a")
		configfile.write(json.dumps(config))
		configfile.close()

	if not config.get("url"):
		print "You have not set your freshbooks url:"
		print "clifresh config --url [companyname.freshbooks.com]"
		return False
	if not config.get("token"):
		print "You have not set your api token:"
		print "clifresh config --token [your_token]"
		return False

	freshbooks = api.TokenClient(
		config.get("url"),
		config.get("token"),
		user_agent='clifresh/1.0'
	)

	if args.action == "projects":
		for project in get_project_list(freshbooks):
			print project
	elif args.action == "tasks":
		print get_project(freshbooks,args.project).name
		for task in get_project_tasks(freshbooks,project_id=args.project):
			print task
	elif args.action == "log":
		log = log_time(freshbooks,args.project,args.task,args.hours,args.message)
		if log.attrib['status'] == 'ok':
			print "Time sucessfully logged!"

if __name__ == "__main__":
	main()