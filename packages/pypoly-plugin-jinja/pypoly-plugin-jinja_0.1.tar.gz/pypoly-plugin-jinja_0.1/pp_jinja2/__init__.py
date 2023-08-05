import pkg_resources
import types
import logging
import os
import sys
import copy

import jinja2

import pypoly
from pypoly.component import Component
from pypoly.component.plugin import TemplatePlugin
from pypoly.content.template import PyPolyHandler
from pypoly.content.template import TemplateConfig, TemplateOutput
from pypoly.content.webpage import CSS


class Main(Component):
    def init(self):
        pass

    def start(self):
        pypoly.plugin.register(TemplateJinja2)

class TextTemplateOutput(TemplateOutput):
    """

    """
    text = None
    def __init__(self, **values):
        self.text = None

        self.update(**values)

    def generate(self, *args, **kargs):
        """
        """
        if self.text != None:
            options = {'pypoly' : PyPolyHandler()}
            kargs.update(options)
            return jinja2.Markup(self.text.render(*args, **kargs))

    def render(self, *args, **kargs):
        """
        """
        if self.text != None:
            options = {'pypoly' : PyPolyHandler()}
            kargs.update(options)
            return str(self.text.render(*args, **kargs))

    def update(self, **options):
        """
        This function updates the class params

        :param options:
        :type options: dict
        """
        if type(options) != types.DictType:
            return -1

        for key, value in options.iteritems():
            # only set a value if it exists in the class
            try:
                if not callable(getattr(self, key)):
                    if type(getattr(self, key)) == type(value):
                        setattr(self, key, value)
                    elif type(getattr(self, key)) == types.NoneType:
                        setattr(self, key, value)
            except:
                continue
        return 0

class WebTemplateOutput(TemplateOutput):
    """

    """
    javascript = []
    xml = None
    css = None
    def __init__(self, **values):
        self.css = CSS()
        self.javascript = []
        #: this is the template
        self.xml = None

        self.update(**values)

    def append(self, obj):
        """
        This appends the values of a TemplateOutput object to an other.

        :param obj: this is a TemplateOutput object
        :type obj: TemplateOutput
        """
        self.css.append(obj.css)
        self.javascript.append(obj.javascript)

    def generate(self, *args, **kargs):
        """
        """
        if self.xml != None:
            options = {'pypoly' : PyPolyHandler()}
            kargs.update(options)
            return jinja2.Markup(self.xml.render(*args, **kargs))

    def render(self, *args, **kargs):
        """
        """
        if self.xml != None:
            options = {'pypoly' : PyPolyHandler()}
            kargs.update(options)
            return self.xml.render(*args, **kargs).encode("utf-8")

    def update(self, **options):
        """
        This function updates the class params

        :param options:
        :type options: dict
        """
        if type(options) != types.DictType:
            return -1

        for key, value in options.iteritems():
            # only set a value if it exists in the class
            try:
                if not callable(getattr(self, key)):
                    if type(getattr(self, key)) == type(value):
                        setattr(self, key, value)
                    elif type(getattr(self, key)) == types.NoneType:
                        setattr(self, key, value)
            except:
                continue
        return 0

class XMLTemplateOutput(TemplateOutput):
    """

    """
    xml = None
    def __init__(self, **values):
        self.xml = None

        self.update(**values)

    def generate(self, *args, **kargs):
        """
        """
        if self.xml != None:
            options = {'pypoly' : PyPolyHandler()}
            kargs.update(options)
            return jinja2.Markup(self.xml.render(*args, **kargs))

    def render(self, *args, **kargs):
        """
        """
        if self.xml != None:
            options = {'pypoly' : PyPolyHandler()}
            kargs.update(options)
            return str(self.xml.render(*args, **kargs))

    def update(self, **options):
        """
        This function updates the class params

        :param options:
        :type options: dict
        """
        if type(options) != types.DictType:
            return -1

        for key, value in options.iteritems():
            # only set a value if it exists in the class
            try:
                if not callable(getattr(self, key)):
                    if type(getattr(self, key)) == type(value):
                        setattr(self, key, value)
                    elif type(getattr(self, key)) == types.NoneType:
                        setattr(self, key, value)
            except:
                continue
        return 0

class TemplateJinja2(TemplatePlugin):
    #: the default template to load
    default = ''
    #: the default style
    style = ''

    def __init__(self, templates):
        TemplatePlugin.__init__(self, templates)

        # set all values to the defaults
        self.default = ''
        self.style = ''
        self.templates = templates

        #: initialize the xml/html template environment
        self._environment_xml = jinja2.Environment(
            loader=jinja2.FileSystemLoader(
                [
                    os.path.join(
                        pypoly.config.get_pypoly('template.path', None),
                        'jinja2'
                    ),
                    pkg_resources.resource_filename(
                        "pp_jinja2",
                        "templates",
                    )
                ],
                encoding='utf-8'
            ),
            autoescape=True
        )

        #: initialize the text template environment
        self._environment_text = jinja2.Environment(
            loader=jinja2.FileSystemLoader(
                [
                    os.path.join(
                        pypoly.config.get_pypoly('template.path', None),
                        'jinja2'
                    ),
                    pkg_resources.resource_filename(
                        "pp_jinja2",
                        "templates",
                    )
                ],
                encoding='utf-8'
            )
        )

        self._load_web_config(
            'jinja2',
            self.templates
        )

    def load_text_module(self, module_name = None, *args):
        """
        This function loads the template files for the modules

        :param filename: the filename of the template file
        :type filename: String
        :param module: the module name
        :type module: String
        :return: a TemplateOutput object
        """
        name = pypoly.session.get_pypoly('template.name', 'default')

        try:
            tmp_path = os.path.join(
                name,
                'module',
                module_name,
                'text'
            )

            pypoly.locale.get_template_lang(tmp_path)

            template = self._environment_text.get_template(
                os.path.join(
                    tmp_path,
                    *args
                )  + ".jinja"
            )

        except BaseException, inst:
            tmp_path = os.path.join(
                'default',
                'module',
                module_name,
                'text'
            )
            template = self._environment_text.get_template(
                os.path.join(
                    tmp_path,
                    *args
                ) + ".jinja"
            )

        return TextTemplateOutput(text = template)

    def load_text_pypoly(self, *args):
        """
        This function loads a web template for PyPoly.

        :param filename: the filename of the template file
        :type filename: String
        :since: 0.1
        """
        name = pypoly.session.get_pypoly(
            'template.name',
            pypoly.config.get_pypoly(
                'template.default',
                None
            )
        )
        if name not in self._web_config_pypoly:
            name = 'default'
        pypoly.log.debug('template' + name)

        try:
            tmp_path = os.path.join(
                name,
                'pypoly',
                'text'
            )
            template = self._environment_text.get_template(
                os.path.join(
                    tmp_path,
                    *args
                ) + ".jinja"
            )

        except BaseException, inst:
            pypoly.log.debug(inst)
            tmp_path = os.path.join(
                'default',
                'pypoly',
                'text'
            )
            template = self._environment_text.get_template(
                os.path.join(
                    tmp_path,
                    *args
                ) + ".jinja"
            )

        pypoly.log.debug(self._web_config_pypoly[name])
        return TextTemplateOutput(text = template)

    def load_web_from_string(self, source):
        template = self._environment_xml.from_string(source)
        return WebTemplateOutput(xml = template)

    def load_web_module(self, module_name = None, *args):
        """
        This function loads the template files for the modules

        :param filename: the filename of the template file
        :type filename: String
        :param module: the module name
        :type module: String
        :return: a TemplateOutput object
        """
        name = pypoly.session.get_pypoly(
            'template.name',
            pypoly.config.get_pypoly(
                'template.default',
                None
            )
        )
        style = pypoly.session.get_pypoly('template.style', 'default')

        if not name in self._web_config_pypoly:
            name = 'default'

        module_name = module_name.lower()

        try:
            tmp_path = os.path.join(
                name,
                'module',
                module_name,
                'web'
            )

            pypoly.locale.get_template_lang(tmp_path)

            template = self._environment_xml.get_template(
                os.path.join(
                    tmp_path,
                    *args
                )  + ".htmljinja"
            )

        except BaseException, inst:
            tmp_path = os.path.join(
                'default',
                'module',
                module_name,
                'web'
            )
            template = self._environment_xml.get_template(
                os.path.join(
                    tmp_path,
                    *args
                ) + ".htmljinja"
            )

        return WebTemplateOutput(xml = template)

    def load_web_pypoly(self, *args):
        """
        This function loads a web template for PyPoly.

        :param filename: the filename of the template file
        :type filename: String
        :since: 0.1
        """
        name = pypoly.session.get_pypoly(
            'template.name',
            pypoly.config.get_pypoly(
                'template.default',
                None
            )
        )
        style = pypoly.session.get_pypoly('template.style', 'default')
        if name not in self._web_config_pypoly:
            name = 'default'
        pypoly.log.debug('template' + name)

        template = None
        try:
            tmp_path = os.path.join(
                name,
                'pypoly',
                'web'
            )
            template = self._environment_xml.get_template(
                os.path.join(
                    tmp_path,
                    *args
                ) + ".htmljinja"
            )

        except BaseException, inst:
            pypoly.log.debug(inst)
            tmp_path = os.path.join(
                'default',
                'pypoly',
                'web'
            )
            template = self._environment_xml.get_template(
                os.path.join(
                    tmp_path,
                    *args
                ) + ".htmljinja"
            )

        pypoly.log.debug(self._web_config_pypoly[name])
        output = WebTemplateOutput(xml = template)
        if style in self._web_config_pypoly[name].css:
            output.update(css = self._web_config_pypoly[name].css[style])

        return output

    def load_xml_module(self, module_name = None, *args):
        """
        This function loads the template files for the modules

        :param filename: the filename of the template file
        :type filename: String
        :param module: the module name
        :type module: String
        :return: a TemplateOutput object
        """
        name = pypoly.session.get_pypoly('template.name', 'default')

        try:
            tmp_path = os.path.join(
                name,
                'module',
                module_name,
                'xml'
            )

            pypoly.locale.get_template_lang(tmp_path)

            template = self._environment_xml.get_template(
                os.path.join(
                    tmp_path,
                    *args
                )  + ".htmljinja"
            )

        except BaseException, inst:
            tmp_path = os.path.join(
                'default',
                'module',
                module_name,
                'xml'
            )
            template = self._environment_xml.get_template(
                os.path.join(
                    tmp_path,
                    *args
                ) + ".htmljinja"
            )

        return XMLTemplateOutput(xml = template)

    def load_xml_pypoly(self, *args):
        """
        This function loads a web template for PyPoly.

        :param filename: the filename of the template file
        :type filename: String
        :since: 0.1
        """
        name = pypoly.session.get_pypoly(
            'template.name',
            pypoly.config.get_pypoly(
                'template.default',
                None
            )
        )
        style = pypoly.session.get_pypoly('template.style', 'default')
        if name not in self._web_config_pypoly:
            name = 'default'
        pypoly.log.debug('template' + name)

        try:
            tmp_path = os.path.join(
                name,
                'pypoly',
                'xml'
            )
            template = self._environment_xml.get_template(
                os.path.join(
                    tmp_path,
                    *args
                ) + ".htmljinja"
            )

        except BaseException, inst:
            pypoly.log.debug(inst)
            tmp_path = os.path.join(
                'default',
                'pypoly',
                'xml'
            )
            template = self._environment_xml.get_template(
                os.path.join(
                    tmp_path,
                    *args
                ) + ".htmljinja"
            )

        pypoly.log.debug(self._web_config_pypoly[name])
        output = XMLTemplateOutput(xml = template)
        if style in self._web_config_pypoly[name].css:
            output.update(css = self._web_config_pypoly[name].css[style])

        return output

