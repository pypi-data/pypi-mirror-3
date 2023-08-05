# CHANGES

## 0.3

* The core logic isn't in the project skeleton anymore. This allow you to 
update Clay whitout having to recreate your projects.

* Bugfix: Non-utf8 content now is handled correctly.

* Bugfix: Fix pyton package


## 0.4

* Added a per-project settings file (settings.json)


## 0.5

* Added a list of all generated views at `_index.html`.


## 0.6

* Static file processors:
    - less (requires node and less).
    - scss (Best known as Sass 3).
    - cleverCSS (*.ccss).
    - coffeescript (requires node and less).

* A default "not found" page.

* A really nice default style for the list of views and "not found" pages.


## 0.7

* Markdown Jinja extension. As a preprocessor (for *.md and *.markdown files) and as a tag ({% markdown %}{% endmarkdown %}). All interesting python-markdown extensions are activated.
Now you can use Clay to make documentation :).

