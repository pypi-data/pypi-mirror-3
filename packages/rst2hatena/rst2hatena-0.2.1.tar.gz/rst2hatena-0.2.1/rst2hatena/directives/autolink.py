# -*- coding:utf-8 -*-

# Copyright (c) 2011 Naoya INADA <naoina@kuune.org>
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.

# THIS SOFTWARE IS PROVIDED BY AUTHOR AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL AUTHOR OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.

__author__ = "Naoya INADA <naoina@kuune.org>"

__all__ = [
    "Niconico",
    "Google",
    "Amazon",
    "Wikipedia",
    "Twitter",
    "Map",
]

import re

from docutils.parsers.rst import Directive
from docutils.parsers.rst import directives

from rst2hatena import hatena_nodes


class Niconico(Directive):
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {}

    def run(self):
        video_id = directives.unchanged_required(self.arguments[0])
        if not re.match(r"sm\d+?", video_id):
            raise self.error(
                'Error in "%s" directive: "%s" is not a valid video id.'
                % (self.name, video_id))
        niconico_node = hatena_nodes.niconico(self.block_text,
                videoid=video_id)
        return [niconico_node]


class Google(Directive):
    target_values = ("image", "news")

    def target(arg):
        return directives.choice(arg, Google.target_values)

    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {
        "target": target,
    }

    def run(self):
        self.options["query"] = directives.unchanged_required(
                self.arguments[0])
        google_node = hatena_nodes.google(self.block_text, **self.options)
        return [google_node]


class Amazon(Directive):
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {}

    def run(self):
        amazon_query = directives.unchanged_required(self.arguments[0])
        amazon_node = hatena_nodes.amazon(self.block_text, query=amazon_query)
        return [amazon_node]


class Wikipedia(Directive):
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {
        "lang": directives.unchanged,
    }

    def run(self):
        self.options["query"] = directives.unchanged_required(
                self.arguments[0])
        wikipedia_node = hatena_nodes.wikipedia(self.block_text,
                **self.options)
        return [wikipedia_node]


class Twitter(Directive):
    quotetype_values = ("title", "tweet", "detail", "tree")

    def quote_type(arg):
        return directives.choice(arg, Twitter.quotetype_values)

    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {
        "type": quote_type,
    }

    def run(self):
        id = directives.unchanged_required(self.arguments[0])
        if id.startswith("@"):
            if "type" in self.options:
                raise self.error(
                    'Error in "%s" directive: "type" option must not be given '
                    'if argument is Twitter ID(starts with "@").'
                    % (self.name))
        elif "type" not in self.options:
            raise self.error(
                'Error in "%s" directive: "type" option must be given '
                'if argument is Tweet ID.' % (self.name))
        self.options["id"] = id
        twitter_node = hatena_nodes.twitter(self.block_text, **self.options)
        return [twitter_node]


class Map(Directive):
    displaytype_values = ("map", "satellite", "hybrid")

    def display_type(arg):
        return directives.choice(arg, Map.displaytype_values)

    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {
        "x": directives.unchanged_required,
        "y": directives.unchanged_required,
        "width": directives.positive_int,
        "height": directives.positive_int,
        "type": display_type,
    }

    def run(self):
        if "x" not in self.options or "y" not in self.options:
            raise self.error(
                'Error in "%s" directive: "x" and "y" option is required.'
                % (self.name))
        if "width" in self.options and "height" in self.options:
            raise self.error(
                'Error in "%s" directive: "width" and "height" option can not '
                'be combined.'
                % (self.name))
        map_node = hatena_nodes.map(self.block_text, **self.options)
        return [map_node]
