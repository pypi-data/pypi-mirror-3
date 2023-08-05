Information:

adi_call_galleryview is a copy of adi_suite_gallerview 

exept for the following lines after the html-tag:





<div metal:fill-slot="top_slot" tal:define="dummy python:request.set('disable_border', 1);
                                            disable_column_one python:request.set('disable_plone.leftcolumn',1);
                                            disable_column_two python:request.set('disable_plone.rightcolumn',1);
                                           " />


This will inhibit the deliverance of the editbar and the left- and right-column to the browser.


The reason for the copy is to have an own css-selector ('.section-adi_call_gallerview')

for the adi_call_galleryview (called from a list of folders), where unnecessary 
    
portal parts shouldn't be shown.


Unfortunately, I couldn't find a solution to not deliver the leftover parts, too.

The disableling seems to be only available for the above three parts.
