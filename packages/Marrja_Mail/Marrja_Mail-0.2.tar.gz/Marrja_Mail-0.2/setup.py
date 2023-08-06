from distutils.core import setup

setup(
    name='Marrja_Mail',
    author='Will Charles',
    author_email='will@will.yt',
    version='0.2',
    packages=['marrja_mail',],
    license='BSD',
    url='https://github.com/Dotnetwill/marrja_mail/',
    description='Small wrapper for marrow.mailer to use Jinja2 templates and automatically send html and plain text emails.',
    long_description= open('README').read(),
    install_requires=[
        "Jinja2>=2.6",
        "marrow.mailer>=4.0.0",
        ]
    )
