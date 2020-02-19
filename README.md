# CC-BE

CC-BE is a backend server stack for the courtcatch project using Django REST Framework.


## Usage

	cd into root cc-be directory
	$ source venv/bin/activate
	$ python3 manage.py runserver
	To authenticate, POST to /auth/ then put the token in the header as such {'Authorization': 'Token <token>'}

## Available Command

	BROWSER	/admin/
	GET	/api/user/
	POST	/api/user/
	GET	/api/user/<username>/
	GET	/api/user/<username>/courts/
	POST	/api/user/<username>/change_password/
	POST	/api/user/<username>/add_credit/
	GET	/api/log/
	GET	/api/log/<username>/
	GET	/api/court?name=<name>&rating=<min_rating>&dist=<max_dist>&lat=<lat>&long=<long>&sort_by=<name|-name|dist|rating>
	POST	/api/court/
	GET	/api/court/<courtname>/
	POST	/api/court/<courtname>/rate_court/
	POST	/api/court/<courtname>/add_image/
	GET	/api/document/
	POST	/api/document/
	GET	/api/document/<username>/
	POST	/auth/

