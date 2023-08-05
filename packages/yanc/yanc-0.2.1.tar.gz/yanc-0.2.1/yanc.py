import re

from nose.plugins import Plugin

import termcolor


class ColorStream(object):

    _colors = {
        "green" : ("OK", "ok", "."),
        "red" : ("ERROR", "FAILED", "errors", "E"),
        "yellow" : ("FAILURE", "FAIL", "failures", "F"),
        "magenta" : ("SKIP", "S"),
        "blue" : ("-" * 70, "=" * 70),
        }

    def __init__(self, stream):
        self._stream = stream
        self._color_map = {}
        self._patten_map = {}
        for color, labels in self._colors.items():
            for label in labels:
                self._color_map[label] = color
                if len(label) > 1:
                    self._patten_map[label] = re.compile("%s=\d+" % label)

    def __getattr__(self, key):
        return getattr(self._stream, key)

    def _colorize(self, string, color=None):
        if string:
            if color is None:
                color = self._color_map.get(string)
                if color is None:
                    for key in self._color_map:
                        # looking for a test failure as LABEL: str(test)
                        if string.startswith(key + ":"):
                            segments = string.split(":")
                            label = self._colorize(segments[0] + ":",
                                                   self._color_map[key])
                            desc = ":".join(segments[1:])
                            if desc.startswith(" Failure: "):
                                desc = termcolor.colored(desc, self._color_map[key])
                            return label + desc
                    for key, key_color in self._color_map.items():
                        # looking for label=number in the summary
                        pattern = self._patten_map.get(key)
                        if pattern is not None:
                            for match in pattern.findall(string):
                                string = string.replace(match,
                                                        self._colorize(match, key_color))
            if color is not None:
                string = termcolor.colored(string, color, attrs=("bold",))
        return string

    def write(self, string):
        self._stream.write(self._colorize(string))

    def writeln(self, string=""):
        self._stream.writeln(self._colorize(string))


class YANC(Plugin):
    """Yet another nose colorer"""

    name = "yanc"

    _options = (
        ("color", "YANC color override - one of on,off [%s]", "store"),
        )

    def options(self, parser, env):
        super(YANC, self).options(parser, env)
        for name, help, action in self._options:
            env_opt = "NOSE_YANC_%s" % name.upper()
            parser.add_option("--yanc-%s" % name.replace("_", "-"),
                              action=action,
                              dest="yanc_%s" % name,
                              default=env.get(env_opt),
                              help=help % env_opt)


    def configure(self, options, conf):
        super(YANC, self).configure(options, conf)
        for name, help, dummy in self._options:
            name = "yanc_%s" % name
            setattr(self, name, getattr(options, name))
        self.color = self.yanc_color != "off" \
                         and (self.yanc_color == "on" \
                             or (hasattr(self.conf.stream, "isatty") \
                                 and self.conf.stream.isatty()))

    def begin(self):
        if self.color:
            self.conf.stream = ColorStream(self.conf.stream)

    def finalize(self, result):
        if self.color:
            self.conf.stream = self.conf.stream._stream
