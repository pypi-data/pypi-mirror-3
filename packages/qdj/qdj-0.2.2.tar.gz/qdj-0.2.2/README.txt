QDJ is like "django-admin.py startproject", but with your own project templates.


Example:
    Install qdj:
        # pip install qdj
    
    Create a project template:
        # qdj create
        Created Django 1.3 template in /Users/nath/.qdj/1.3
    
    Add a requirements file:
        # echo >>~/.qdj/1.3/files/requirements.txt "django == {{ django_version }}"
    
    Use the template:
        # qdj start myproject
    
    Show the created files:
        # find myproject
        myproject
        myproject/requirements.txt
        myproject/settings.py
        myproject/manage.py
        myproject/urls.py
        myproject/__init__.py
    
    Check requirements.txt:
        # cat myproject/requirements.txt
        django == 1.3.1
