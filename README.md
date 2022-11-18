# Netskope
Importing University of Toulouse URL lists to Netskope tenant.

HOW TO?

1. Activate the Netskope API v2

From your Netskope tenant, go to Settings > Tools > REST API v2
- click on the "Pen" icon
- enable the REST API feature

2. Add new token

- click on "NEW TOKEN" button
- give it a name and an expiration timeline
- add the following endpoints with "Read + Write" privileges:
  - /api/v2/policy/urllist/file
  - /api/v2/policy/urllist
  - /api/v2/policy/urllist/deploy

3. Get the token

Save the configuration in order to get the token
- click on "COPY TOKEN" button

4. Edit the script

- paste the token under the "Authentication headers" section
'Netskope-Api-Token': 'add_the_token_here'

- edit the tenant_url variable under the "Customer's tenant / Netskope API endpoints" section by your own tenant
- edit the two paths under the "Paths" section. Be careful of your OS path.
  - "path_temp_folder" is the path for the temporary folder where the lists are conververted to JSON format
  - "path_archive" is the path for the University of Toulouse files

5. Add the University of Toulouse URL categories

- edit the "categories" tuple under the University of Toulouse section
Example: categories = ["adult", "dating", "malware", "sect", "gambling", "drogue"]

For the whole list of categories, follow this link: http://dsi.ut-capitole.fr/blacklists/

6. Launch the script
  - python3 import_categories.py

Be careful, it's a python v3 script. Upgrade your python interpreter to this version.
The script needs special commands such as "wget, json or requests". You have to install them.

7. Add the new lists to a custom category

Once the script ending successfuly, you will have to create a custom category on your Netskope tenant.
Otherwise, those categories won't never be enforced.

From your Netskope tenant, go to Policies > Web > CUSTOM CATEGORIES
- click on the "NEW CUSTOM Categories" button
- give it a name
- add to the "URL List" (Include)" whole the catergories needed
- save it and click on "APPLY CHANGES"

8. Add the new Custom Categories to a Real-time Protection rule(s)


Have a safe journey with Netskope!
