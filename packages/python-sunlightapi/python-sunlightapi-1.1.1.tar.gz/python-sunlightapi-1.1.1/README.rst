==================
python-sunlightapi
==================

.. warning::
    This library is deprecated in favor of the more comprehensive `python-sunlight <http://python-sunlight.readthedocs.org>`_.


Python library for interacting with the Sunlight Labs API.

The Sunlight Labs API provides legislator information and district lookups.

(http://services.sunlightlabs.com/api/)

python-sunlightapi is a project of Sunlight Labs (c) 2010.
Written by James Turk <jturk@sunlightfoundation.com>.

All code is under a BSD-style license, see LICENSE for details.

Homepage: http://pypi.python.org/pypi/python-sunlightapi/

Source: http://github.com/sunlightlabs/python-sunlightapi/

The package can be installed via pip, easy_install or by downloading the
source and running ``python setup.py install``.

Requirements
============

python >= 2.4

simplejson >= 1.8 (not required with python 2.6, will use built in json module)

Usage
=====

To initialize the api, all that is required is for it to be imported and for an
API key to be defined.

(If you do not have an API key visit http://services.sunlightlabs.com/api/ to
register for one.)

Import ``sunlight`` from ``sunlightapi``:
    
    >>> from sunlightapi import sunlight, SunlightApiError
    
And set your API key:
    
    >>> sunlight.apikey = 'your-key-here'

-------------------
legislators methods
-------------------

The legislators namespace is comprised of several functions:
    * legislators.get           - get a single legislator
    * legislators.getList       - get zero or more legislators
    * legislators.search        - fuzzy search for legislators by name
    * legislators.allForZip     - get all legislators representing a zipcode
    * legislators.allForLatLong - get all legislators representing a point


get and getList
---------------
    
legislators.get and legislators.getList both take any number of parameters and
return all legislators that match the provided criteria.  These parameters are
also the ones returned in each legislator object.  

The available parameters are:
    * title
    * firstname
    * middlename
    * lastname
    * name_suffix
    * nickname
    * party
    * state
    * district
    * in_office
    * gender
    * birthdate
    * phone
    * fax
    * website
    * webform
    * email
    * congress_office
    * bioguide_id
    * votesmart_id
    * fec_id
    * govtrack_id
    * crp_id
    * eventful_id
    * congresspedia_url
    * twitter_id
    * official_rss
    * youtube_url
    * senate_class
    * birthdate


To get the representative that represents NC-4:

    >>> print(sunlight.legislators.get(state='NC', district='4'))
    Rep. David Price (D-NC)
    
legislators.getList works much the same way, but returns a list.  It is
possible to do a more complex query, for instance
"all legislators from New York that are Republicans":

    >>> for leg in sunlight.legislators.getList(state='NY', party='R'):
    ...     print(leg)
    Rep. Pete King (R-NY)
    Rep. Christopher Lee (R-NY)


**It is preferred that you do not call getList without parameters as it will
pull down all legislators, if you need to do this feel free to grab the provided
dump of the API data available at http://services.sunlightlabs.com/api/**


search
------

legislators.search allows you to query the database with a less than perfect
representation of a legislator's name.

The search is tolerant of use of nicknames, lastname-firstname juxtaposition,
initials and minor misspellings.  The return is a set of results that include
legislator records as well as certainity scores between 0 and 1 (where 1 is
most certain).

Search takes two optional parameters

``threshold``
    the minimum score you want to return, the default is 0.8 and you should rarely go lower than 0.7.
``all_legislators``
    if True will search legislators in the API that are no longer in office (default is False)

An example usage of search is as follows:

    >>> for r in sunlight.legislators.search('Diane Finestine'):
    ...     print(r)
    0.92125 Sen. Dianne Feinstein (D-CA)

    
It is also possible to get multiple results:
    
    >>> for r in sunlight.legislators.search('Frank'):
    ...     print(r)
    1.0 Rep. Barney Frank (D-MA)
    0.972222222222 Rep. Trent Franks (R-AZ)
    0.952380952381 Sen. Al Franken (D-MN)


allForZip
---------

legislators.allForZip retrieves all legislators that represent a given zipcode.

This typically means two senators and one (or more) representatives.

To get all legislators that represent the 27511 zipcode:
    
    >>> for legislator in sunlight.legislators.allForZip(27511):
    ...     print(legislator)
    Rep. David Price (D-NC)
    Sen. Kay Hagan (D-NC)
    Sen. Richard Burr (R-NC)
    Rep. Brad Miller (D-NC)


allForLatLong
-------------

legislators.allForLatLong retrieves all legislators representing a given point.

This is a shortcut for calling districts.getDistrictFromLatLong and then
looking up the district representative and state senators.

To get all legislators that represent a location in western PA at 41.92, -80.14:
    
    >>> for legislator in sunlight.legislators.allForLatLong(41.92, -80.14):
    ...     print(legislator)
    Sen. Bob Casey (D-PA)
    Sen. Arlen Specter (D-PA)
    Rep. Kathy Dahlkemper (D-PA)


-----------------
districts methods
-----------------

The districts namespace is comprised of two functions:
    * districts.getDistrictsFromZip
    * districts.getDistrictFromLatLong


getDistrictsFromZip
-------------------

districts.getDistrictsFromZip fetches all districts that overlap a given
zipcode.

To get all districts that overlap 14623:
    >>> for district in sunlight.districts.getDistrictsFromZip(14623):
    ...     print(district)
    NY-29
    NY-28


getDistrictFromLatLong
----------------------

districts.getDistrictFromLatLong finds the district that a given lat-long
coordinate pair falls within.

To find out what district 61.13 N, 149.54 W falls within:
    >>> print(sunlight.districts.getDistrictFromLatLong(61.13, 149.54))
    AK-0

This point is in fact in Anchorage, Alaska, so this is correct.


-----------------
committee methods
-----------------

The committee namespace contains:
    * committee.getList
    * committee.get
    * committee.allForMember

getList
-------

committee.getList gets all committees for a given chamber (House, Senate, or Joint).

To see all joint committees for the current congress:
    >>> for c in sunlight.committees.getList('Joint'):
    ...     print(c)
    Joint Economic Committee
    Joint Committee on Printing
    Joint Committee on Taxation
    Joint Committee on the Library

get
---

committee.get gets full details for a given committee, including membership and subcommittees.

Example of getting details for a committee:

    >>> com = sunlight.committees.get('HSAG')
    >>> print(com.name)
    House Committee on Agriculture
    >>> for sc in com.subcommittees:
    ...     print(sc)
    Subcommittee on  Conservation, Credit, Energy, and Research
    Subcommittee on Department Operations, Oversight, Nutrition and Forestry
    Subcommittee on General Farm Commodities and Risk Management
    Subcommittee on Horticulture and Organic Agriculture
    Subcommittee on Livestock, Dairy, and Poultry 
    Subcommittee on Rural Development, Biotechnology, Specialty Crops, and Foreign Agriculture
    >>> for m in com.members:
    ...     print(m)
    Rep. Joe Baca (D-CA)
    Rep. John Boccieri (D-OH)
    Rep. Leonard Boswell (D-IA)
    Rep. Bobby Bright (D-AL)
    Rep. Dennis Cardoza (D-CA)
    Rep. Bill Cassidy (R-LA)
    Rep. Travis Childers (D-MS)
    Rep. Mike Conaway (R-TX)
    Rep. Jim Costa (D-CA)
    Rep. Henry Cuellar (D-TX)
    Rep. Kathy Dahlkemper (D-PA)
    Rep. Brad Ellsworth (D-IN)
    Rep. Jeff Fortenberry (R-NE)
    Rep. Bob Goodlatte (R-VA)
    Rep. Sam Graves (R-MO)
    Rep. Debbie Halvorson (D-IL)
    Rep. Stephanie Herseth Sandlin (D-SD)
    Rep. Tim Holden (D-PA)
    Rep. Tim Johnson (R-IL)
    Rep. Steven Kagen (D-WI)
    Rep. Steve King (R-IA)
    Rep. Larry Kissell (D-NC)
    Rep. Frank Kratovil (D-MD)
    Rep. Bob Latta (R-OH)
    Rep. Frank Lucas (R-OK)
    Rep. Blaine Luetkemeyer (R-MO)
    Rep. Cynthia Lummis (R-WY)
    Rep. Betsy Markey (D-CO)
    Rep. Jim Marshall (D-GA)
    Rep. Eric Massa (D-NY)
    Rep. Mike McIntyre (D-NC)
    Rep. Walt Minnick (D-ID)
    Rep. Jerry Moran (R-KS)
    Rep. Randy Neugebauer (R-TX)
    Rep. Collin Peterson (D-MN)
    Rep. Earl Pomeroy (D-ND)
    Rep. Phil Roe (R-TN)
    Rep. Mike Rogers (R-AL)
    Rep. Mark Schauer (D-MI)
    Rep. Jean Schmidt (R-OH)
    Rep. Kurt Schrader (D-OR)
    Rep. David Scott (D-GA)
    Rep. Adrian Smith (R-NE)
    Rep. G.T. Thompson (R-PA)
    Rep. Tim Walz (D-MN)

allForLegislator
----------------

All for legislator shows all of a legislator's committee and subcommittee memberships.

*note that the subcommittees included are only the subcommittees that the member has a seat on*

Showing all of a legislators committees and subcommittees:
    >>> for com in sunlight.committees.allForLegislator('S000148'):
    ...    print(com)
    ...    for sc in com.subcommittees:
    ...        print('   '+str(sc))
    Senate Committee on Rules and Administration
    Senate Committee on Finance
       Subcommittee on International Trade and Global Competitiveness
       Subcommittee on Social Security, Pensions and Family Policy
       Subcommittee on Taxation, IRS Oversight, and Long-term Growth
    Joint Committee on the Library
    Joint Economic Committee
    Senate Commmittee on the Judiciary
       Subcommittee on Administrative Oversight and the Courts
       Subcommittee on Antitrust, Competition Policy and Consumer Rights
       Subcommittee on Crime and Drugs
       Subcommittee on Immigration, Refugees and Border Security
       Subcommittee on Terrorism and Homeland Security
    Joint Committee on Printing
    Senate Committee on Banking, Housing, and Urban Affairs
       Subcommittee on Securities, Insurance, and Investment
       Subcommittee on Financial Institutions
       Subcommittee on Housing, Transportation, and Community Development
