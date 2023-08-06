import requests
import json
import os.path
import sys
from utils import get_server_config

class ConfluenceServer(object):
  def __init__(self, name, base_url, auth):
    self.name = name
    self.base_url = os.path.join(base_url, 'rest/mywork/latest/task')
    self.auth = auth

  def get_tasks(self):
    content = requests.get(self.base_url, auth=self.auth).content
    tasks = json.loads(content)
    todo = []
    for task in tasks:
      if task['status'] == 'TODO':
        task['server'] = self
        todo.append(task)

    return todo

  def add_task(self, text):
    req = requests.post(self.base_url, data=json.dumps({
        'title': text, 
        'status': 'TODO',
        'application': 'com.codeandstuff.workbox'
      }), 
      auth=self.auth,
      headers={'content-type': 'application/json'})

    if req.status_code == 200:
      return json.loads(req.content)

    return None

  def complete_task(self, task_id):
    req = requests.put("%s/%d" % (self.base_url, task_id), data=json.dumps({
        'status': 'DONE'
      }),
      auth=self.auth,
      headers={'content-type': 'application/json'})

    if req.status_code == 200:
      return json.loads(req.content)

    return None

  def remove_task(self, task_id):
    req = requests.delete("%s/%d" % (self.base_url, task_id),
        auth=self.auth)

    if req.status_code == 200:
      return True

    return False

def load_servers():
  server_config = get_server_config()
  if not server_config:
    print >> sys.stderr, "\n  You need to configure some Confluence servers. Try `workbox config` for some help.\n"
    sys.exit(1)

  return [ConfluenceServer(s['name'], s['base_url'], (s['username'], s['password'])) for s in server_config]

def get_tasks():
  federated_tasks = []
  for server in load_servers():
    federated_tasks += server.get_tasks()

  return federated_tasks

def add_task(title):
  return load_servers()[0].add_task(title)

