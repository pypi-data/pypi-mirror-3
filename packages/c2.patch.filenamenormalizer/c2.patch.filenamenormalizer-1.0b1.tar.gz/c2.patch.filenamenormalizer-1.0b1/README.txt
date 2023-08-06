Introduction
==============

This patch product is for downloaded filename become strange ascii code in muluti-byte languages on Plone


- When downloading file with Japanese name, downloaded file has some strange ascii coded name.

- I think we should get file name that shows in Plone page.

- This happens on all Plone version. I think if the file is named with multi byte code, this strange ascii name shows up.

- Please, look at attached file to fix this problem for IE and Firefox. Other browsers, we are still working on it.

  - http://dev.plone.org/plone/ticket/8591


requirement
-------------
Plone 3.x (Tested by Plone 3.3.1 on MaxOS X 10.5)

