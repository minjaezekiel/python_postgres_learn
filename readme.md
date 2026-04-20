## GUIDE
This is a comprehensive guide to help a beginner in python to be able to use python object oriented programming concepts to interract with the postgresql db.

Step 1:
Clone the repository:
https://github.com/minjaezekiel/python_postgres_learn.git

Step 2:
Download and install requirements.txt file.
pip install -r requirements.txt

Note: Make sure the postgresql db is installed in your PC

Step 3: 
Read through the comments i set for you to gain understanding of how it all works, be free to change the code  in any place or implement your own codes into it for further learning.

##Key Concepts Explained for Beginners

1. The Class Structure (class PostgreSQLManager)
We wrap all our database logic inside a class. This is "Object-Oriented." It keeps our data (credentials) and our actions (methods like insert, update) neatly bundled together. This allows us to reuse this code easily in other projects.

2. The Connection and Cursor
Connection (self.connection): Imagine this as the telephone line between Python and the Database. You must "dial" (connect) before you can talk.
Cursor (self.cursor): If the connection is the phone call, the cursor is the specific sentence you are speaking. Databases use cursors to keep track of where you are in a set of results.

3. Parameterized Queries (%s)
You will notice I never write code like this:
cursor.execute(f"INSERT INTO users VALUES ('{user_name}')")

Instead, I write:
cursor.execute("INSERT INTO users VALUES (%s)", (user_name,))

Why? This is critical for security. If a user enters a name like Robert'; DROP TABLE users; --, the first version would delete your whole database (an SQL Injection attack). The second version (with %s) treats that input strictly as text, preventing the attack.

4. Commit vs. Rollback
PostgreSQL databases work in "transactions." This means you can make 10 changes, but until you say commit(), none of them are permanent.

Commit: "Yes, I am sure, save these changes to the hard drive."
Rollback: "Something went wrong, forget everything I just did and go back to how things were."

5. Private Methods (Starting with _)
I created methods like _execute_query and _fetch_data. These start with an underscore. In Python, this is a polite way of telling other programmers: "Don't use these methods directly outside the class. They are just helpers to keep the main code clean." The public methods (insert_employee, get_all_employees) call these helpers in the background.

This work/ lesson is totally free...
### Have Fun!
