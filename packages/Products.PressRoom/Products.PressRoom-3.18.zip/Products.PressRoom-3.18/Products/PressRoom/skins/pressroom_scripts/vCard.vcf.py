## Script (Python) "computeRelatedItems"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=find related items for an object
##

request = context.REQUEST
c = context

print 'BEGIN:VCARD'
print 'FN:%s' % c.Title()
print 'N:%s' % c.Title()
print 'ORG:%s' % c.getOrganization()
print 'ADR:%s;%s' % (c.getCity() , c.getStateOrProvince())
print 'TEL;type=WORK:%s' % c.getPhone()
print 'TEL;type=CELL:%s' % c.getCellphone()
print 'EMAIL:%s' % c.getEmail()
print 'TITLE:%s' % c.getJobtitle()
print 'NOTE:%s' % c.Description()
print 'END:VCARD'

request.RESPONSE.setHeader('Content-Type','text/x-vcard')

return printed

