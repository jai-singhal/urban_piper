# Urban Piper Product Developer-Python Hiring Challenge

## Technologies used
- Python==3.6.8
- Django==2.2.1
- Pika==1.0.1
- Rabbitmq
- Django Channels
- Postgresql
- DigitalOcean(For Deployement)
- jquery/javascript


## How to run the project locally

For running the project locally, we are going to use rabbitmq locally, and also
database as dbsqlite3 

1. Install the python(3.6.8), rabbitmq, and redis

    #### Rabbitmq: 

    `
        $ sudo apt-get install -y erlang
    `

    `
        $ sudo apt-get install rabbitmq-server
    `

    `
        $ sudo systemctl enable rabbitmq-server
    `

    `
        $ sudo systemctl start rabbitmq-server
    `
2. Clone the repository from https://gitlab.com/jai-singhal/urban_piper

3. Unzip it, and cd to it

4. create virtualenv by
 
    `
        $ virtualenv -p python3 venv
    `

    And then activate it by

    `
        $ source venv/bin/activate
    `

5. Install the dependencies by

    `
        $ pip3 install -r requirements.txt 
    `

6. Migrate the database. Run

    `
        $ python3 manage.py migrate
    `

7. Load the users data from dumped data

    `
        $ python3 manage.py loaddata dbdata.json
    `

8. Run the server

    `
        $ python3 manage.py runserver
    `

9. Navigate to http://127.0.0.1:8000 and then login either by Storage Manager, or
Delivery Person. Login Credentials are mentioned in the login page.

10. Open the application in several Browser windows. Use Incognito mode for login by 
different users.

Note: For more queries. Feel free to ask at **jaisinghal48[at]gmail[dot]com**