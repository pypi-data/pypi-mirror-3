from models import ViewPoint

def on_app_start():
    for view_point in ViewPoint.objects.all():
        view_point.register_view_point()

"""
View point indexing complexities
new view point -> new index
on mongo type backends this is a non issue
on appspace indexing this is an issue
the space that does the indexing must be aware of all indexes
if a view point is created all other appspaces must be notified
django node to node communication, app 2 app
"""
