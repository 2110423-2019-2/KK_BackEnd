# CC-BE

CC-BE is a backend server stack for the courtcatch project.


## Usage

	cd into root cc-be directory
	$python3 manage.py runserver
	To authenticate, POST to /auth/ then put the token in the head as such {'Authorization': 'Token <token>'}

## Avaliable Command

	BROWSER	/admin/
	GET	/api/user/
	GET	/api/user/<username>/
	POST	/api/user/<username>/
	POST	/api/user/<username>/change_password/
	POST	/api/user/<username>/add_credit/
	GET	/api/log/
	GET	/api/log/<username>/
	GET	/api/court/
	GET	/api/court/<courtname>/
	POST	/api/court/<courtname>/rate_court/
	GET	/api/document/
	POST	/api/document/
	GET	/api/document/<username>/
	POST	/auth/

