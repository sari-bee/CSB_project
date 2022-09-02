## Intentionally Insecure Tasks App

LINK: https://github.com/sari-bee/CSB_project

The app is written with Python & Django.
Apply migrations with 
``
python3 manage.py migrate
``
Start the server with python3 manage.py runserver
Find the app on localhost:8000/tasks

The app is a very simple Tasks list. The user can register, sign in, and then view and manipulate their Tasks list.

I have used OWASP 2021 list for the flaws.

FLAW 1:
Source links: 

exact source link pinpointing flaw 1...
description of flaw 1...
how to fix it...

1. Cross-site request forgery (CSRF). This type of attack exploits a vulnerability in checking for session credentials when submitting a form. If a CSRF token is not checked when submitting a form, a malicious intruder can utilize a signed in user's credentials by leading them to a false site through which the intruder can post forms et cetera under the user's credentials.
-
In this project, the form adding a task has no CSRF token check (it has been disabled), thus enabling a CSRF attack.

In Django, in order to force CSRF token checking when submitting a form, the line {% csrf_token %} should be added to the addtask form on page tasks.html, much in the same way that it is included in e.g. the donetask form on the same page. In addition the @csrf_exempt decorator must be removed from addtask method in views.py. Django will then automatically require a CSRF token when submitting a form.

FLAW 2:
exact source link pinpointing flaw 1...
description of flaw 1...
how to fix it...

2. SQL injection as an example of Injection. When user input is used as such as part of an SQL command, the malicious user can input data that will perform as unintended; for example, they may input data that will drop all database tables. To prevent this, user inputs must be sanitized before using them as a part of an SQL command.

In this project, when signing in, the user is fetched from the tasks_user database table with a raw SQL query, in which the user input from the sign in form is used as such without validation or sanitation. This makes the query vulnerable to injection. Namely, the user is fetched as such:

query = 'SELECT * FROM tasks_user WHERE username = "%s"' % request.POST['username']
user = User.objects.raw(query)[0]

Extra SQL commands could be added to the end of the query and access to the database gained in this way.
The query should instead be applied using Django's ORM, which provides automatic protection from SQL injection, as follows:

username = request.POST['username']
user = User.objects.get(username=username)

Alternatively the raw SQL query could be done in a safe way by using a params argument:

username = request.POST['username']
user = User.objects.raw('SELECT * FROM tasks_user WHERE username = %s', [username])[0]

FLAW 3:
exact source link pinpointing flaw 1...
description of flaw 1...
how to fix it...

3. Broken Access Control by way of allowing URLs to be manipulated in such a way as to gain access to private data.

In this project, the task listing for each user is under tasks/users/'username'. There is no check to see that the signed in user is the one accessing the page, so anyone who knows other users' usernames can access and even manipulate their task lists.

This could be fixed by adding the following to the beginning of the tasks method:

if username != request.session['username']:
    return HttpResponseRedirect(reverse('error'))

Thus, if the username carried in the session of the user currently logged in does not match the username carried in the URL, the user is redirected to an error page.

FLAW 4:
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

FLAW 5:
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