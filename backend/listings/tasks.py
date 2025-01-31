from .classification import ListingTagClassifier
from huey.contrib.djhuey import db_periodic_task, db_task, on_commit_task, task

@db_task()
def do_some_queries():
    # This task executes queries. Once the task finishes, the connection
    # will be closed.
    pass

#@on_commit_task()
@task()
def generate_tags(title, description):
    INCLUDE_DESC = False
    # This task executes queries. Once the task finishes, the connection
    # will be closed.
    ltg = ListingTagClassifier.ListingTagClassifier()
    ltg.load_model()
    listing_text = [title.strip().lower() + description.strip().lower()] if INCLUDE_DESC else [title.strip().lower()]
    
    top_tags = ltg.predict_listing_tags(listing_text)
    print(top_tags)
    pass