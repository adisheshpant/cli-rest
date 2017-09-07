#!/usr/bin/env python
import argcomplete, json, requests
import argparse as ap
from os import walk
from pygments import styles
from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import Terminal256Formatter

def getFiles(path):
  f = []
  for (dirpath, dirnames, fileNames) in walk(path):
     f += fileNames
  return ( [x.split(".")[0] for x in f if x.endswith(".json")] )

def getReq(prefix, parsed_args, **kwargs): 
  return getFiles("requests")

def getEnv(prefix, parsed_args, **kwargs): 
  return getFiles("env")

def buildUrl(envJs, reqJs, params):
  url = reqJs['url']

  for k,v in envJs.iteritems():
    kp = '{'+k+'}'
    if kp in url:
      url = url.replace(kp, v)

  if params:
    for param in params:
      p = param.split("=")
      kp = '{'+p[0]+'}'
      if kp in url:
        url = url.replace(kp, p[1])

  return url

def buildHeaders(envJs, hparams):
  headers = {}

  if 'headers' in envJs:
    headers = envJs['headers']

  if hparams:
    for h in hparams:
      v = h.split("=")
      headers[v[0]] = v[1]

  return headers
    
def main(**args):
  req = args['req']
  env = args['env']
  envJs = json.load(open("env/"+env+".json"))
  reqJs = json.load(open("requests/"+req+".json"))

  url = buildUrl(envJs, reqJs, args['params'])
  headers = buildHeaders(envJs, args['headers'])
  method = reqJs['method']
  body = reqJs['body'] if 'body' in reqJs else None

  if '{' in url:
    print "Missing params",url
    return

  print "Request:"
  print method, url
  for k,v in headers.iteritems():
    print k,':',v
  if body:
    print body

  print "\nResponse:"
  r = requests.request(method, url, json=body, headers=headers)
  print r.text
  print "Status:",r.status_code
  
if __name__ == '__main__':
  parser = ap.ArgumentParser()
  parser.add_argument('-e', '--env').completer = getEnv
  parser.add_argument('-r', '--req').completer = getReq
  parser.add_argument('-p', '--params', nargs='+', type=str)
  parser.add_argument('-hp', '--headers', nargs='+', type=str)
  argcomplete.autocomplete(parser)
  args = parser.parse_args()
  main(**vars(args))
