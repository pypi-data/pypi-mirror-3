# encoding: utf-8
# Copyright (c) 2011 AXIA Studio <info@pypapi.org>
# and Municipality of Riva del Garda TN (Italy).
#
# This file is part of PyPaPi Framework.
#
# This file may be used under the terms of the GNU General Public
# License versions 3.0 or later as published by the Free Software
# Foundation and appearing in the file LICENSE.
#
# This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
# WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
#


def ApplicationConfigurator(section):
    return section

def FormRegistrator(section):
    """Registra una nuova form, letta dalla configurazione."""

    from os.path import exists, join, split
    from pkg_resources import resource_filename
    from ZConfig import ConfigurationError
    from ZConfig.components.logger.handlers import resolve
    from pypapi.db.interfaces import IRelationResolver
    from pypapi.ui.cute.interfaces import IColumn
    from pypapi.ui.cute.form import StoreFormRegistration

    try:
        # "class" è una keyword, non possiamo accedere direttamente
        # all'attributo
        section.form_class = resolve(section.__dict__['class'])
        basedir = split(resolve(section.form_class.__module__).__file__)[0]
    except Exception, e:
        raise ConfigurationError("Section %r references class %r that can't be resolved to an implementation: %s" %
                                 (section.getSectionName(), section.__dict__['class'], str(e)))

    try:
        section.data_interface = resolve(section.interface)
    except Exception, e:
        raise ConfigurationError("Section %r references interface %r that can't be resolved to an implementation: %s" %
                                 (section.getSectionName(), section.interface, str(e)))

    # In prima battuta provo a risolvere la risorsa con PkgResources se referenziata "dotted",
    # alternativamente interpreto come percorso relativo.
    # es. package.subpackage/file.ui
    try:
        tkns = section.uifile.split('/')
        pkg, file_name = tkns[0], '/'.join(tkns[1:])
        uifile = resource_filename(pkg, file_name)
    except ImportError, ValueError:
        uifile = join(basedir, section.uifile)
    if not exists(uifile):
        raise ConfigurationError("Section %r references uifile %r that can't be resolved" %
                                 (section.getSectionName(), section.uifile))

    section.uifile = uifile

    section.form_registration = StoreFormRegistration(section.form_class, section.data_interface,
                                                      section.uifile, name=section.getSectionName(),
                                                      title=section.title,
                                                      primary=section.primary,
                                                      form_source=section.formsource)
    for model in section.models:
        name = model.getSectionName()
        resolver = IRelationResolver(section.form_registration.form_class.interface)
        interface = resolver.resolveInterface(name)
        cols_obj = []
        for col_spec in model.columns:
            col_name = col_spec.getSectionName()
            try:
                column = IColumn(interface.get(col_name))
            except Exception, e:
                raise ConfigurationError("Model %r of Form %r tried to create column %r: %s" % \
                                        (name, section.getSectionName(), col_name, str(e)))
            flags = {}
            if col_spec.title is not None:
                column.title = col_spec.title
            if col_spec.description is not None:
                column.description = col_spec.description
            if col_spec.enabled is not None:
                flags['enabled'] = col_spec.enabled
            if col_spec.editable is not None:
                flags['editable'] = col_spec.editable
            if col_spec.checkable is not None:
                flags['checkable'] = col_spec.checkable
            column._flags.update(flags)
            cols_obj.append(column)
        section.form_registration.setModel(cols_obj, name)
    return section

