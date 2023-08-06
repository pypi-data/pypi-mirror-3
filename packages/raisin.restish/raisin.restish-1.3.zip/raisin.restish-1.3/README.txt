= raisin.restish =

This is the restish server used by the raisin.pyramid server to fetch resources to render the
boxes of its pages.

For more information about restish, check out the official website:

    http://ish.io/projects/show/restish

= Starting the server =

For information on starting and stopping the server, have a look at the README.txt
in raisin.buildout:

svn cat svn://yourusername@svn.crg.es/big/raisin/raisin.buildout/trunk/README.txt

= About the server =

The only purpose of this module serve the resources defined in root.py of

    raisin.resource

It also provides the database adapters in the request environment, using the DB class from

    raisin.mysqldb

Other than that, this package is just a normal restish server, and should just be capable of
delivering the resources defined in raisin.resource.
