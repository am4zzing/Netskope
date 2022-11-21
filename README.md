# Netskope
Importing University of Toulouse URL lists to Netskope by Yuri CARRON, CISSP, ycarron@netskope.com

Be informed that the first start could take at least one day.
It comes from the URLs verification for all the categories (5k+ URLs are going to be verified).
Then, only the differences will be push to Netskope.

HOW DOES IT WORK?

0. Prerequisites

For Windows OS
- download and install python for Windows
https://www.python.org/downloads/windows/

Add the mandatory functions
- py -m pip install wget
- py -m pip install requests
- py -m pip install validators
- py -m pip install progress

1. Activate the Netskope API v2

From your Netskope tenant, go to Settings > Tools > REST API v2
- click on the "Pen" icon
- enable the REST API feature

2. Add a new token

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

- replace the 'add_the_token_here' by your new token under the "Authentication headers" section
'Netskope-Api-Token': 'add_token_here'
- edit the tenant_url variable under the "Customer's tenant / Netskope API endpoints" section by your own tenant

5. Add the University of Toulouse URL categories

- edit the "categories" tuple under the University of Toulouse section
Example: categories = ["adult", "dating", "malware", "sect", "gambling", "drogue"]

For the whole list of categories, follow this link: http://dsi.ut-capitole.fr/blacklists/
By design, the "Adult" category is the only maintain category by the owner's.

6. Launch the script
  - MacOS: python3 import_categories.py
  - Windows OS: py import_categories.py

7. Add the new lists to a custom category

Once the script ending successfuly, you will have to create a custom category on your Netskope tenant.
Otherwise, those categories won't never be enforced.

From your Netskope tenant, go to Policies > Web > CUSTOM CATEGORIES
- click on the "NEW CUSTOM Categories" button
- give it a name
- add to the "URL List" (Include)" whole the categories needed
- save it
- click on "APPLY CHANGES"

8. Add the new Custom Categories to a Real-time Protection rule(s)

From your Netskope tenant, go to Policies > Real-time Protection

- add or edit a rule
- under category add the new Custom Category
- save it
- click on "APPLY CHANGES"

Have a safe journey with Netskope!
