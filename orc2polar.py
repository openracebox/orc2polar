#!/usr/bin/env python3
"""
Write a CSV version of ORC Polar data.

Author: Lasse Karstensen <lasse.karstensen@gmail.com>, November 2017
"""
import argparse
import json
import logging
import re

from os.path import dirname, join
from pprint import pprint
from sys import argv, stderr
from os import getenv

import requests

def format_csv(allowances):
    speeds = []  # [(angle1, [speeds]), (angle2, [speeds]), ..]
    def pot2knots(k):
        return "%0.4f" % (1/k*3600.)  # Precision discard to make it readable.

    for k, v in allowances.items():
        if not k.startswith("R"):
            continue
        if k == "Run":
            k = "R180"

        assert k.startswith("R")
        k = int(k[1:])

        knots = list(map(pot2knots, v))
        speeds.append((k, knots))
    beating = tuple(zip(allowances["BeatAngle"], list(map(pot2knots, v))))

    for i in range(len(beating)):
        row = [float('nan')] * len(speeds[0][1])
        row[i] = beating[i][1]
        t = (beating[i][0], row)
        speeds.append(t)
    speeds.sort()

    if 0:
        pprint(speeds)

    def join_nan(items, sep=","):
        s = ""
        for v in items:
            s += ";%s" % (v)
        return s
    logging.info("Using CSV output format with ; as separator. Unit is knots.")
    result = "twa\\tws;6;8;10;12;14;16;20\n"
    for angle, items in speeds:
        result += "%.1f%s\n" % (angle, join_nan(items))
    return result


def fetch_dataset(country_code):
    USER_AGENT = "orc2polar.py (+http://github.com/openracebox/ )"
    try:
        url = "http://data.orc.org/public/WPub.dll?action=DownRMS&CountryId=%s&ext=json" % country_code
        response = requests.get(url, headers={"User-Agent": USER_AGENT})
    except Exception as e:
        raise e
    if response.status_code != 200:
        return None

    return response.json()




if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description="ORC2polar - Extract polar diagram data from ORC certificate")
    parser.add_argument("sailnumber", help="Sail number to pick. Example: \"NOR15000\"")
    parser.add_argument("--debug", action="store_true",
                        help="Enable debug output")
    parser.add_argument("--smartfilter", metavar="filterarg",
        help="If there are more than one boat with sailnumber, filter for this in the vessel name. Example: \"titanic\"")

    parser.add_argument("--output-format", choices=["csv"], default="csv", help="Which format to output in. Default: csv")

    parser.add_argument("--datafile", metavar="jsonfile",
                        help="Use a previously downloaded file as data source.")
    parser.add_argument("--save-datafile", metavar="jsonfile",
                        help="Write downloaded file to local disk")

    if getenv("VIM"):
        argv.append("--debug")
#        argv += ["--save-datafile", "nor.json"]
#        argv += ["--datafile", "nor.json"]
        argv += ["NOR15149"]

    if len(argv) == 1:
        parser.print_help()
        exit()
    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(level=logging.DEBUG)

    match = re.match("([a-zA-Z]{2,})([0-9]+)", args.sailnumber)
    if not match:
        logging.error("Unable to parse sail number %s", args.sailnumber)
        exit(1)
    country_code, sailnumber = match.groups()
    logging.debug("Looking for %s %s ", country_code, sailnumber)

    if args.datafile:
        with open(args.datafile, "r") as fp:
            boats = json.load(fp)
            logging.debug("Read dataset from %s. Make sure you are using the right country file." % fp.name)
    else:
        boats = fetch_dataset(country_code)
        if args.save_datafile:
            with open(args.save_datafile, "w") as fp:
                json.dump(boats, fp)
                logging.info("Wrote downloaded dataset to %s", fp.name)


    candidates = []
    for boat in boats["rms"]:
        if sailnumber in boat["SailNo"]:
            if args.smartfilter:
                raise NotImplementedError()
            candidates.append(boat)

    if len(candidates) == 0:
        logging.error("%s not found in ORC data.", args.sailnumber)
        exit(1)
    elif len(candidates) > 1:
        logging.error("Multiple boats found. Use --smartfilter. %s not found in ORC data.", args.sailnumber)
        for boat in candidates:
            logging.info("Boat name seen: %s" % boat["YachtName"])
        exit(2)
    else:
        boat = candidates[0]

    logging.info("Using data for %s %s" % (boat["SailNo"], boat["YachtName"]))

    if args.output_format == "csv":
        def boat_filename(boat):
            return "%s.polar.csv" % boat["SailNo"].replace(" ", "").lower()

        polar_csv = format_csv(boat["Allowances"])
        with open(boat_filename(boat), "w") as fp:
            fp.write(polar_csv)
            logging.info("Wrote %s",  fp.name)
    else:
        raise NotImplementedError(args.output_format)
