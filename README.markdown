URL health checker
==================

- Author: Viktor Stískala, viktor@stiskala.cz
- Created: 2011-04-22
- License: New BSD License

This utility goes through the links in the specified file and checks their
health by returned http code. If the code is other than 200 (OK) then error
message is printed to standard output.

### Usage ###

<pre>
./checker.py links_file
</pre>

## Links file ##

- file name have to be passed as first argument to the utility
- each line should contain one url address, use # for comments
- you can specify another IP address for each link to override DNS lookup
	- can be used for checking links after server replacement before
	changing DNS settings to the new IP address

## Requirements ##

- Python 2.5+
- use 2to3 utility before using in Python 3
