# Requirements:

* Handle concurrent services booking by clients and staff that will need:
    - row locking
    - atomic transactions
    - constraint enforcement

* Backoffice in a separated FE connected to the admin api to manage: 
    - services
    - clients
    - staff
    - prices
    - schedules
    - reports

* Authentication and authorization:
    - JWT token
    - Session token 

* Cron jobs / automatic tasks:
    Examples:
    - reminders via SMS
    - reminders via email
    - monthly report with activity and revenue for staff users
    - sync services with staff google calendar

    Technology: DjangoQ

* Notifications:
    SMS via providers:
        Twilio
        MessageBird
        Vonage

* Integrations:
    Google Calendar API