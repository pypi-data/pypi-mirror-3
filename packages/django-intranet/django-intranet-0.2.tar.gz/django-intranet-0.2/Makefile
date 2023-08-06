# Local development management
clean:
	find -L . -name "*~" -exec rm -fr {} \;
	find -L . -name "*.pyc" -exec rm -fr {} \;
	find -L . -name ".DS_Store" -exec rm -fr {} \;
	find -L . -name "Thumbs.db" -exec rm -fr {} \;
	find -L . -name "Thumbs.db:encryptable" -exec rm -fr {} \;

messages-fr:
	django-admin.py makemessages -l fr

js-messages-fr:
	django-admin.py makemessages -d djangojs -l fr 

compilemessages:
	django-admin.py compilemessages
