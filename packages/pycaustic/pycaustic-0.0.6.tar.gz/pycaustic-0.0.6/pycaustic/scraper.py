# -*- coding: utf-8 -*-

import requests
import uuid
import copy
import os
import urlparse
import json

from .patterns import Regex
from .responses import ( DoneLoad, DoneFind, Wait, MissingTags,
                         Failed, Result )
from .templates import Substitution
from .errors import InvalidInstructionError, SchemeSecurityError

class Request(object):

    def __init__(self, instruction, tags, input, force, request_id, uri):
        self._instruction = copy.deepcopy(instruction)
        self._tags = tags
        self._input = input
        self._force = force
        self._id = request_id
        self._uri = uri

    @property
    def instruction(self):
        return self._instruction

    @property
    def tags(self):
        return self._tags

    @property
    def input(self):
        return self._input

    @property
    def force(self):
        return self._force

    @property
    def id(self):
        return self._id

    @property
    def uri(self):
        return self._uri


class Scraper(object):

    def __init__(self, session=requests.Session()):
        # We defensively deepcopy session -- advisable?
        self._session = copy.deepcopy(session)

    def _load_uri(self, base_uri, uri_to_resolve):
        """
        Obtain a remote instruction.

        Returns the instruction as a python object, along with the resolved uri
        """
        resolved_uri = urlparse.urlsplit(urlparse.urljoin(base_uri, uri_to_resolve))
        base_scheme = urlparse.urlsplit(base_uri).scheme
        if base_scheme is not None and base_scheme != resolved_uri.scheme:
            raise SchemeSecurityError("Cannot cross from '%s' to '%s'" % (
                base_scheme, resolved_uri.scheme))

        try:
            if resolved_uri.scheme in ['http', 'https']:
                instruction = json.loads(requests.get(resolved_uri).text)
            elif resolved_uri.scheme is '':
                instruction = json.load(open(urlparse.urlunsplit(resolved_uri)))
            else:
                raise InvalidInstructionError("Reference to unsupported scheme '%s'" % (
                    resolved_uri.scheme))
            return instruction, urlparse.urlunsplit(resolved_uri)
        except requests.exceptions.RequestException as e:
            raise InvalidInstructionError("Couldn't load '%s': %s" % (resolved_uri, e))
        except IOError as e:
            raise InvalidInstructionError("Couldn't open '%s': %s" % (resolved_uri, e))
        except ValueError:
            raise InvalidInstructionError("Invalid JSON in '%s'" % resolved_uri)

    def _scrape_find(self, req, instruction, description, then):
        """
        Scrape a find instruction
        """
        if 'find' not in instruction:
            raise InvalidInstructionError("Missing regex")

        findSub = Substitution(instruction['find'], req.tags)
        replaceSub = Substitution(instruction.get('replace', '$0'), req.tags)
        nameSub = Substitution(instruction.get('name'), req.tags)
        ignore_case = instruction.get('case_insensitive', False)
        multiline = instruction.get('multiline', False)
        dot_matches_all = instruction.get('dot_matches_all', True)

        # Default to full range
        min_match = instruction.get('min_match', 0)
        max_match = instruction.get('max_match', -1)
        match = instruction.get('match', None)

        # Use single match if it was defined
        min_match = min_match if match is None else match
        max_match = max_match if match is None else match

        # Python counts a little differently
        max_match = None if max_match == -1 else max_match + 1

        missing_tags = Substitution.add_missing(findSub, replaceSub, nameSub)
        if len(missing_tags):
            return MissingTags(req, missing_tags)

        # Default to regex as string
        name = nameSub.result if nameSub.result else findSub.result
        replace = replaceSub.result

        regex = Regex(findSub.result, ignore_case, multiline, dot_matches_all, replace)

        # Negative max means we can't utilize the generator, sadly...
        subs = [s for s in regex.substitutions(req.input)][min_match:max_match]

        results = []
        # Call children once for each substitution, using it as input
        # and with a modified set of tags.
        for s in subs:
            fork_tags = copy.deepcopy(req.tags)
            fork_tags[name] = s
            results.append(Result(s,
                                  Scraper(self._session).scrape(then,
                                                                tags=fork_tags,
                                                                input=s,
                                                                uri=req.uri
                                                               )))

        if len(results):
            return DoneFind(req, name, description, results)
        else:
            return Failed(req, "No matches for '%s', evaluated to '%s'" % (
                instruction['find'], findSub.result))

    def _scrape_load(self, req, instruction, description, then):
        """
        Scrape a load instruction

        :returns: DoneLoad, Wait, MissingTags, or Failed
        """
        if 'load' not in instruction:
            raise InvalidInstructionError("Missing URL in `load` key")

        method = instruction.get('method', 'get')
        if method not in ['head', 'get', 'post']:
            raise InvalidInstructionError("Illegal HTTP method: %s" % method)

        urlSub = Substitution(instruction['load'], req.tags)
        nameSub = Substitution(instruction.get('name'), req.tags)
        postsSub = Substitution(instruction.get('posts'), req.tags)
        cookiesSub = Substitution(instruction.get('cookies', {}), req.tags)
        headersSub = Substitution(instruction.get('headers', {}), req.tags)

        # Extract our missing tags, if any
        missing_tags = Substitution.add_missing(urlSub, nameSub, postsSub,
                                                cookiesSub)
        if len(missing_tags):
            return MissingTags(req, missing_tags)

        url = urlSub.result
        name = nameSub.result if nameSub.result else url

        if req.force != True:
            return Wait(req, name, description)

        posts = postsSub.result
        cookies = cookiesSub.result
        headers = headersSub.result

        try:
            opts = dict(cookies=cookies, headers=headers)
            if method == 'post' or posts:
                opts['data'] = posts
                # Force use of POST if post-data was set.
                method = 'post'

            requester = getattr(self._session, method)

            resp = requester(urlSub.result, **opts)
            if resp.status_code == 200:
                # Call children using the response text as input
                result = Result(resp.text,
                                Scraper(self._session).scrape(then,
                                                              tags=req.tags,
                                                              input=resp.text,
                                                              uri=req.uri
                                                             ))
                return DoneLoad(req, name, description, result, resp.cookies)
            else:
                return Failed(req, "Status code %s from %s" % (
                    resp.status_code, url))
        except requests.exceptions.RequestException as e:
            return Failed(req, str(e))

    def _extend_instruction(self, orig, extension):
        """
        Extend one instruction with another.  Orig and extension are modified
        in-place!
        """
        # keys that are turned into arrays & extended
        for ex_key in ['extends', 'then']:
            # Nothing to extend, skip out the pop at end
            if ex_key not in extension:
                continue
            # We can just copy it over
            elif ex_key not in orig:
                orig[ex_key] = extension[ex_key]
            else:
                # Wrap the original value in a list
                if not isinstance(orig[ex_key], list):
                    orig[ex_key] = [orig[ex_key]]

                # Use extend if the extension is also a list, append otherwise
                if isinstance(extension[ex_key], list):
                    orig[ex_key].extend(extension[ex_key])
                else:
                    orig[ex_key].append(extension[ex_key])

            # Clear out key for update at end
            extension.pop(ex_key)

        # keys that are updated
        for up_key in ['cookies', 'headers', 'posts']:
            # Nothing to update, skip out pop at end
            if up_key not in extension:
                continue
            # We can just copy it over
            elif up_key not in orig:
                orig[up_key] = extension[up_key]
            # If they're both dicts, then we update.  If not, then a replace
            # will happen.
            else:
                orig_val = orig[up_key]
                up_val = extension[up_key]
                if isinstance(orig_val, dict) and isinstance(up_val, dict):
                    orig_val.update(up_val)
                # Keep things available for total replacement.
                else:
                    continue

            # Clear out key for update at end
            extension.pop(up_key)

        # everything else is replaced.
        orig.update(extension)

    def _scrape_dict(self, req, instruction):
        """
        Scrape a dict instruction.

        :returns: Response
        """
        instruction = copy.deepcopy(instruction)

        while 'extends' in instruction:
            extends = instruction.pop('extends')
            if isinstance(extends, basestring):
                loaded_instruction, target_uri = self._load_uri(req.uri, extends)
                self._extend_instruction(instruction, loaded_instruction)
            elif isinstance(extends, dict):
                self._extend_instruction(instruction, extends)
            elif isinstance(extends, list):
                for ex in extends:
                    if isinstance(ex, basestring):
                        loaded_instruction, target_uri = self._load_uri(req.uri, ex)
                        self._extend_instruction(instruction, loaded_instruction)
                    elif isinstance(ex, dict):
                        self._extend_instruction(instruction, ex)
                    else:
                        raise InvalidInstructionError("element of `extends` list must be a dict or str")
            else:
                raise TypeError()

        then = instruction.pop('then', [])
        description = instruction.pop('description', None)

        if 'find' in instruction:
            return self._scrape_find(req, instruction, description, then)
        elif 'load' in instruction:
            return self._scrape_load(req, instruction, description, then)
        else:
            raise InvalidInstructionError("Could not find `find` or `load` key.")

    def scrape(self, instruction, tags={}, input='', force=False, **kwargs):
        """
        Scrape a request.

        :param: instruction An instruction, either as a string, dict, or list
        :type: str, dict, list
        :param: (optional) tags Tags to use for substitution
        :type: dict
        :param: (optional) input Input for Find
        :type: str
        :param: (optional) force Whether to actually load a load
        :type: bool
        :param: (optional) uri URI to resolve from
        :type: str
        :param: (optional) id ID for request
        :type: str

        :returns: Response or list of Responses
        """

        uri = kwargs.pop('uri', os.getcwd() + os.path.sep)
        req_id = kwargs.pop('id', str(uuid.uuid4()))

        # Have to track down the instruction.
        while isinstance(instruction, basestring):
            instructionSub = Substitution(instruction, tags)
            if instructionSub.missing_tags:
                return MissingTags(self, instructionSub.missingTags)
            instruction, uri = self._load_uri(uri, instructionSub.result)

        req = Request(instruction, tags, input, force, req_id, uri)

        # Handle each element of list separately within this context.
        if isinstance(instruction, list):
            return map(lambda i: Scraper(self._session).scrape(i,
                                                               tags=tags,
                                                               input=input,
                                                               force=force,
                                                               uri=uri),
                      instruction)

        # Dict instructions are ones we can actually handle
        elif isinstance(instruction, dict):
            return self._scrape_dict(req, instruction)

        # Fail.
        else:
            raise InvalidInstructionError(instruction)
