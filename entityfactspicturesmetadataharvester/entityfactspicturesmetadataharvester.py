#!/usr/bin/python3
# -*- coding: utf-8 -*-
import argparse
import json
import os
import socket
import sys
import urllib.parse

from threading import current_thread

import requests
import rx
import xmltodict

from rx import operators as op
from rx.scheduler import ThreadPoolScheduler

USER_AGENT_HTTP_HEADER_KEY = 'user-agent'
USER_AGENT_PATTERN = "entityfactspicturesmetadataharvester-bot-from-{0}/0.0.1 (https://github.com/slub/entityfactspicturesmetadataharvester; zazi@smiy.org) entityfactspicturesmetadataharvester/0.0.1"
HOSTNAME = socket.getfqdn()
USER_AGENT = USER_AGENT_PATTERN.format(HOSTNAME)
HTTP_HEADERS = {USER_AGENT_HTTP_HEADER_KEY: USER_AGENT}
WIKIMEDIA_COMMONS_FILE_METADATA_API_ENDPOINT = "https://opendata.utou.ch/glam/magnus-toolserver/commonsapi.php?meta&image="
UTF8_CHARSET_ID = 'utf-8'
UNICODE_CHARSET_ID = 'unicode'
SLASH = "/"
ID_IDENTIFIER = "@id"
DEPICTION_IDENTIFIER = "depiction"
GND_IDENTIFIER_TAG = 'gnd_id'

METADATA_CONTENT_TYPE = "picture metadata"
WIKIMEDIA_COMMONS_FILE_METADATA_HARVESTING = "Wikimedia Commons file metadata"
METADATA_THREAD_POOL_SCHEDULER = ThreadPoolScheduler(10)


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def get_depiction_json(line):
    jsonline = json.loads(line)

    if ID_IDENTIFIER in jsonline:
        entitfacts_sheet_id = jsonline[ID_IDENTIFIER]
    else:
        eprint("no GND identifier in EntityFacts sheet '{0}' (thread = '{1}')".format(line, current_thread().name))
        return None

    last_index_of_slash_in_ef_sid = entitfacts_sheet_id.rfind(SLASH)
    if last_index_of_slash_in_ef_sid > 0:
        gnd_identifier = entitfacts_sheet_id[last_index_of_slash_in_ef_sid + 1:]
    else:
        eprint("no GND identifier in EntityFacts sheet id '{0}' (thread = '{1}')".format(entitfacts_sheet_id,
                                                                                         current_thread().name))
        return None

    if DEPICTION_IDENTIFIER in jsonline:
        depiction_json = jsonline[DEPICTION_IDENTIFIER]
    else:
        eprint(
            "no depiction information for GND identifier '{0}' in its EntityFacts sheet (thread = '{1}')".format(
                gnd_identifier, current_thread().name))
        return None

    eprint("found depiction information of GND identifier '{0}' in its EntityFacts sheet (thread = '{1}')".format(
        gnd_identifier, current_thread().name))
    depiction_json_tuple = (depiction_json, gnd_identifier)

    return depiction_json_tuple


def get_metadata_url(depiction_json, gnd_identifier):
    if ID_IDENTIFIER in depiction_json:
        picture_url = depiction_json[ID_IDENTIFIER]
    else:
        eprint(
            "no picture URL for GND identifier '{0}' in depiction information '{1}' of its EntityFacts sheet (thread = '{2}')".format(
                gnd_identifier, depiction_json, current_thread().name))
        return None

    last_index_of_slash_in_picture_url = picture_url.rfind(SLASH)
    if last_index_of_slash_in_picture_url > 0:
        picture_file_name = picture_url[last_index_of_slash_in_picture_url + 1:]
    else:
        eprint("no file name found in picture URL '{0}' of GND identifier '{1}' (thread = '{2}')".format(picture_url,
                                                                                                         gnd_identifier,
                                                                                                         current_thread().name))
        return None

    metadata_url = WIKIMEDIA_COMMONS_FILE_METADATA_API_ENDPOINT + urllib.parse.quote(picture_file_name)

    eprint(
        "found/created Wikimedia Commons file metadata URL of GND identifier '{0}' in its depiction information (thread = '{1}')".format(
            gnd_identifier,
            current_thread().name))

    result_tuple = (metadata_url, gnd_identifier)
    return result_tuple


def do_request(image_uri, gnd_identifier, content_type):
    eprint(
        "try to retrieve {0} for GND identifier '{1}' from URL '{2}' (thread = '{3}')".format(content_type,
                                                                                              gnd_identifier,
                                                                                              image_uri,
                                                                                              current_thread().name))
    response = requests.get(image_uri, headers=HTTP_HEADERS, timeout=60)
    if response.status_code != 200:
        eprint("couldn't fetch {0} for GND identifier '{1}' from URL '{2}' got a '{3}' (thread = '{4}')".format(
            content_type, gnd_identifier, image_uri, response.status_code, current_thread().name))
        return None

    response_body = response.content
    eprint("retrieved {0} for GND identifier '{1}' (thread = '{2}')".format(content_type, gnd_identifier,
                                                                            current_thread().name))
    return response_body


def retrieve_content_obs(request_url_tuple, content_type):
    return rx.of(request_url_tuple).pipe(
        op.map(lambda r_url_tuple: retrieve_content(r_url_tuple[0], r_url_tuple[1], content_type)),
        op.filter(lambda value1: value1 is not None))


def retrieve_content(request_url, gnd_identifier, content_type):
    response = do_request(request_url, gnd_identifier, content_type)
    if response is None:
        return None
    response_tuple = (response, gnd_identifier)
    return response_tuple


def add_gnd_identifier_to_response_obs(response_tuple_obs):
    return response_tuple_obs.pipe(op.map(lambda response_tuple: add_gnd_identifier_to_response(response_tuple[0],
                                                                                                response_tuple[1])))


def add_gnd_identifier_to_response(response_xml_bytes, gnd_identifier):
    response_xml_string = response_xml_bytes.decode(UTF8_CHARSET_ID)
    response_dict = xmltodict.parse(response_xml_string)
    response_dict[GND_IDENTIFIER_TAG] = gnd_identifier
    result_tuple = (response_dict, gnd_identifier)

    return result_tuple


def write_content_as_ldj_obs(content_dict_tuple_obs, content_type):
    return content_dict_tuple_obs.pipe(op.map(lambda content_dict_tuple: write_content_as_ldj(content_dict_tuple[0],
                                                                                              content_dict_tuple[1],
                                                                                              content_type)))


def write_content_as_ldj(content_dict, gnd_identifier, content_type):
    jsonline = json.dumps(content_dict, indent=None) + os.linesep
    sys.stdout.write(jsonline)
    eprint("wrote {0} for GND identifier '{1}' (thread = '{2}')".format(content_type, gnd_identifier,
                                                                        current_thread().name))
    return gnd_identifier


def push_input(observer, scheduler):
    for line in sys.stdin:
        observer.on_next(line)
    return observer.on_completed()


def do_harvesting(source_obs,
                  get_url_function,
                  content_type,
                  harvesting_type,
                  harvesting_scheduler):
    all_in_one_harvesting = source_obs.pipe(
        op.map(lambda line: get_depiction_json(line)),
        op.filter(lambda value: value is not None),
        op.map(lambda depiction_json_tuple: get_url_function(depiction_json_tuple[0],
                                                             depiction_json_tuple[1])),
        op.filter(lambda value: value is not None),
        op.map(lambda url_tuple: retrieve_content_obs(url_tuple, content_type)),
        op.map(lambda response_tuple_obs: add_gnd_identifier_to_response_obs(response_tuple_obs)),
        op.map(lambda content_tuple_obs: write_content_as_ldj_obs(content_tuple_obs, content_type)),
        op.flat_map(lambda x: x))

    all_in_one_harvesting.subscribe(
        on_next=lambda gnd_identifier: eprint(
            "PROCESSED {0} of GND identifier '{1}': {2}".format(harvesting_type, gnd_identifier,
                                                                current_thread().name)),
        on_error=lambda e: eprint(e),
        on_completed=lambda: eprint("PROCESS {0}s harvesting done!".format(harvesting_type)),
        scheduler=harvesting_scheduler)


def run():
    parser = argparse.ArgumentParser(prog='entityfactspicturesmetadataharvester',
                                     description='Reads depiction information (images URLs) from given EntityFacts sheets (as line-delimited JSON records) and retrieves the (Wikimedia Commons file) metadata of these pictures (as line-delimited JSON records).',
                                     epilog='example: entityfactspicturesmetadataharvester < [INPUT LINE-DELIMITED JSON FILE WITH ENTITYFACTS SHEETS] > [OUTPUT PICTURES METADATA LINE-DELIMITED JSON FILE]',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    args = parser.parse_args()

    if hasattr(args, 'help') and args.help:
        parser.print_usage(sys.stderr)
        exit(-1)

    source = rx.create(push_input)

    source_connectable_obs = source.pipe(op.publish())

    # Wikimedia Commons file metadata harvesting
    do_harvesting(source_connectable_obs,
                  get_metadata_url,
                  METADATA_CONTENT_TYPE,
                  WIKIMEDIA_COMMONS_FILE_METADATA_HARVESTING,
                  METADATA_THREAD_POOL_SCHEDULER)

    source_connectable_obs.connect()


if __name__ == "__main__":
    run()
