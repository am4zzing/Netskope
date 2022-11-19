########################################################
####                                                #### 
####    Script developped by Yuri CARRON, CISSP     ####
####          Email: ycarron@netskope.com           ####
####                                                ####
########################################################
#!/usr/local/bin/python3

import os
import os.path
import wget
import tarfile
import requests
import json
import urllib3
import warnings
import validators
from os import path
from progress.bar import Bar

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

########################################################
####    Customer's tenant / Netskope API endpoints  ####
########################################################

tenant_url = "https://" + "acme.eu.goskope.com"

get_urllist = tenant_url + "/api/v2/policy/urllist?pending=0"
upload_file = tenant_url + "/api/v2/policy/urllist/file"
apply_changes = tenant_url + "/api/v2/policy/urllist/deploy"

########################################################
####                      Paths                     ####
########################################################

path_temp_folder = "/Users/ycarron/Desktop/temp/"
path_archive = "/Users/ycarron/Desktop/blacklists/blacklists/"

########################################################
####              Authentication headers            ####
########################################################

headers = {
      'Netskope-Api-Token': 'add_token_here',
      'Accept': 'application/json',
}

########################################################
####              University of Toulouse            ####
########################################################

Univ_Toulouse_URL = "http://dsi.ut-capitole.fr/blacklists/download/blacklists.tar.gz"
# choose which categories you want to import
categories = ["adult", "dating", "malware"]

########################################################
####                   Functions                    ####
########################################################

# convert the Univ Toulouse file to JSON file
def convert_to_json(path_dir, filename, cat):
  full_cat_name = cat + "_" + filename
  path = path_dir + "/" + filename
  with open(path) as f:
    content_list = f.readlines()
  content_list = [x.strip() for x in content_list]
  y = get_urllist_id(get.json(), full_cat_name)
  if y != 0:
    string = "{\"items\":[{\"id\":" + str(y) + ",\"name\":\"" + full_cat_name + "\",\"data\":{\"urls\":["
  else:
    string = "{\"items\":[{\"name\":\"" + full_cat_name + "\",\"data\":{\"urls\":["

  # progressing bar
  print("Clean up the category")
  bar = Bar("Processing " + full_cat_name , max=len(content_list))
  i = 0
  while i < len(content_list):
    full_url = "http://" + content_list[i]

    # check if the URL is compliance and remove blogspot website from the list  
    if validators.url(full_url) != True or "blogspot" in content_list[i]:
        content_list.remove(content_list[i])
    else:
      content_list[i] = "\"" + content_list[i] + "\""
      i = i + 1
    bar.next()
  s = ','.join(content_list)
  string = string + s
  string2 = "],\"type\":\"exact\"}}]}"
  string2 = string + string2
  file_converted = path_temp_folder + cat + "_" + filename + ".json"
  with open(file_converted, 'w') as nf:
    nf.write(string2)
  print("\nFile ", full_cat_name, " is now converted in JSON format: temporary folder")
  nf.close()
  f.close()
  bar.finish()

# get the url category ID if exists, else return 0
def get_urllist_id(urllists, urllist_name):
  id = 0
  for mdict in urllists:
    for key in mdict:
      if key == "id":
        id = mdict[key]
      if mdict[key] == urllist_name:
        return id
  return 0

# upload url list to Netskope
def send_to_netskope(path, filename):
  print("Sending the URL category:", filename, "to Netskope")
  file = {'urllist': open(path, 'rb')}
  post = requests.post(upload_file, headers=headers, files=file, verify=False)
  if post.status_code == 200 or post.status_code == 201:
    print("The URL category has been sent successfully!")
  else:
    print("The server returned HTTP error: ", post.text)

########################################################
####                       Main                     ####
########################################################

if __name__ == "__main__":
  print("Starting the import of University of Toulouse URL categories")
  print("Downloading the archive from University of Toulouse")
  
  # download the archive
  response = wget.download(Univ_Toulouse_URL, "blacklists.tar.gz")
  
  # open the archive
  file = tarfile.open('blacklists.tar.gz')
  
  # extracting the archive
  file.extractall('./blacklists')
  
  # closing the archive
  file.close()
  
  # delete the archive
  os.remove('blacklists.tar.gz')
  
  # check if the temporary folder exists, else create it
  if path.exists(path_temp_folder) == False:
    print("Temporary folder created!")
    os.mkdir(path_temp_folder)
  
  # get the url categories from Netskope
  print("\nFetch the URL categories from Netskope")
  get = requests.get(get_urllist, headers=headers, verify=False)
  if get.status_code == 200:
    print("URL categories fetched: OK!")
  else:
    print("URL categories fetched: KO -> error: ", post.text)
  
  # get the list of all files and directories
  print("Getting the list of all files and directories")
  for cat in categories:
   path_dir = path_archive + cat
   dir_list = os.listdir(path_dir)
   for filename in dir_list:
     if filename != "very_restrictive_expression" and filename != "usage" and filename != "expressions":
      convert_to_json(path_dir, filename, cat)
  
  # parse the temporary folder and upload the url categories
  print("Parsing the temporary folder")
  new_dir_list = os.listdir(path_temp_folder)
  for filename in new_dir_list:
    path = path_temp_folder + filename
    send_to_netskope(path, filename)
  
  # apply changes to Netskope
  print("Applying the changes to Netskope")
  post = requests.post(apply_changes, headers=headers, verify=False)
  if post.status_code == 200:
    print("The configuration has been applied successfully!")
  else:
    print("Changes: KO -> error: ", post.text)
