## Script (Python) "isEmail"
##bind container=container                                                                                                          
##bind context=context                                                                                                              
##bind namespace=                                                                                                                   
##bind script=script                                                                                                                
##parameters=toCheck
##                                                                                                                                   

return context.portal_registration.isValidEmail(toCheck)

