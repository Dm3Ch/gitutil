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

def get_merge_message(source_branch, target_branch):
  return 'Merged \'{0}\' branch into \'{1}\''.format(source_branch, target_branch)

#Checking if source branch is already merged into target branch and returns merge commit's sha hash
def get_merge_commit_sha(merge_message, target_branch_head):
  commit = target_branch_head.commit
  message = commit.message.strip()
  while commit.parents and not message == merge_message:
    commit = commit.parents[0]
    message = commit.message.strip()
  if message == merge_message:
    return commit.hexsha
  else:
    return False

def drop_commit(repo, commit_sha):
  try:
    repo.git.rebase('-p', '--onto', commit_sha+'^', commit_sha)
  except git.GitCommandError as err:
    command, status, stderr_value, stdout_value = err.args
    print('[ERROR] Error dropping previous merge commit:\n  Command: git {0}\n  Status: {1}\n  Stderr: {2}\n  Stdout: {3}'.format(command[1], status, stderr_value, stdout_value))
    sys.exit(3)

parser = argparse.ArgumentParser()
parser.add_argument("source_branch", help="Source branch for merge")
parser.add_argument("target_branch", help="Target branch for merge")
args = parser.parse_args()

print('[INFO] Source branch: ' + args.source_branch)
print('[INFO] Target branch: ' + args.target_branch)

repo_dir = os.getcwd()

print('[INFO] Repo dir: ' + repo_dir + '\n')

try:
  repo = git.Repo(repo_dir)
except git.InvalidGitRepositoryError:
  print('[ERROR] Current dirrectory doesn\'t contain git repository.')
  sys.exit(1)

heads = repo.heads
if not branch_exist(heads, args.source_branch):
  print('[ERROR] Source branch \'{}\' doesn not exist'.format(args.source_branch))
  sys.exit(2)

if not branch_exist(heads, args.target_branch):
  print('[ERROR] Target branch \'{}\' doesn not exist'.format(args.target_branch))
  sys.exit(2)

merge_message = get_merge_message(args.source_branch, args.target_branch)

merge_commit_sha = get_merge_commit_sha(merge_message, heads.master)
if merge_commit_sha:
  print('[INFO] Merge commit already exists in target branch with sha: ' + merge_commit_sha)
  drop_commit(repo, merge_commit_sha)
  print('[INFO] Merge commit \'{}\' sucessfully was dropped\n'.format(merge_commit_sha))

try:
  repo.git.checkout(args.target_branch)
  repo.git.merge('--squash', args.source_branch)
  repo.git.commit('-m', merge_message)
except git.GitCommandError as err:
  command, status, stderr_value, stdout_value = err.args
  print('[ERROR] Error while merging:\n  Command: git {0}\n  Status: {1}\n  Stderr: {2}\n  Stdout: {3}'.format(command[1], status, stderr_value, stdout_value))
  sys.exit(3)

print('[INFO] Successfully merged')
