Flask App Readme (Created by ChatGPT)

This readme provides instructions on how to start the Flask app and lists the prerequisites required to run the app.
Prerequisites

Before running the Flask app, ensure that you have the following prerequisites:

    Anaconda installed or Pipenv installed
    Python version 3.10 or later

Installation

    Clone the repository to your local machine.
    Open the terminal and navigate to the project directory.
    Create a virtual environment using either Anaconda or Pipenv. If using Anaconda, create the environment by running the following command:


```
conda create --name myenv python=3.10
```
If using Pipenv, create the environment by running the following command:

```
pipenv install
```
Activate the virtual environment using the following command:

```
conda activate myenv
```
If using Pipenv, activate the environment using the following command:
```
pipenv shell
```
Install the required packages using either Anaconda or Pipenv. If using Anaconda, install the packages by running the following command:

```
conda install --file requirements.txt
```

If using Pipenv, install the packages by running the following command:

```
pipenv install -r requirements.txt
```

Starting the Flask App

Once you have installed the required packages, you can start the Flask app by running the following command in the terminal:

On Windows:

```
set FLASK_APP=main.py
flask run
```

On Linux or MacOS:

```
export FLASK_APP=main.py
flask run
```

This will start the Flask app, and you can access it by opening your web browser and navigating to http://localhost:5000.
Conclusion

That's it! You now have the prerequisites installed and can start the Flask app. If you have any questions or issues, please reach out to us for assistance.
