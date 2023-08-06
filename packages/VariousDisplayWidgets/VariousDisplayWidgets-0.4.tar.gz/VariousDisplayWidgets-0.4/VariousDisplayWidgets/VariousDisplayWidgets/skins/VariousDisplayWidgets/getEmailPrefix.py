## Script (Python) "getEmailPrefix"
##bind container=container                                                                                                          
##bind context=context                                                                                                              
##bind namespace=                                                                                                                   
##bind script=script                                                                                                                
##parameters=
##                                                                                                                                   

if 'Email message' in map(lambda x: x.content_meta_type, context.allowedContentTypes()):
    return context.absolute_url() + '/create_email?to='
else:
    return 'mailto:'
