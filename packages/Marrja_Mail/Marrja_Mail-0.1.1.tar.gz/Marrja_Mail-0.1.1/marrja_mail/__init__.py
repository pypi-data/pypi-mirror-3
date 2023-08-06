# -*- coding: utf-8 -*-
from jinja2 import Environment, PackageLoader, TemplateNotFound
from marrow.mailer import Mailer, Message
import logging


class Config(object):
    """
        Marrja mailer configuration
    """
    EMAIL_HOST = 'localhost'
    EMAIL_USERNAME = ''
    EMAIL_PWD = ''
    EMAIL_PORT = 25
    EMAIL_SENDER = ''
    EMAIL_TEMPLATE_DIR = ''
    LOGGER_NAME = 'marrja'
    LOGGER_LEVEL = logging.NOTSET


class MarrjaMailer(object):
    """
    Main wrapper around marrow.mailer and jinja2.

    This should be run once in the global scope as it inits marrow and Jinja
    """
    def __init__(self, pkg_name, config=None,  server='localhost',
                  username=None, password=None, email_port=25,
                  default_sender=None, template_dir='email_templates'):
        """
        Can be created by passing the configuration for sending a mail,
        pkg_name is required so we can find your email templates but depending
        on your configuration server, username, password may not be required.

        Only server, username, password, port, sender and template_dir can be
        configured.  If you need to change other settings such as logging.
        Please pass a Config object.
        """
        if not config is None:
            self._config = config
        else:
            self._config = Config()
            if not server is None:
                self._config.EMAIL_HOST = server
            if not username is None:
                self._config.EMAIL_USERNAME = username
            if not password is None:
                self._config.EMAIL_PWD = password
            if not email_port is None:
                self._config.EMAIL_PORT = email_port
            if not default_sender is None:
                self._config.EMAIL_SENDER = default_sender
            self._config.EMAIL_TEMPLATE_DIR = template_dir

        #Init log
        self._log = logging.getLogger(self._config.LOGGER_NAME)
        self._log.setLevel(self._config.LOGGER_LEVEL)
        console_handler = logging.StreamHandler()
        self._log.addHandler(console_handler)

        #Init Jinja
        self._jinja_env = Environment(loader=PackageLoader(pkg_name,
            self._config.EMAIL_TEMPLATE_DIR))

        #Init Mailer
        self._mailer = Mailer(dict(
            transport = dict(
                use = 'smtp',
                host = self._config.EMAIL_HOST,
                username = self._config.EMAIL_USERNAME,
                password = self._config.EMAIL_PWD,
                port = self._config.EMAIL_PORT),
            manager = dict()))

        self._mailer.start()

    def send_email(self, send_to, template, subject, **kwargs):
        """
            Sends an email to the target email with two types
                1) HTML
                2) Plain

            We will try the template with .htm for rich and .txt for plain,
            if one isn't found we will only send the
            correct one.

            Both will rendered with Jinja2
        """

        message = Message(author=self._config.EMAIL_SENDER, to=send_to)
        message.subject = subject

        try:
            rendered_template = self._jinja_env.get_template(template + '.txt')
            message.plain = rendered_template.render(**kwargs)
            self._log.debug('Plain text email is %s', message.plain)
        except TemplateNotFound:
            self._log.debug('txt template not found')

        try:
            rendered_template = self._jinja_env.get_template(template + '.htm')
            message.rich = rendered_template.render(**kwargs)
            self._log.debug('html email generated %s' % message.rich)
        except TemplateNotFound:
            self._log.debug('html template not found')

        self._mailer.send(message)
