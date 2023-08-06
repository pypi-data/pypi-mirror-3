## Script (Python) "isURI"
##bind container=container                                                                                                          
##bind context=context                                                                                                              
##bind namespace=                                                                                                                   
##bind script=script                                                                                                                
##parameters=toCheck
##                                                                                                                                   

known_uri_prefixes = ('http://', 'https://', 'mailto:', 'ftp://')

for prefix in known_uri_prefixes:
    if toCheck.startswith(prefix): return True
else:
    return False
