import procrastinate

app = procrastinate.App(
    connector=procrastinate.contrib.django.DjangoConnector(),
    import_paths=[
        "apps.notifications.tasks",
        "apps.reports.tasks",
    ],
)
