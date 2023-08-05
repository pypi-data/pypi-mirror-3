## Controller Python Script "imagerepository_addKeywords"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##title=
##parameters=paths=None,subject_keywords=None,subject_existing_keywords=None

if paths is None:
    return state.set(portal_status_message="No images selected.")

if subject_keywords is None:
    subject_keywords = []

if subject_existing_keywords is None:
    subject_existing_keywords = []

new_subjects = tuple(subject_keywords+subject_existing_keywords)

for path in paths:
    obj = context.restrictedTraverse(path)
    subjects = obj.Subject() + new_subjects
    # make unique
    subjects = tuple(dict([(x, None) for x in subjects]).keys())
    obj.setSubject(subjects)
    obj.reindexObject()

portal_status_message="Keywords '%s' added." % ", ".join(new_subjects)

return state.set(portal_status_message=portal_status_message)
