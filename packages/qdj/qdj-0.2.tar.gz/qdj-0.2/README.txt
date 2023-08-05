QDJ is like "django-admin.py startproject", but with your own project templates.


Example:
    Create a project template:
        # qdj create
        Created template for Django 1.3 in ~/.qdj/templates/1.3
    
    Change the template:
        # echo >>~/.qdj/1.3/views.py "'''This is views.py for {{ project_name }}'''"
    
    And then use it:
        # qdj start myproject
        # head -n 1 myproject/views.py
        '''This is views.py for myproject'''
