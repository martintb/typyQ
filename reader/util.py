def dfs(graph, start, goal=None):
  stack = [(start, [start])]
  while stack:
    (vertex, path) = stack.pop()
    for next in graph[vertex] - set(path):
      stack.append((next, path + [next]))
  return path


def parse_jobs(job_list):
  job_list = sorted(job_list,key=lambda x: x.num,reverse=False)

  # First the 'job depedency/predecessor graph' needs to be constructed
  # for the depth-first-search (dfs) algorithm for work correctly.
  # job_dict  is constructed simultaneously so we can easily get the job_state from a job_num
  graph = {}
  job_dict = {}
  for job in job_list:
    neighbors = []
    if job.predecessor:
      neighbors.append(job.predecessor)
    graph[job.num] = set(neighbors)
    job_dict[job.num] = job
  
  # Searches the graph and creates dependecy paths using dfs
  # Starts at end of job_list b/c we can follow the last job
  # in a branch all the way up the tree
  jobno_groups = []
  checked_set = set() # this will eventually contain all job numbers in queue
  for job in reversed(job_list):
    if (set([job.num]) - checked_set):#if job.num is in checked_set, this 'if' will be false
      tree = dfs(graph,job.num)
      checked_set = checked_set | set(tree) #this adds new, unique values to checked_set
      jobno_groups.append(tree)
  
  #Loop over and add job state to job num tree
  jobs = []
  for group in jobno_groups:
    job_group = []
    for jobno in reversed(group):
      job = job_dict[jobno]
      job.stateno = str(jobno)+':'+ job.state
      job_group.append(job)
    jobs.append(job_group)

  # sort jobs by user name
  jobs = sorted(jobs,key = lambda x: x[0].user)
  return jobs
