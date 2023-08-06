Overview
========

KSS (Kinetic Style Sheets) for Archetypes

This product gives generic KSS support to Archetypes. It depends on the product
"kss.core" and "plone.app.kss".

Features implemented
--------------------

- In-place field validation. In the edit field, when a field area is left,
  the field gets validated and field error  message is displayed.

  This must be implemented for each field type individually. At the moment,
  only the stringField is done. To test, go to a mandatory field like Title,
  delete its value and try to leave it.

- In-place form submission. When the Save button is pressed, we first validate
  the entire form from the page. If we have an error, we stay in the page and
  display the portal status message, plus every field error message. If there is
  no error, we resubmit the form.

  The form resubmission may be implemented in a more effective way in the future,
  together with the total rewrite of AT's current submission scripts.

  Missing/TODOS:

     - Implement field validation for all the other field types.

     - There is a lingering UnicodeDecodeError during the rendering of document_view.
       UPDATE. The problem is related to Zope 2.10 and/or AT,
       but since I can't run AT trunk on Zope 2.9, I will need to provide a fix...

     - The popups for leaving the edit region are not hooked in. This means that sometimes
       the "do you want to leave the page" popup comes in where it should not be.

     - The loading of the kupu editor is done with a simple hack, it seems to
       be no clean way in javascript to find when the iframe has been loaded,
       some more complex hack is needed for this that works on all browsers
       and is reliable in all the cases.

KSS extensions defined for general purpose use
----------------------------------------------

- A generic macro replacer server action

- client action for submitting to an url

- client action for submitting the current form
