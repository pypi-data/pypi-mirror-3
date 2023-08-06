# Copyright (C) 2012 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

__author__ = 'afshar@google.com (Ali Afshar)'

import os
import pprint
import httplib2
import apiclient.errors
import apiclient.http
from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import flow_from_clientsecrets
from oauth2client.tools import run

API_VERSION = 'v2'


def GetCredentials():
  """Load the credentials, or authorize the user."""
  storage_file = os.path.expanduser('~/.drivecli.creds')
  storage = Storage(storage_file)
  credentials = storage.get()
  if credentials is None or credentials.invalid == True:
    flow = flow_from_clientsecrets(
        os.path.expanduser('~/.drivecli.secrets'),
        scope='https://www.googleapis.com/auth/drive')
    credentials = run(flow, storage)
  return credentials


class Error(object):
  def __init__(self, status=None, error=None):
    self.status = status
    if error:
      self.resp = error.resp
      self.status = int(self.resp.get('status'))
      self.uri = error.uri
      self.content = error.content

  def __eq__(self, err):
    e = (err is Error or
            (isinstance(err, Error) and self.status == err.status))
    return e

  def get(self, value, default=None):
    logging.error(self)
    raise AssertionError('This is not the response you were looking for.')


  def __repr__(self):
    return 'Error<%s> %s' % (self.status, self.content)


TESTING = 'https://www-googleapis-test.sandbox.google.com/'
STAGING = 'https://www-googleapis-staging.sandbox.google.com/'
PROD = 'https://www.googleapis.com/'


def GetDiscoveryUrl():
  return '%s/%s' % (PROD,
                    'discovery/v1/apis/{api}/{apiVersion}/rest')


def BuildClient(http):
  return build('drive', API_VERSION,
            discoveryServiceUrl=GetDiscoveryUrl(), http=http)


def GetAuthorizedHttp(boss):
  creds = GetCredentials()
  http =  httplib2.Http()
  creds.authorize(http)
  wrapped_request = http.request

  def _Wrapper(uri, method="GET", body=None, headers=None, **kw):
    body_to_log = body and len(body) or 0
    boss.Log('Req: %s %s len=%s' %
                 (uri, method, body_to_log))
    boss.Log('Req headers:\n%s' % pprint.pformat(headers))
    if headers and headers.get('content-type') == 'application/json':
      boss.Log('Req body:\n%s' % body)
    resp, content = wrapped_request(uri, method, body, headers, **kw)
    boss.Log('Rsp: %s len=%s %s' % (resp.status, len(content),
                                         resp['content-type']))
    boss.Log('Rsp headers:\n%s' % pprint.pformat(resp))
    if 'application/json' in resp.get('content-type'):
      boss.Log('Rsp body:\n%s' % content)
    return resp, content
  http.request = _Wrapper
  return http


def _GetBodyAndMedia(filename=None, media=None, mimeType=None,
                     resumable=False, title=None, description=None):
  body = {}
  if filename and not media:
    media = apiclient.http.MediaFileUpload(filename, mimetype=mimeType)


  title = title or FLAGS.title
  if title:
    body['title'] = title
  mimeType = mimeType or FLAGS.mimeType
  if mimeType:
    body['mimeType'] = mimeType


def _Insert(d, title=None, filename=None, media=None, mimeType=None,
            resumable=True):
  args = {
    'body': {}
  }
  if title:
    args['body']['title'] = title
  if mimeType:
    args['body']['mimeType'] = mimeType
  if media:
    args['media_body'] = media
  elif filename:
    args['media_body'] = apiclient.http.MediaFileUpload(filename,
                                                        mimetype=mimeType,
                                                        resumable=resumable)
  if 'media_body' in args:
    if resumable:
      args['media_body']._resumable = True
  try:
    return d.files().insert(**args).execute()
  except apiclient.errors.HttpError, e:
    return Error(error=e)


def _Get(d, id, **kw):
  try:
    return d.files().get(fileId=id, **kw).execute()
  except apiclient.errors.HttpError, e:
    return Error(error=e)


def _Download(d, uri):
  resp, content = d._http.request(uri)
  return resp, content


def _DownloadFile(d, uri, filename=None):
  resp, content = _Download(d, uri)
  print resp
  return resp, content


def _List(d, **kw):
  try:
    return d.files().list(**kw).execute()
  except apiclient.errors.HttpError, e:
    return Error(error=e)


def _AddPermission(d, fileId, role, type, value):
  p = {
    'role': role,
    'type': type,
    'value': value,
  }
  try:
    return d.permissions().insert(fileId=fileId, body=p).execute()
  except apiclient.errors.HttpError, e:
    return Error(error=e)


def _Permissions(d, fileId):
  try:
    return d.permissions().list(fileId=fileId).execute()
  except apiclient.errors.HttpError, e:
    return Error(error=e)


def _Changes(d, **kw):
  try:
    return d.changes().list(**kw).execute()
  except apiclient.errors.HttpError, e:
    return Error(error=e)


def _About(d):
  try:
    return d.about().get().execute()
  except apiclient.errors.HttpError, e:
    return Error(error=e)
