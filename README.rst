ORC2polar
=========

This is a small tool to download and save polars from the ORC certificate.

"Polars" in sail boat racing are computed/theoretical optimal speeds
for a given wind angle.

This is a console based tool capable of offline operation (with --datafile), so
you can easily extract polars for competing boats even when offshore/offline.

Usage
-----

::

	usage: orc2polar.py [-h] [--debug] [--smartfilter filterarg]
						[--output-format {csv}] [--datafile jsonfile]
						[--save-datafile jsonfile]
						sailnumber

	ORC2polar - Extract polar diagram data from ORC certificate

	positional arguments:
	  sailnumber            Sail number to pick. Example: "NOR15000"

	optional arguments:
	  -h, --help            show this help message and exit
	  --debug               Enable debug output
	  --smartfilter filterarg
							If there are more than one boat with sailnumber,
							filter for this in the vessel name. Example: "titanic"
	  --output-format {csv}
							Which format to output in. Default: csv
	  --datafile jsonfile   Use a previously downloaded file as data source.
	  --save-datafile jsonfile
							Write downloaded file to local disk

Requirements
------------

::

    pip3 install requests


Contact
-------

Written by Lasse Karstensen <lasse.karstensen@gmail.com>.

Licensed under GPLv2.

Issues can be filed on https://github.com/openracebox/orc2polar/issues/
