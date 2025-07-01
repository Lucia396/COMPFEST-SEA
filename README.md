# COMPFEST-SEA

## Setting Up Environment
1. Open 'compfest sea' folder to access file, then open 'app.py' file.
2. Use a virtual environment to access the website, by following these command on your terminal
    - Create an environment by creating a ```.venv``` folder within
      * On macOS/Linux
      ```
      $ cd /path/to/folder
      $ python3 -m venv .venv
      ```
      * On Windows
      ```
      > cd /path/to/folder
      > py -3 -m venv .venv
      ```
    - Activate the environment
      * On macOS/Linux
      ```
      $ . .venv/bin/activate
      ```
      * On Windows
      ```
      > .venv\Scripts\activate
      ```
3. Within the activated environment, use the following command to install all of Flask packages needed
   ```
   pip install Flask
   pip install Flask-SQLAlchemy
   pip install Flask-Bcrypt
   pip install Flask-WTF
   ```
4. Run the web by typing the following command ```flask run```. If you have the debugger disabled or trust the users on your network, you can make the server publicly available simply by adding ```--host=0.0.0.0``` to the command line (```flask run --host=0.0.0.0```)
5. Visit that URL in your browser to view the website
6. To quit the website, type CTRL+C to command prompt

## Notifications for Environment
- Secret key in the website is distinct when it comes to different devices. The user needs to change the string of the secret key. It should be a long random bytes or str. Copy the output of command ```python -c 'import secrets; print(secrets.token_hex())'``` to your config ```app.config['SECRET_KEY'] = 'output'``` gives the secret key needed.
- The database for each data has been created with the database model in Flask and can be accessed in instance folder.
- On subscription form pages, meal type and delivery days can be chosen more than one. To choose multiple item, press ```Command (⌘)``` + Click item for macOS or ```Ctrl``` + Click item.
- To see each feature of the website, hover to the image of each feature.
- To add another Meal Plan Menu, go to the ```if __name__ == '__main__':``` function and create a new variable, along with attributes of the database.

## Setting Up Admin Account
1. There are 2 admin accounts have been made on ```if __name__ == '__main__':``` function. The first account using email ```lucia@gmail.com``` and password ```asdfghjkl```. The second account using email ```giovani@gmail.com``` and password ```zxcvbnm```. User can directly login to admin account with these users.
2. To create another admin account, go to that function and create a new variable, along with admin email, name, and password, using format ```User(Email='email@gmail.com', Name='name', Password=bcrypt.generate_password_hash('password').decode('utf-8'), Role='admin')```. Then, add that new variable to ```db.session.add_all([admin1, admin2])```. For instance :
    ```
    new_admin = User(Email='admin@gmail.com', Name='admin', Password=bcrypt.generate_password_hash('admin123').decode('utf-8'), Role='admin')
    # then add new_admin to db.session.add_all([admin1, admin2])
    if not User.query.first():
        db.session.add_all([admin1, admin2, new_admin])
        db.session.commit()
    db.session.close()
    ```
