# upTimeTracker
Track websites and notify users via email when websites go down and get up again. This script also logs every up and down incident, and the user can add errors to the ignore list in order to ignore unwanted notifications. Include the name of the site, the URL, the reason for the downtime, the resolved time, and the duration of the incident in the notification email. 

Cronjob (on Linux) or Task Scheduler (on Windows) can be used to execute the script. The user only needs to interact with the ``website.json`` file placed in the ``assets`` directory. The website.json file can be used to customize email settings, add additional websites for tracking, and add ignore errors.

## How to run the script;
``python3 upTimeTracker.py -u <email_username> -p <email_password> -s <email_server> -o <email_port> -f <email_from>``

## Screenshots of the notification email;

Down Time             |  Up Time
:-------------------------:|:-------------------------:
![down](https://user-images.githubusercontent.com/87106402/201993461-e587e18e-bb7a-4c6a-98b1-86535379c585.png) |  ![up](https://user-images.githubusercontent.com/87106402/201993351-1ac05fe3-7409-4391-aef9-3c0ac46f3d0c.png)
