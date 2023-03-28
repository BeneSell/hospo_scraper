Thats the website at the moment:
![grafik](https://user-images.githubusercontent.com/45356497/228362765-1d8e700d-5982-4a80-aa8b-58f9a1d1a17d.png)


Example of an article [https://hochschulsport-koeln.de/](https://hochschulsport-koeln.de/):
![grafik](https://user-images.githubusercontent.com/45356497/228363661-a5151ab4-b62b-4066-8426-c93f46a31ff2.png)



# Flask App Readme (Mostly created by ChatGPT)

## Disclaimer all content is stolen from https://hochschulsport-koeln.de/

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
