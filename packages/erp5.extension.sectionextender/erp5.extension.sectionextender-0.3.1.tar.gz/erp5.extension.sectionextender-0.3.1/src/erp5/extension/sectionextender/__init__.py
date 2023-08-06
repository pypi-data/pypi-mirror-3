# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2012 Apkawa. All Rights Reserved.
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
# Copyright (c) 2006-2008 Zope Corporation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).    A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

import re


def _get_extended_section_by_source(section_extender_lines):
    """
    From the 'buildout' section, get all the sections, which are going
    to be extended using this extension, along with their target and
    source options.

    @param section_extender_lines: section extender lines
    @type section_extender_lines: str
    @rtype: list
    @returns: target section, target option and source option for all sections
    """
    section_extender_re = re.compile('\s*([^:]+):([^\s]+)\s*([^\s]+)\s*$')
    extended_section_list = []

    for section_extender_line in section_extender_lines.splitlines():
        if not section_extender_line:
            continue

        try:
            extended_section = section_extender_re.match(
                section_extender_line).groups()
        except AttributeError:
            continue

        extended_section_list.append(extended_section)

    return extended_section_list


def ext(buildout):
    """
    This extension allows any sections in 'parts' to define a (source)
    option whose value will be added to the (target) option of a
    (target) section, thus allowing to extend a section from another
    one.

    Sections to be extended are specified in the 'buildout' section
    following this format (there could be many lines:

    section-extender =
        TARGET-SECTION:TARGET-OPTION SOURCE-OPTION
        TARGET-SECTION2:TARGET-OPTION2 SOURCE-OPTION2
        ...

    For example, the following buildout configuration snippet allows to
    extend the 'supervisor-instance' for the option 'programs' and can
    be found in any sections as 'supervisor-program':

    [buildout]
    extensions = erp5.extension.sectionextender

    section-extender =
        supervisor-instance:programs supervisor-program
        test1-section:test1-section-option test1-source-option

    @param buildout: buildout configuration sections and their options
    @type buildout: dict
    """
    # Get the sections to be extended otherwise do nothing
    if 'section-extender' not in buildout['buildout']:
        return

    extended_section_list = _get_extended_section_by_source(
        buildout['buildout']['section-extender'])

    for part in buildout['buildout']['parts'].strip().split():
        if not part:
            continue

        for target_section, target_option, source_option in extended_section_list:
            if source_option in buildout[part]:
                # Set the value if it has never been set before
                if target_option not in buildout[target_section]:
                    buildout[target_section][target_option] = buildout[part][source_option]
                # Otherwise, just add on a new line
                else:
                    buildout[target_section][target_option] += '\n' + buildout[part][source_option]
