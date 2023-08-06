sixfoh
======

Generates base `sixfoh <http://youtu.be/XfkDnsxc-zE>`_-encoded images for yer websites.

Installation
============

    pip install sixfoh

Usage
=====

Give sixfoh a some images to convert to base64:::

    sixfoh datauri/*.png

If no files are given, it will look for images in the current directory.

Usage with Less
---------------

Pipe your output with the ``--less``` flag and it will prepend Less variables to import into
your CSS.::

    sixfoh --less myimage.png > datauri.less

I usually slice up all my icons in Photoshop and output them into a "data-uri" folder.::

    sixfoh -L data-uri/* > datauri.less

Import it and use it:::

    @import "datauri.less";

    #Logo {
        background-image: @myimage;
    }

You do the same for Sass with the ``--scss`` flag.

Options
-------

-L
    Writes images into a group of LessCSS variables, to be included in a stylesheet or written to a .less file to be imported. (alias: --less)

-S
    Writes images into a group of Sass variables, to be included in a stylesheet or written to a .scss file to be imported. (alias: --scss)

-f
    Force output and ignore warnings.

---

image:: http://www.gifmania.co.uk/cars/3D/lowrider.gif
