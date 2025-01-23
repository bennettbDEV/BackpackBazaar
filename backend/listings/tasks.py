from huey.contrib.djhuey import db_periodic_task, db_task, on_commit_task

@db_task()
def do_some_queries():
    # This task executes queries. Once the task finishes, the connection
    # will be closed.
    pass

@on_commit_task()
def generate_tags(title, description):
    # This task executes queries. Once the task finishes, the connection
    # will be closed.
    pass