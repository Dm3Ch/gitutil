import argparse
import os
import git
import sys

from pprint import pprint

def branch_exist(heads, branch_name):
  for head in heads:
    if head.name == branch_name:
      return True
  return False

parser = argparse.ArgumentParser()
parser.add_argument("source_branch", help="Source branch for merge")
parser.add_argument("target_branch", help="Target branch for merge")
args = parser.parse_args()

print('Source branch: ' + args.source_branch)
print('Target branch: ' + args.target_branch)

repo_dir = os.getcwd()

print('Repo dir: ' + repo_dir + '\n')

try:
  repo = git.Repo(repo_dir)
except git.InvalidGitRepositoryError:
  print('[ERROR] Current dirrectory doesn\'t contain git repository.')
  sys.exit(1)


if not branch_exist(repo.heads, args.source_branch):
  print('[ERROR] Source branch \'{}\' doesn not exist'.format(args.source_branch))
  sys.exit(2)

if not branch_exist(repo.heads, args.target_branch):
  print('[ERROR] Target branch \'{}\' doesn not exist'.format(args.target_branch))
  sys.exit(2)

try:
  repo.git.checkout(args.target_branch)
  repo.git.merge('--squash', args.source_branch)
  repo.git.commit('-m', 'Merged \'{0}\' branch into \'{1}\''.format(args.source_branch, args.target_branch))
except git.GitCommandError as err:
  command, status, stderr_value, stdout_value = err.args
  print('[ERROR] Error while merging:\nCommand: git {0}\nStatus: {1}\nStderr: {2}\nStdout: {3}'.format(command[1], status, stderr_value, stdout_value))
  sys.exit(3)

print('Succesfully exit')
