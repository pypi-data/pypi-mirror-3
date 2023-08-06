============================
collective.facebook.portlets
============================

.. contents:: Table of Contents
   :depth: 2

Overview
--------

This package implements some `Facebook`_ `Social Plugins`_ as portlets for
your Plone site.

This package depends on `collective.facebook.accounts`_.

Currently, the following portlets are available:

Facebook Wall portlet
    This portlet displays the user's Facebook Wall and their News Feed.

Facebook Activity Feed portlet
    This portlet is based on the Activity Feed plugin and it has some UI
    limitations. The Activity Feed plugin displays the most interesting recent
    activity taking place on your site. Since the content is hosted by
    Facebook, the plugin can display personalized content whether or not the
    user has logged into your site. The activity feed displays stories when
    users interact with content on your site, such as like, watch, read, play
    or any custom action. Activity is also displayed when users share content
    from your site in Facebook or if they comment on a page on your site in
    the Comments box. If a user is logged into Facebook, the plugin will be
    personalized to highlight content from their friends. If the user is
    logged out, the activity feed will show recommendations from across your
    site, and give the user the option to log in to Facebook.

Don't panic
-----------

Facebook Wall portlet
^^^^^^^^^^^^^^^^^^^^^

To add a Facebook Wall portlet do the following:

- From the manage portlets screen select "Facebook Wall".
- Enter a header (if you want one).
- Choose the Facebook account to use from the drop-down.
- Enter the ID of the wall you want to be listed (e.g. plonecms).
- Enter the maximum number of entries you want the portlet to show.
- Mark the checkbox if you want only the posts made from the wall owner to be
  shown (plonecms in this case), or leave it unmarked if you want all posts no
  matter who posted them.

That's it.

Facebook Activity Feed portlet
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To add a Facebook Activity Feed portlet do the following:

- From the manage portlets screen select "Facebook Activity Feed".
- Enter a header (if you want one).
- Enter App ID/API Key of your application.
- Enter the site URL from which you want to display interesting recent
  activity (e.g. plone.org).
- Select if you want to show recommendations from across your site.
- Set the portlet width and height.
- Select the color scheme you want to use: light or dark.
- Select the link target you want to use: _blank, _top or _parent.
- Enter the border color in hexadecimal format (e.g. #ffffff).

That's it.

Screenshots
-----------

.. figure:: https://github.com/collective/collective.facebook.portlets/raw/master/wall.png
    :align: center
    :height: 582px
    :width: 263px

    Facebook Wall portlet.

.. figure:: https://github.com/collective/collective.facebook.portlets/raw/master/activity.png
    :align: center
    :height: 362px
    :width: 260px

    Facebook Activity Feed portlet.

To do list
----------

In the near future we are going to release a new version including the
following features:

`Recommendations Box portlet`_
    This portlet will be based on the Recommendations Box plugin. The
    Recommendations Box shows personalized recommendations to your users.
    Since the content is hosted by Facebook, the plugin can display
    personalized recommendations whether or not the user has logged into your
    site. To generate the recommendations, the plugin considers all the social
    interactions with URLs from your site. For a logged in Facebook user, the
    plugin will give preference to and highlight objects her friends have
    interacted with.

.. _`collective.facebook.accounts`: http://pypi.python.org/pypi/collective.facebook.accounts
.. _`Facebook`: http://www.facebook.com/
.. _`Social Plugins`: https://developers.facebook.com/docs/plugins/
.. _`Recommendations Box portlet`: https://github.com/collective/collective.facebook.portlets/issues/2

