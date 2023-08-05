Introduction
============

A Plone portlet that uses the catalog internals to find 'similar' content to the page you are looking at

This portlet uses some deep dark data structures within the ZCatalog and ZCTextindex, so it could be brittle in the future
if those structures are changed. Then again, they have been the same for the past 8 years or so ;)

This portlet also runs in linear time relative to the number for documents you have in your site, so
it could well slow things down. That said I've tried to make it pretty efficient.

How it Works
============

In a nutshell, this portlet compares the text content of an object with all other objects on the site to
find other objects with a similar content. The steps are as follows:

1) Find the path of this document
2) Look up the record_id (docid) of this path in the catalog
3) Look in the SearchableText index to find all word ids (wids) in this document
4) Work out the top 20 most 'important' words in this document [*]
5) For each of the top 20 words, find all documents containing any of those words
6) Use a vector space model to measure similarity of each candidate document to our top 20 words
7) Return the top 10 most similar documents.



[*] We work out the top 20 words using a TF*IDF algorithm (the same used in ZCTextIndex.OkapiIndex) to find the 
words that appear proportionately high in this document compared to all documents in general.



TODO
====

Add some caching ;)

