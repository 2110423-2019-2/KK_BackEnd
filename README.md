# CC-BE

CC-BE is a backend server stack for the courtcatch project using Django REST Framework.


## Usage

	cd into root cc-be directory
	$ pip install django
	$ pip install djangorestframework
	$ python3 manage.py runserver
	To authenticate, POST to /auth/ then put the token in the header as such {'Authorization': 'Token <token>'}

## Available Command

	BROWSER	/admin/
	GET	/api/user/
	POST	/api/user/
	GET	/api/user/<username>/
	POST	/api/user/<username>/change_password/
	POST	/api/user/<username>/add_credit/
	GET	/api/log/
	GET	/api/log/<username>/
	GET	/api/court/
	POST	/api/court/
	GET	/api/court/<courtname>/
	POST	/api/court/<courtname>/rate_court/
	POST	/api/court/<courtname>/add_image/
	GET	/api/document/
	POST	/api/document/
	GET	/api/document/<username>/
	POST	/auth/

