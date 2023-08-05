================
cubicweb.ajax.js
================
.. module:: cubicweb.ajax.js

.. function:: Deferred

dummy ultra minimalist implementation of deferred for jQuery

returns true if `url` is a mod_concat-like url
(e.g. http://..../data??resource1.js,resource2.js)

decomposes a mod_concat-like url into its corresponding list of
resources' urls
>>> _listResources('http://foo.com/data/??a.js,b.js,c.js')
['http://foo.com/data/a.js', 'http://foo.com/data/b.js', 'http://foo.com/data/c.js']

.. function:: function loadAjaxHtmlHead(response)

inspect dom response (as returned by getDomFromResponse), search for
a <div class="ajaxHtmlHead"> node and put its content into the real
document's head.
This enables dynamic css and js loading and is used by replacePageChunk

.. function:: ajaxFuncArgs(fname, form, *args)

extend `form` parameters to call the js_`fname` function of the json
controller with `args` arguments.

.. function:: loadxhtml(url, form, reqtype='get', mode='replace', cursor=false)

build url given by absolute or relative `url` and `form` parameters
(dictionary), fetch it using `reqtype` method, then evaluate the
returned XHTML and insert it according to `mode` in the
document. Possible modes are :

   - 'replace' to replace the node's content with the generated HTML
   - 'swap' to replace the node itself with the generated HTML
   - 'append' to append the generated HTML to the node's content

If `cursor`, turn mouse cursor into 'progress' cursor until the remote call
is back.

.. function:: loadRemote(url, form, reqtype='GET', sync=false)

Asynchronously (unless `async` argument is set to false) load an url or path
and return a deferred whose callbacks args are decoded according to the
Content-Type response header. `form` should be additional form params
dictionary, `reqtype` the HTTP request type (get 'GET' or 'POST').

.. function:: _(message)

emulation of gettext's _ shortcut

.. function:: _loadDynamicFragments(node)

finds each dynamic fragment in the page and executes the
the associated RQL to build them (Async call)

.. function:: unregisterUserCallback(cbname)

unregisters the python function registered on the server's side
while the page was generated.

.. function:: buildWysiwygEditors(parent)

XXX: this function should go in edition.js but as for now, htmlReplace
references it.

replace all textareas with fckeditors.

.. function:: stripEmptyTextNodes(nodelist)

takes a list of DOM nodes and removes all empty text nodes

.. function:: getDomFromResponse(response)

convenience function that returns a DOM node based on req's result.
XXX clarify the need to clone

.. function:: reloadCtxComponentsSection(context, actualEid, creationEid=None)

reload all components in the section for a given `context`.

This is necessary for cases where the parent entity (on which the section
apply) has been created during post, hence the section has to be reloaded to
consider its new eid, hence the two additional arguments `actualEid` and
`creationEid`: `actualEid` is the eid of newly created top level entity and
`creationEid` the fake eid that was given as form creation marker (e.g. A).

You can still call this function with only the actual eid if you're not in
such creation case.

.. function:: reload(domid, registry, formparams, *render_args)

`js_render` based reloading of views and components.