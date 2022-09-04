# Cyber Security Base project I

LINK: https://github.com/sari-bee/CSB_project

The app is written with Python & Django.

1. Apply migrations with 
``
python3 manage.py migrate
``

2. Start the server with
``
python3 manage.py runserver
``

3. Find the app on localhost:8000/tasks

The app is a very simple Tasks list. The user can register, sign in, and then view and manipulate their Tasks list.

I have used OWASP 2021 list for the flaws.

## FLAW 1
Source links: [1](https://github.com/sari-bee/CSB_project/blob/5eaa25507a2fc741c875421056d4389d6e9e313e/tasks/templates/tasks/tasks.html#L30) [2](https://github.com/sari-bee/CSB_project/blob/5eaa25507a2fc741c875421056d4389d6e9e313e/tasks/views.py#L40)

Flaw 1 is cross-site request forgery (CSRF). CSRF tokens are added to forms submitted on websites to ensure that the submission is originating from the site itself. The form's CSRF token is checked and matched with the session token. If the CSRF token is not checked, a malicious intruder can lead a user into a false site through which the intruder can post information with the user's credentials.

In this project, a CSRF vulnerability has been introduced by disabling Django's built-in CSRF token check on the method addtask in views.py (source link 2) and omitting the CSRF token from the form adding a task on tasks.html (source link 1).

This can be fixed by removing the
```
@csrf_exempt
```
decorator from method addtask on views.py (source link 2) and by adding the line
```
{% csrf_token %}
```
as the first line in the addtask form on tasks.html (source link 1).

## FLAW 2
Source link: [1](https://github.com/sari-bee/CSB_project/blob/5eaa25507a2fc741c875421056d4389d6e9e313e/tasks/views.py#L73)

Flaw 2 is SQL injection (OWASP A03, Injection). When user input is not sanitized but instead incorporated directly into an SQL command, the malicious user can input data that will perform SQL commands that were not intended (such as dropping database tables). This can be prevented e.g. by always passing user inputs as parameters to SQL commands, instead of as raw data.

In this project, a raw SQL query has been used to fetch user details from the tasks_user database table when signing in (method signin in views.py, source link 1). In this query, the user input from the sign in form is used as raw data, which makes the query vulnerable to injection.

To fix this, there are several alternatives replacing rows 73-74 in views.py (source link 1). Firstly, the query can be applied using Django's ORM, which provides automatic protection from injection:

```
user = User.objects.get(username=username)
```

Alternatively, the raw SQL query could be done in a safe way by passing the user input as a parameter:

```
user = User.objects.raw('SELECT * FROM tasks_user WHERE username = %s', [username])[0]
```

## FLAW 3
Source link: [1](https://github.com/sari-bee/CSB_project/blob/5eaa25507a2fc741c875421056d4389d6e9e313e/tasks/views.py#L23)

Flaw 3 is allowing users to gain access to private data through URL manipulation (OWASP A01, Broken Access Control). If a user's credentials are not checked when loading a page, and if the URLs of pages containing private data are constructed in such a way that other users or intruders can decipher the logic behind URL construction, the site runs the risk of revealing sensitive information to outsiders.

In this project, the task listing for each user is under tasks/users/'username' and thus easily found if the usernames of other users are known. Further, there is no check to see if the user that is signed in is the one attempting to access the page (method tasks in views.py, source link 1). Thus, anyone who knows other users' usernames can access their task lists.

This flaw can be fixed by adding to the beginning of the tasks method (source link 1) a check to verify the username whose task list is attempted to access against that of the logged in user (session username), as follows:

```
if username != request.session['username']:
    return HttpResponseRedirect(reverse('error'))
```

Thus, if the username carried in the session of the user currently logged in does not match the username carried in the URL, the user is redirected to an error page.

## FLAW 4
Source link: [1](https://github.com/sari-bee/CSB_project/blob/5eaa25507a2fc741c875421056d4389d6e9e313e/tasks/views.py#L62)

Flaw 4 is storing passwords in an insecure way in the database (OWASP A07, Identification and Authentication Failures).

In this project, passwords are stored as plaintext in the database (source link 1). This means that if a malicious intruder gains control of the database, they will have instant access to all user credentials. 

This can be fixed by salting and hashing all created passwords before storing them in the database. Salting refers to adding random characters to the password. The entire string is then hashed, which means that the plaintext string is put through a hashing algorithm which scrambles it to make it unreadable as such. If passwords are hashed without salting, if two users have the same password the passwords will end up hashed in the same way. Then, if one user's password is revealed, so is also the other's. Because salts are unique, the resulting hashes are also unique.

To enable salting and hashing, the following lines are added to the views.py file:

The following imports:

```
import os
from werkzeug.security import generate_password_hash, check_password_hash
```

To the adduser method, before creating a new User (with the hashed_password):

```
salted_password = password + str(os.urandom(16))
hashed_password = generate_password_hash(salted_password)
```

To the signin method, to compare the input password with what is found in the database:

```
salted_password = password + user.salt
check_password_hash(user.password, salted_password)
```

If this returns True then the session is established.

In addition, the tasks_user database table must updated to include the salt. The salt can be stored as plaintext as the purpose of the salt is to avoid ending up with the same hashes in the event that two users choose the same password.

## FLAW 5
Source link: [1](https://github.com/sari-bee/CSB_project/blob/5eaa25507a2fc741c875421056d4389d6e9e313e/tasks/views.py#L77)

Flaw 5 is revealing sensitive information as part of an error message (OWASP A09, Security Logging and Monitoring Failures).

In this project, if a user attempts to sign in with the wrong password, an error page is shown. The URL for the error page reveals the password that the user has typed (source link 1). Thus, a password probably closely resembling the right one is revealed as plaintext and e.g. stored in the browser history.

To fix this, the URL for the error page should be made more generic, because the user input is not required to show the error page. In the views.py signin method (source link 1),
```
message = password
```
should be replaced with
```
message = "fail"
```
