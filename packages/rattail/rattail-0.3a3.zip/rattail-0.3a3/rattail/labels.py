#!/usr/bin/env python
# -*- coding: utf-8  -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2012 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU Affero General Public License as published by the Free
#  Software Foundation, either version 3 of the License, or (at your option)
#  any later version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for
#  more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################

"""
``rattail.labels`` -- Label Printing
"""

import os
import os.path
import socket
from cStringIO import StringIO

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

import edbob
from edbob.util import requires_impl


_profiles = OrderedDict()


class LabelPrinter(edbob.Object):
    """
    Base class for all label printers.

    Label printing devices which are "natively" supported by Rattail will each
    derive from this class in order to provide implementation details specific
    to the device.  You will typically instantiate one of those subclasses (or
    one of your own design) in order to send labels to your physical printer.
    """

    profile_name = None
    formatter = None

    @requires_impl()
    def print_labels(self, labels, *args, **kwargs):
        """
        Prints labels found in ``labels``.
        """

        pass


class CommandFilePrinter(LabelPrinter):
    """
    Generic :class:`LabelPrinter` subclass which "prints" labels to a file in
    the form of native printer (textual) commands.  The output file is then
    expected to be picked up by a file monitor, and finally sent to the printer
    from there.
    """

    def batch_header_commands(self):
        """
        This method, if implemented, must return a sequence of string commands
        to be interpreted by the printer.  These commands will be the first
        which are written to the file.
        """

        return None

    def batch_footer_commands(self):
        """
        This method, if implemented, must return a sequence of string commands
        to be interpreted by the printer.  These commands will be the last
        which are written to the file.
        """

        return None

    def print_labels(self, labels, output_dir=None):
        """
        "Prints" ``labels`` by generating a command file in the output folder.
        The full path of the output file to which commands are written will be
        returned to the caller.

        If ``output_dir`` is not specified, and the printer instance is
        associated with a :class:`LabelProfile` instance, then config will be
        consulted for the output path.  If a path still is not found, the
        current (working) directory will be assumed.
        """

        if not output_dir and self.profile_name:
            output_dir = edbob.config.get('rattail.labels', '%s.output_dir' % self.profile_name)
        if not output_dir:
            output_dir = os.getcwd()

        fn = '%s_%s.labels' % (socket.gethostname(),
                               edbob.local_time().strftime('%Y-%m-%d_%H-%M-%S'))
        labels_path = os.path.join(output_dir, fn)
        labels_file = open(labels_path, 'w')

        header = self.batch_header_commands()
        if header:
            print >> labels_file, '\n'.join(header)

        print >> labels_file, self.formatter.format_labels(labels)

        footer = self.batch_footer_commands()
        if footer:
            print >> labels_file, '\n'.join(footer)

        labels_file.close()
        return labels_path


class LabelFormatter(edbob.Object):
    """
    Base class for all label formatters.
    """

    format = None

    @requires_impl()
    def format_labels(self, labels, *args, **kwargs):
        """
        Formats ``labels`` and returns the result.
        """

        pass


class CommandFormatter(LabelFormatter):
    """
    Generic subclass of :class:`LabelFormatter` which generates native printer
    (textual) commands.
    """

    def label_header_commands(self):
        """
        This method, if implemented, must return a sequence of string commands
        to be interpreted by the printer.  These commands will immediately
        precede each *label* in one-up printing, and immediately precede each
        *label pair* in two-up printing.
        """

        return None

    @requires_impl()
    def label_body_commands(self):
        pass

    def label_footer_commands(self):
        """
        This method, if implemented, must return a sequence of string commands
        to be interpreted by the printer.  These commands will immedately
        follow each *label* in one-up printing, and immediately follow each
        *label pair* in two-up printing.
        """

        return None


class TwoUpCommandFormatter(CommandFormatter):
    """
    Generic subclass of :class:`LabelFormatter` which generates native printer
    (textual) commands.

    This class contains logic to implement "two-up" label printing.
    """

    @property
    @requires_impl(is_property=True)
    def half_offset(self):
        """
        The X-coordinate value by which the second label should be offset, when
        two labels are printed side-by-side.
        """

        pass

    def format_labels(self, labels):
        fmt = StringIO()

        half_started = False
        for product, quantity in labels:
            for i in range(quantity):
                if half_started:
                    print >> fmt, '\n'.join(self.label_body_commands(product, x=self.half_offset))
                    footer = self.label_footer_commands()
                    if footer:
                        print >> fmt, '\n'.join(footer)
                    half_started = False
                else:
                    header = self.label_header_commands()
                    if header:
                        print >> fmt, '\n'.join(header)
                    print >> fmt, '\n'.join(self.label_body_commands(product, x=0))
                    half_started = True

        if half_started:
            footer = self.label_footer_commands()
            if footer:
                print >> fmt, '\n'.join(footer)

        val = fmt.getvalue()
        fmt.close()
        return val
    

class LabelProfile(edbob.Object):
    """
    Represents a label printing profile.  This abstraction is used to define
    not only the physical (or otherwise?) device to which label should be sent,
    but the label formatting specifics as well.
    """

    name = None
    display_name = None
    printer_factory = None
    formatter_factory = None
    format = None

    def get_formatter(self):
        if self.formatter_factory:
            return self.formatter_factory(format=self.format)
        return None

    def get_printer(self):
        if self.printer_factory:
            return self.printer_factory(
                profile_name=self.name,
                formatter=self.get_formatter())
        return None


def init(config):
    """
    Initializes the label printing system.

    This reads label profiles from config and caches the corresponding
    :class:`LabelProfile` instances in memory.
    """

    profiles = config.require('rattail.labels', 'profiles')
    profiles = profiles.split(',')
    for key in profiles:
        key = key.strip()
        profile = LabelProfile(name=key)
        profile.display_name = config.require('rattail.labels', '%s.display' % key)
        profile.printer_factory = edbob.load_spec(
            config.require('rattail.labels', '%s.printer' % key))
        profile.formatter_factory = edbob.load_spec(
            config.require('rattail.labels', '%s.formatter' % key))
        profile.format = config.get('rattail.labels', '%s.format' % key)
        _profiles[key] = profile


def get_profile(name):
    """
    Returns the :class:`LabelProfile` instance corresponding to ``name``.
    """

    return _profiles.get(name)


def iter_profiles():
    """
    Returns an iterator over the collection of :class:`LabelProfile` instances
    which were read and created from config.
    """

    return _profiles.itervalues()
