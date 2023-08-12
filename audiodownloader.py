"""
This addon and all code included is open-source under the Apache-2.0 License

CREDIT TO Yomichan by FooSoft Productions for the idea of hashing the audio files to be able to compare them.
https://foosoft.net/projects/yomichan/

Author:         Dillon Wall
Description:    This file handles all API requests and audio specific functions.
                The main functionality of this file is to use an AudioDownloader object to download the audio file
                    for an Anki card, save it to the user's collection.media, and return the file name.
"""
import requests
import json
import re
import os
import hashlib
import mimetypes

DEFAULT_TIMEOUT = 15


# Static funcs
def substitute_string_vars(s, replace_dict, duplicate_fld):
    """
    Substitutes any variable in {} in the string (s) with a corresponding entry in replace_dict
    """
    # validate string so that all variable names (between {}) are lowercase
    val_str = ""
    for sub_str in re.split('({[^}]*})', s):
        if sub_str.startswith('{'):
            val_str += sub_str.lower()
        else:
            val_str += sub_str

    relevant_keys = []
    prev_val = ""
    for key, value in replace_dict.items():
        if val_str.find("{" + key.lower() + "}") >= 0:
            if value == "" and duplicate_fld:
                value = prev_val
            relevant_keys.append(key)
            val_str = val_str.replace("{" + key.lower() + "}", value)
            prev_val = value

    return val_str, relevant_keys


def get_request(url, allow_redirects=True):
    """
    Performs a GET request to the specified url
    Uses a predefined User-Agent to make it look like we are accessing it from the browser
    """
    if url is None or not url.startswith("http"):
        raise Exception(url)

    # In order to bypass certain limitations from sites that require a browser to access,
    #   this header makes it look like we are using a browser instead of whatever is default
    response = requests.request(
        method="GET",
        headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'},
        url=url,
        timeout=DEFAULT_TIMEOUT
    )

    if not response:
        raise IOError("No response for %s", url)

    if response.status_code != 200:
        value_error = ValueError(
            "Got %d status for %s" %
            (response.status_code, url)
        )
        try:
            value_error.payload = response.content
            response.close()
        except Exception:
            pass
        raise value_error

    if not allow_redirects and response.geturl() != url:
        raise ValueError("Request has been redirected")

    content_type = response.headers.get('Content-Type', '')
    is_json = 'application/json' in content_type
    audio_ext = None
    if not is_json:
        audio_ext = mimetypes.guess_extension(content_type)
        if not audio_ext:
            if 'mpeg' in content_type:
                audio_ext = '.mp3'
            elif 'aac' in content_type:
                audio_ext = '.aac'
            else:
                audio_ext = os.path.splitext(url)[1]
    payload = response.content
    response.close()

    return payload, is_json, audio_ext


def filter_urls_list(arr):
    """
    Recursive helper for  filter_urls_dict
    """
    for val in arr:
        if type(val) is dict:
            return filter_urls_dict(val)
        elif type(val) is list:
            return filter_urls_list(val)
        else:
            return  # we shouldn't get here?


def filter_urls_dict(dictionary):
    """
    Expects a dictionary
    Recursively searches and filters out any urls from the json
    for now, this just returns the first url it finds
    """
    # raise Exception(dictionary)
    for key in dictionary:
        if type(dictionary[key]) is dict:
            return filter_urls_dict(dictionary[key])
        elif type(dictionary[key]) is list:
            return filter_urls_list(dictionary[key])
        elif key.lower() == 'url':
            return dictionary[key]


def save_from_https(media_content, output_file_name):
    """
    Saves a file to the user's media collection
    """
    open(output_file_name, 'wb').write(media_content)


def create_file_name(args_dict, relevant_keys, audio_name, audio_ext):
    """
    Create a new file name from the provided args dict
    """
    filename = audio_name
    for key in relevant_keys:
        if key in args_dict:
            filename += '_' + str(args_dict[key])

    filename = filename.replace('[', '').replace(']', '')    # remove brackets

    return filename + audio_ext


def shaHashDigest(hashItem):
    """
    # Credit Yomichan for the idea, refactored the audio hashing system for use in python
    Hashes the given hashItem into SHA-256 format and returns the hex digest
    """
    m = hashlib.sha256()
    m.update(hashItem)

    digest = m.hexdigest()

    return digest


def isAudioBinaryValid(hashItem):
    """
    # Credit Yomichan for the idea, refactored the audio hashing system for use in python
    Checks the audio binary and makes sure it isn't the JPod101 no-audio audio file
    """
    digest = shaHashDigest(hashItem)
    if digest == 'ae6398b5a27bc8c0a771df6c907ade794be15518174773c58c7c7ddd17098906':    # Invalid audio file hash
        return False
    return True


class AudioDownloader:
    def __init__(self, audio_sources, mw):
        self.audio_sources = audio_sources
        self.mw = mw

    def download_single(self, args_dict, duplicate_fld):
        """
        Downloads an audio file based on the args_dict,
            saves it to the user's collection.media,
            and returns the file name.
        """
        # try each in order, if result is nothing or error occurs try next
        for audio_name, raw_url in self.audio_sources.items():
            try:
                get_url, relevant_keys = substitute_string_vars(raw_url, args_dict, duplicate_fld)
                request_payload, is_json, audio_ext = get_request(get_url)
                if is_json:
                    json_dict_payload = json.loads(request_payload)
                    download_url = filter_urls_dict(json_dict_payload)
                    request_payload, _, audio_ext = get_request(download_url)

                if not isAudioBinaryValid(request_payload):
                    continue

                output_file_name = create_file_name(args_dict, relevant_keys, audio_name, audio_ext)
                full_output_file_name = os.path.join(self.mw.col.media.dir(), output_file_name)
                save_from_https(request_payload, full_output_file_name)

                return output_file_name
            except Exception:
                pass

        return None
