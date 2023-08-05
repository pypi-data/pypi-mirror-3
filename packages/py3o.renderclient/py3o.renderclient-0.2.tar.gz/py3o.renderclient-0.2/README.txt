Overview
========

py3o.renderclient is a client library that can be used to easily integrate with
the py3o.renderserver to transform LibreOffice/OpenOffice documents into PDF.

This architecture was designed to avoid the pyuno dependency in the client program.
Depending on pyuno is really complicated on some plateforms.

Using this client you can leverage a distante (or local) renderserver to transform
documents for you with nearly no code.

Example
=======

Here is a sample minimalistic client that considers you have a renderserver running
on localhost::

    from py3o.renderclient import RenderClient

    client = RenderClient('localhost', 8994)
    client.login('toto', 'plouf')
    client.render('py3o_example.odt', 'py3o_example.pdf', 'pdf')

For the moment the login/password phase is not checked by the server, but we aim to
add an authentication layer in the future.

Status
======

Since we are still in pre 1.0 releases we may change the API and add more functionnalities,
now is a good time to give feed-back and feature requests.

