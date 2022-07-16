# Swift Load API

This is the backend python flask app for Swift Load. It provides **REST APIs** to our frontend application and performs the **POST** and **GET** requests. It receives data from the user to upload the required video\videos using all the various details the user provides with like Video Title, Description, Category, Keywords, ThumbnaiFile, PrivacyStatus (uses **Youtube Data V3 API** to upload the video). It uploads the videos to a specified Youtube channel you authenticate with while logging in. 

## Getting Started

Clone this repo at your desired location. <br />
- create a python virtualenv in the same directory <br />
- now activate the virtualenv and add these packages <br />
```
pip install --upgrade google-api-python-client
pip install --upgrade google-auth-oauthlib google-auth-httplib2
pip install flask
pip install flask-cors
```
- add the client_secrets.json file in the same directory and then install
```
pip install oauth2client
```
- to run the script 
```
python api.py
```
The flask application is now hosted on your localhost <br />
<br />
**Congratulations!** 

