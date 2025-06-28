# COMPFEST-SEA

## Step-by-step
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
   ```
4. Run the web by typing the following command ```flask run```. If you have the debugger disabled or trust the users on your network, you can make the server publicly available simply by adding ```--host=0.0.0.0``` to the command line (```flask run --host=0.0.0.0```)
5. Visit that URL in your browser to view the website
6. To quit the website, type CTRL+C to command prompt


## Notifications
- Secret key in the website is distinct when it comes to different devices. The user needs to change the string of the secret key. It should be a long random bytes or str. Copy the output of command ```python -c 'import secrets; print(secrets.token_hex())'``` to your config ```app.config['SECRET_KEY'] = 'output'``` gives the secret key needed.
- On subscription form pages, meal type and delivery days can be chosen more than one. To choose multiple item, press ```Command (⌘)``` + Click item for macOS or ```Ctrl``` + Click item.
