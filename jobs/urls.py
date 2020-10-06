from django.urls import include, path, re_path
from . import views


urlpatterns = [
    re_path(r'^husky/v1/hash/tasks/(?P<pk>.+)$',   # Url to get update or delete a job
        views.get_delete_update_job.as_view(),
        name='get_delete_update_job'
    ),
    path('husky/v1/hash/tasks/',    # urls list all and create new one
        views.get_post_jobs.as_view(),
        name='get_post_jobs'
    )
]