## Script (Python) "contentpanels_config"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=pageIndex=0, panelIndex=0, columnIndex=0, pageTitle='',  panelObjectPath='', panelObjectViewlet='default_viewlet', panelSkin='defaultPorletWrapper', toPage=-1, toColumn=-1, toPanel=-1
##title=edit the content panels config data

request = container.REQUEST
RESPONSE =  request.RESPONSE

pageIndex=int(pageIndex)
columnIndex=int(columnIndex)
panelIndex=int(panelIndex)
toPage=int(toPage)
toColumn=int(toColumn)
toPanel=int(toPanel)

if request.has_key('addColumn'):
  context.addColumn(pageIndex=pageIndex, columnIndex=columnIndex)
elif request.has_key('addPage'):
  pageIndex = context.addPage(pageIndex=pageIndex)
elif request.has_key('deletePage'):
  pageIndex = context.deletePage(pageIndex=pageIndex)
  pageIndex = pageIndex > 0 and pageIndex - 1 or 0
elif request.has_key('deleteColumn'):
  context.deleteColumn(pageIndex=pageIndex, columnIndex=columnIndex)
elif request.has_key('deletePanel'):
  context.deletePanel(pageIndex=pageIndex, columnIndex=columnIndex, panelIndex=panelIndex)
elif request.has_key('movePage'):
  context.movePage(pageIndex, toPage)
elif request.has_key('moveColumn'):
  context.moveColumn(pageIndex, columnIndex, toColumn)
elif request.has_key('movePanel'):
  context.movePanel(pageIndex, columnIndex, panelIndex, toColumn, toPanel)

URL = '%s/contentpanels_config_form?pageIndex=%d' % (context.absolute_url(), pageIndex)

if request.has_key('addPanel'):
  relativePath = context.toRelativePath(panelObjectPath)
  viewletOptions = {}

  for k,v in request.form.items():
       if k not in ['buttonPreview', 'cpPath', 'addPanel', 'pageIndex', 'columnIndex', "panelIndex", "panelObjectPath", "panelObjectViewlet", "panelSkin", "buttonSelect"]:
           viewletOptions[k] = v

  if request['addPanel'] == 'edit':
      context.changePanel(pageIndex=pageIndex,
                   columnIndex=columnIndex,
                   panelIndex=panelIndex,
                   panelObjectPath=relativePath,
                   panelObjectViewlet=panelObjectViewlet,
                   panelSkin=panelSkin,
                   viewletOptions = viewletOptions,)
  else:
      context.addPanel(pageIndex=pageIndex, 
                   columnIndex=columnIndex, 
                   panelIndex=panelIndex,
                   panelObjectViewlet=panelObjectViewlet, 
                   panelObjectPath=relativePath, 
                   panelSkin=panelSkin, 
                   viewletOptions = viewletOptions,)

  context.reindexObject()
  request.RESPONSE.setHeader('Content-Type', 'text/html')
  return """<html><head><script type="text/javascript">window.opener.location.href='%s'; window.close(); </script></head><body></body></html>""" % URL

context.reindexObject()
request.RESPONSE.redirect(URL)

