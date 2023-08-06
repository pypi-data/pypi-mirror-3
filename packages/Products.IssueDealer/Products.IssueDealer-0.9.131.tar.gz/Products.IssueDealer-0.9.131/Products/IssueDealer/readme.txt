What is it?

  The Issue Dealer is a tool for managing issues, currently
  it focuses on the information in, and structuring of, issues.

  It can be used as a generic issue tracker, a knowledge management
  tool, a weblog or an outliner.

  It also contains an experimental framework for creating content
  classes through the web, access it via issuedealerinstance/laf

  It has been tested to work with Zope 2.9 - 2.13 but is believed to
  work with older versions of Zope as well.

Why have you created it?

  Initially the company I work for (Nidelven IT) needed a tool that
  could help organize and share information.  It started as a basic
  'folder and document' archive on my computer, now it's evolving
  into an advanced (but simple to use!) information management and
  distribution system.

Why is it free?

  We give it away for free because you get to try it out, and
  then if you need customizing or hosting of it, that's where
  we can offer you a service.

  We'd like to start a community around this application eventually,
  so if you think this is an interesting application, get in touch and
  maybe we can do something together.

How are you developing it?

  We're developing this tool 'as we go' and will be adding to it as we
  figure out what's needed and what's simple; we're not using a specific
  development process on it yet, we'll start using XP when others find
  it interesting and join in on the development.

What happens next?

  The focus for the 1.0 release is to make the application manage
  information, the focus for the 2.0 release is (for now) to make the
  application handle contacts and processes.

Is it secure?

  Yes and no.  It is has been built to be secure for outsiders, but
  once someone has access to viewing, adding, editing or something
  else, you should assume that they can access any part of the system.

Does it scale?

  Probably not.  This product is primarily focused on small groups of
  people, and hasn't been stress-tested with big groups of users.

What are the main features?

  The main features of the Issue Dealer are:

    Issue Tracking

      - Tracks issues which can be of the type goal, idea, info,
        problem, question and undefined

      - Can notify users of new issues or changes to issues assigned
        to them

    Information management

      - Enables structuring and searching of data

      - Advanced search, with saved searches (filters)

    Publishing

      - A weblog publisher

        - Can publish issues to other weblogs

      - A local weblog publisher

        - Acts as a weblog server

        - Supports Atom-enabled clients

        - Enables many forms of subscriptions, through Atom as well as
          email

      - WebDAV publisher

        - Can publish issues along with their images to WebDAV-enabled
          servers

      - FAQ publisher

        - Generates FAQs based on questions and solutions

      - Category publisher

        - Publishes issues as categories; these categories can in turn
          be used in feedback forms on websites, as the publisher
          accepts incoming issues as well

      - Tree publisher

        - Publishes and issues and its contents to a given URL as a
          static page

    Advanced HTML/CSS interface

      - Many different views of issues in simple interfaces making the
        issues easy to work with

      - WYSIWYG editing with support for images

TODO:

  - Implement advanced regexp search.  


