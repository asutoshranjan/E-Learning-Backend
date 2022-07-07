from flask import Flask, request, jsonify;
from flask_cors import CORS, cross_origin;

import httplib2
import os
import random
import sys
import time

from apiclient.discovery import build
from apiclient.errors import HttpError
from apiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow


output = "Succesfully Uploaded"
vidloc = ""
# Explicitly tell the underlying HTTP transport library not to retry, since
# we are handling retry logic ourselves.
httplib2.RETRIES = 1

# Maximum number of times to retry before giving up.
MAX_RETRIES = 10

# Always retry when these exceptions are raised.
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError)

# Always retry when an apiclient.errors.HttpError with one of these status
# codes is raised.
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

CLIENT_SECRETS_FILE = "client_secrets.json"
scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

# This OAuth 2.0 access scope allows an application to upload files to the
# authenticated user's YouTube channel, but doesn't allow other types of access.
YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# This variable defines a message to display if the CLIENT_SECRETS_FILE is
# missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

   %s

with information from the API Console
https://console.developers.google.com/

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__),
                                   CLIENT_SECRETS_FILE))

VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")



def get_authenticated_service(dic):
  flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
    scope=YOUTUBE_UPLOAD_SCOPE,
    message=MISSING_CLIENT_SECRETS_MESSAGE)

  storage = Storage("%s-oauth2.json" % sys.argv[0])
  credentials = storage.get()

  if credentials is None or credentials.invalid:
    credentials = run_flow(flow, storage, dic)

  return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
    http=credentials.authorize(httplib2.Http()))

def initialize_upload(youtube, dic):
  tags = None
  if dic["keywords"]:
    tags = dic["keywords"].split(",")

  body=dict(
    snippet=dict(
      title=dic["title"],
      description=dic["description"],
      tags=tags,
      categoryId=dic["category"]
    ),
    status=dict(
      privacyStatus=dic["privacyStatus"]
    )
  )
  # Call the API's videos.insert method to create and upload the video.
  insert_request = youtube.videos().insert(
    part=",".join(body.keys()),
    body=body,
    # The chunksize parameter specifies the size of each chunk of data, in
    # bytes, that will be uploaded at a time. Set a higher value for
    # reliable connections as fewer chunks lead to faster uploads. Set a lower
    # value for better recovery on less reliable connections.
    #
    # Setting "chunksize" equal to -1 in the code below means that the entire
    # file will be uploaded in a single HTTP request. (If the upload fails,
    # it will still be retried where it left off.) This is usually a best
    # practice, but if you're using Python older than 2.6 or if you're
    # running on App Engine, you should set the chunksize to something like
    # 1024 * 1024 (1 megabyte).
    media_body=MediaFileUpload(dic["file"], chunksize=-1, resumable=True)
  )

  resumable_upload(insert_request)


# This method implements an exponential backoff strategy to resume a
# failed upload.
def resumable_upload(insert_request):
  response = None
  error = None
  retry = 0
  while response is None:
    try:
      print("Uploading file...")
      status, response = insert_request.next_chunk()
      if response is not None:
        if 'id' in response:
          print("Video id '%s' was successfully uploaded." % response['id'])
          output = response['id']
          print(output)
        else:
          exit("The upload failed with an unexpected response: %s" % response)
    except HttpError as e:
      if e.resp.status in RETRIABLE_STATUS_CODES:
        error = "A retriable HTTP error %d occurred:\n%s" % (e.resp.status,
                                                             e.content)
      else:
        raise
    except RETRIABLE_EXCEPTIONS as e:
      error = "A retriable error occurred: %s" % e

    if error is not None:
      print(error)
      retry += 1
      if retry > MAX_RETRIES:
        exit("No longer attempting to retry.")

      max_sleep = 2 ** retry
      sleep_seconds = random.random() * max_sleep
      print("Sleeping %f seconds and then retrying..." % sleep_seconds)
      time.sleep(sleep_seconds)






app = Flask(__name__)
cors = CORS(app)

@app.route('/api', methods = ['GET'])
@cross_origin()

def uploadvideoyt():
    #dic = dictionary 
    dic = {}
    filelocation = request.args['query']
    strfilelocation = str(filelocation)

    vidloc = "C:\\Users\\asuto\Desktop\\"+strfilelocation

    file = vidloc
    title = "Hello World Video 1 Day 2"
    description = """This is the new video 3 multiline descrption guys.
    I belive here I can add chapters as well.
    Here are my youtube chapters
    Like Comment and Suscribe Guys!
    ---**--**--**--
    00:00 - Intro
    00:20 - Outro
    It is the most popular site for Python programmers."""
    category = "22"
    keywords = "youtube api, hello world, like, comment, day2Video"
    privacyStatus = VALID_PRIVACY_STATUSES[0]

    dicyt = {"file":file, "title":title, "description":description, "category":category, "keywords":keywords, "privacyStatus":privacyStatus}
    
    if not os.path.exists(dicyt["file"]):
        exit("Please specify a valid file using the --file= parameter.")

    youtube = get_authenticated_service(dicyt)
    try:
        initialize_upload(youtube, dicyt)
    except HttpError as e:
        print("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))
    

    dic["loction"] = vidloc
    dic["output"] = output
    return dic

if __name__ == "__main__":
    app.run()