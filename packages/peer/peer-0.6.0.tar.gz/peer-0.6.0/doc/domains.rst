
Domain management
=================

Basically, a domain in this system consists of the string representation of
a DNS domain, and a reference to a user, the owner of the domain. It also
has a *verified* mark, the semantics of which will be explained below. Any
user can have any number of domains.

In the user profile view, accesible by clicking on the button labelled with
the username in the upper right corner, there is a link labelled
**add domain**. Following it, the user is presented with a form to add a
new domain. In this form the user simply has to fill in the name of the
domain, and click on the *add domain* button.

Adding a domain is not enough to use it in the system. PEER has to verify
that the user has actual management rights over that domain in the DNS
environment. To do this, after the user has submitted the domain creation
form, it presents her with a page in which there is a special string, and a
button labelled *verify ownership*. The user has to create a resource named
with that string in the root of the HTTP service for that domain. Once she
creates it, she has to click the **verify domain** button. The system then
sends an HTTP GET request to
``http://<the new domain>/<the verification string>``, and only when it gets
a 200 OK response code, it considers the domain (and marks it as) verified.

A user can see a list of all her domains in her user profile view, where she
can also verify her yet unverified domains or remove them.

Every entity in PEER is associated with a domain object. This is used in
some validators that check that some parts of the entity's metadata (such as
endpoints) belongs to its entity's domain.
