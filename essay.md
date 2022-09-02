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
Source links: [1](https://github.com/sari-bee/CSB_project/blob/c6fa537cdb300c439afdd6cde1d7d749920fca95/tasks/templates/tasks/tasks.html#L30) [2](https://github.com/sari-bee/CSB_project/blob/c6fa537cdb300c439afdd6cde1d7d749920fca95/tasks/views.py#L40)

Flaw 1 is cross-site request forgery (CSRF). CSRF tokens are added to forms submitted on websites to ensure that the submission is originating from the site itself. The form's CSRF token is checked and matched with the session token. If the CSRF token is not checked, a malicious intruder can lead a user into a false site through which the intruder can post information with the user's credentials.

In this project, a CSRF vulnerability has been introduced by disabling Django's built-in CSRF token check on the method addtask in views.py (source link 2) and omitting the CSRF token from the form adding a task on tasks.html (source link 1).

This can be fixed by removing the @csrf_exempt decorator from method addtask on views.py (source link 2) and by adding the line {% csrf_token %} as the first line in the addtask form on tasks.html (source link 1).

## FLAW 2
Source link: [1](https://github.com/sari-bee/CSB_project/blob/c6fa537cdb300c439afdd6cde1d7d749920fca95/tasks/views.py#L73)

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
Source link: [1](https://github.com/sari-bee/CSB_project/blob/9e4ffaf84fd199385aa9dfd722bb011f47980fda/tasks/views.py#L23)

Flaw 3 is allowing users to gain access to private data through URL manipulation (OWASP A01, Broken Access Control). If a user's credentials are not checked when loading a page, and if the URLs of pages containing private data are constructed in such a way that other users or intruders can decipher the logic behind URL construction, the site runs the risk of revealing sensitive information to outsiders.

In this project, the task listing for each user is under tasks/users/<username> and thus easily found if the usernames of other users are known. Further, there is no check to see if the user that is signed in is the one attempting to access the page (method tasks in views.py, source link 1). Thus, anyone who knows other users' usernames can access their task lists.

This flaw can be fixed by adding to the beginning of the tasks method (source link 1) a check to verify the username whose task list is attempted to access against that of the logged in user (session username), as follows:

```
if username != request.session['username']:
    return HttpResponseRedirect(reverse('error'))
````

Thus, if the username carried in the session of the user currently logged in does not match the username carried in the URL, the user is redirected to an error page.

## FLAW 4
Source link: [1]()

exact source link pinpointing flaw 1...
description of flaw 1...
how to fix it...

4. Identification and Authentication failures, which includes both insufficient complexity requirements for passwords and storing usernames and passwords in an insecure way in the database. In addition, this includes exposing session identifiers e.g. in the URL.

In this project, there are no requirements for password length or complexity, thus enabling weak and default passwords. The usernames and passwords are stored as plaintext in the database, which means that if the database is broken into, all user credentials are freely available to the intruder. Further, the username is used as the session identifier, and shown in the URL for the task list.

One of the fixes would be to salt and hash all created passwords before storing them in the database. Salting refers to adding random characters to the password. The entire string is then hashed, which means that the plaintext string is put through a hashing algorithm which scrambles it to make it unreadable as such. Only hashing is insufficient because without the salt, if two users have the same password, the passwords will end up hashed in the same way and thus revealing one user's password will also reveal the other's. Because salts are unique, the resulting hashes are also unique.

On way to add salting and hashing is that the following imports are added to the views.py file:

import os
from werkzeug.security import generate_password_hash, check_password_hash

Thereafter, the following should be added to the adduser method before creating a new User with the hashed password:

(password = request.POST['password'])
salted_password = password + str(os.urandom(16))
hashed_password = generate_password_hash(salted_password)

In addition, the salt needs to be added to the tasks_user database table, so that it can be fetched and used when check the sign-in for accuracy. The salt can be stored as plaintext as the purpose of the salt is to avoid hashing the same strings in the event that two users choose the same password.

In addition, the following is added to the signin method to compare the input password + salt with what is found (hashed) in the database:

(The password is collected and user is fetched from the database with the username as in the method)
salted_password = password + user.salt
check_password_hash(user.password, salted_password)

If this returns True then the session is established as in the method.

## FLAW 5
exact source link pinpointing flaw 1...
description of flaw 1...
how to fix it...

5. Security Logging and Monitoring Failures occur when errors are monitored or logged in a way that reveals sensitive information to a malicious attacker.

In this app, when a user attempts to sign in, but types in the wrong password, an error page is shown. The URL for the error page reveals the password that the user has typed. Thus, a password possibly very closely resembling the right one is revealed as plaintext in the URL.

This could be solved by leaving the argument out of the URL or by changing it into something generic such as "fail", in the views.py method signin:

Replace
message = password
with
message = "fail"

...

 word count? 1000 word report (hard limits: 800-1500)

 Add source link to each flaw if appropriate. Ideally, the link should have the format https://urldomain/repo/ file.py#L42 (Line 42 in file.py). The links can be easily obtained by clicking the line numbers in the Github  repository file browser. If the flaw involves in omitting some code, then comment-out the code, and provide
 the link to the beginning of the commented block.

 Be specific with your fix. If possible, provide a fix to the problem in the code. The fix can be commented
 out. If appropriate, add a source link to each fix as well.