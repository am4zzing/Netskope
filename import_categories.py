########################################################
####                                                #### 
####    Script developped by Yuri CARRON, CISSP     ####
####          Email: ycarron@netskope.com           ####
####                                                ####
########################################################
#!/usr/local/bin/python3

import os
import os.path
import time
import wget
import tarfile
import requests
import json
import urllib3
import warnings
import validators
import shutil
from os import path
from difflib import Differ
from progress.bar import Bar

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

########################################################
####    Customer's tenant / Netskope API endpoints  ####
########################################################

tenant_url = "https://acme.eu.goskope.com"

api_get_urllist = tenant_url + "/api/v2/policy/urllist?pending=0"
api_upload_file = tenant_url + "/api/v2/policy/urllist/file"
api_apply_changes = tenant_url + "/api/v2/policy/urllist/deploy"

########################################################
####                      Paths                     ####
########################################################

# check the operating system
if os.name == "posix":
  path_temp_folder = "/Users/ycarron/Desktop/temp/"
  path_archive = "/Users/ycarron/Desktop/blacklists/blacklists/"
  path_archive_2 = "/Users/ycarron/Desktop/blacklists_2/blacklists/"
  slash = "/"
if os.name == "nt":
  path_temp_folder = "C:\\Users\\son.goku\\Desktop\\temp\\"
  path_archive = "C:\\Users\son.goku\\Desktop\\blacklists\\blacklists\\"
  path_archive_2 = "C:\\Users\son.goku\\Desktop\\blacklists_2\\blacklists\\"
  slash = "\\"

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
categories = ["adult", "agressif", "cryptojacking", "ddos", "drogue", "hacking", "malware", "phishing", "sect", "stalkerware", "tricheur", "warez"]

list_cat_changed = []

########################################################
####                   Functions                    ####
########################################################

# get the list of all files and directories
def get_all_files():
  print("Getting the list of all files and directories")
  for cat in categories:
    path_dir = path_archive + cat
    dir_list = os.listdir(path_dir)
    for filename in dir_list:
      if filename != "very_restrictive_expression" and filename != "usage" and filename != "expressions":
        # if the folder exists, get the difference between the new and old list
        if path.exists(path_archive_2 + cat + slash + filename) == True:
          diff = [] 
          with open(path_dir + slash + filename) as file_1, open(path_archive_2 + cat + slash + filename) as file_2:
            differ = Differ()
            for line in differ.compare(file_1.readlines(), file_2.readlines()):
              if line[0] == '-':
                string = line.strip()
                string = string.replace('- ', '')
                diff.append(string)
            if diff:
              # concat the new list to the old JSON file
              json_filename = cat + "_" + filename + ".json"
              print("New URLs found in the category: ", cat)
              print("Adding them to the file: ", json_filename)
              contact_diff_to_json(diff, json_filename)
              list_cat_changed.append(filename)
              file_1.close()
              file_2.close()
              return
            return
        # convert the file to JSON format
        convert_file_to_json(path_dir, filename, cat)

# concat the new list to the old JSON file
def contact_diff_to_json(diff, json_filename):
  text_file = open(path_temp_folder + json_filename, "r")
  i = 0
  while i < len(mylist):
    full_url = "http://" + mylist[i]

    # check if the URL is compliance and remove blogspot website from the list  
    if validators.url(full_url) != True or "blogspot" in mylist[i]:
      mylist.remove(mylist[i])
    else:
      mylist[i] = mylist[i]
      i = i + 1
    if mylist:
      data = text_file.read()
      index = data.find("\"urls\":[") + 8
      output_line = data[:index] + "\"" + '\",\"'.join(mylist) + "\"," + data[index:]
  text_file.close()

# get the url categories from Netskope API
def get_categories_from_netskope():
  print("\nFetch the URL categories from Netskope")
  # bypass the Netskope API global rate limit
  time.sleep(0.5)
  get = requests.get(api_get_urllist, headers=headers, verify=False)
  if get.status_code == 200:
    print("URL categories fetched: OK!")
  else:
    print("URL categories fetched: KO -> error: ", get.text)
  return get

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

# create the JSON file to the temporary folder
def create_file(filename, cat, clist):
  full_cat_name = cat + "_" + filename
  get = get_categories_from_netskope()

  # get the url category ID if exists, else return 0
  cid = get_urllist_id(get.json(), full_cat_name)
  if cid != 0:
    string = "{\"items\":[{\"id\":" + str(cid) + ",\"name\":\"" + full_cat_name + "\",\"data\":{\"urls\":["
  else:
    string = "{\"items\":[{\"name\":\"" + full_cat_name + "\",\"data\":{\"urls\":["
  s = ','.join(clist)
  string = string + s + "],\"type\":\"exact\"}}]}"
  file_converted = path_temp_folder + cat + "_" + filename + ".json"
  with open(file_converted, 'w') as nf:
    nf.write(string)
  print("File ", full_cat_name, " is now converted in JSON format: temporary folder")
  nf.close()

# convert the Univ Toulouse file to JSON file
def convert_file_to_json(path_dir, filename, cat):
  full_cat_name = cat + "_" + filename
  path = path_dir + slash + filename
  with open(path) as f:
    content_list = f.readlines()
  content_list = [x.strip() for x in content_list]

  print("Cleaning up the category")
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

  # split large file
  length = len(content_list)
  if length >= 600000:
    middle_index = length // 2
    first_half = content_list[:middle_index]
    second_half = content_list[middle_index:]
    full_cat_name = full_cat_name + "_1"
    create_file(filename, cat, first_half)
    full_cat_name = full_cat_name + "_2"
    create_file(filename, cat, second_half)
  else:
    create_file(filename, cat, content_list)
  f.close()
  bar.finish()

# upload url list to Netskope API
def send_to_netskope(path, filename):
  print("Sending the URL category:", filename, "to Netskope")
  file_urllist = {'urllist': open(path, 'rb')}
  # bypass the Netskope API global rate limit
  time.sleep(0.5)
  post = requests.post(api_upload_file, headers=headers, files=file_urllist, verify=False)
  if post.status_code == 200 or post.status_code == 201:
    print("The URL category has been sent successfully!")
  else:
    print("The server returned HTTP error: ", post.text)

# apply changes to Netskope API
def apply_changes_to_netskope():
  print("Applying the changes to Netskope")
  post = requests.post(api_apply_changes, headers=headers, verify=False)
  if post.status_code == 200:
    print("The configuration has been applied successfully!")
  else:
    print("Changes: KO -> error: ", post.text)

########################################################
####                       Main                     ####
########################################################

if __name__ == "__main__":
  print("Starting the import of University of Toulouse URL categories")

  # download the archive
  print("Downloading the archive from University of Toulouse")
  response = wget.download(Univ_Toulouse_URL, "blacklists.tar.gz")
  
  # open the archive
  file = tarfile.open('blacklists.tar.gz')
  
  # extracting the archive
  print ("\nExtracting the archive 'blacklists.tar.gz'")
  file.extractall('blacklists')
  file.close()
  
  # delete the archive
  print ("Removing the archive 'blacklists.tar.gz'")
  os.remove('blacklists.tar.gz')

  # check if the temporary folder exists, else create it
  if path.exists(path_temp_folder) == False:
    print("Temporary folder has been created!")
    os.mkdir(path_temp_folder)
  
  # get the list of all files and directories, and convert files to JSON format
  get_all_files()
  
  # parse the temporary folder and upload the url categories
  print("Parsing the temporary folder")
  new_dir_list = os.listdir(path_temp_folder)
  for filename in new_dir_list:
    full_path = path_temp_folder + filename
    if path.exists('blacklists_2') == False:
      send_to_netskope(full_path, filename)
    else:
      if filename in list_cat_changed:
        # upload url list to Netskope API
        send_to_netskope(full_path, filename)
      else:
        print("There is no change in the file: ", filename)

  # delete the archive if the folder exists
  if path.exists('blacklists_2') == True:
    print ("Deleting the old folder 'blacklists_2'")
    shutil.rmtree('blacklists_2')

  # rename the archive
  print ("Renaming the folder 'blacklists' to 'blacklists_2'")
  os.rename("blacklists","blacklists_2")

  # apply changes to Netskope API
  apply_changes_to_netskope()