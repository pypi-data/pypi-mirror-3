===========
Marrja Mail
===========

Marrja mail is a small module that brings together Jinja2 and marrow.mailer to 
easily send emails rendered from templates. You supply a template name with 
no extension and it will try it with .txt and .htm from the 'email_templates' directory inside your package
(this is customisable) and attach the ones that are found.

Basic usage:
::
    #Once per applicaton
    from marrja_mail import MarrjaMailer

    email_sender = MarrjaMailer(__name__, server='smtp.myserver.com', username='user@myserver.com',
                                password='mypass', default_sender='my_sender@myserver.com')
    
    #Then to send email
    email_sender.send('user@send.to', 'template_file', 'subject line' , var_for=jinja_template)

TODO:
=====

- Add support for testing that dumps out the rendered template to a dir
- Expose more configuration options for marrow.mailer
- Write better docs

More info @ https://github.com/Dotnetwill/marrja_mail
