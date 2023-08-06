StickyList is a simple product that enables displaying a selection of
links.  For example, to embed the contents of a StickList in a page
use something like

  <metal:block tal:define="xyz python:request.set('stickylist', settings['some_stickylist'])">
     <span metal:use-macro="context/stickylist_macros/macros/listing" />
   </metal:block>
