## Script (Python) "create_email"
##bind container=container                                                                                                          
##bind context=context                                                                                                              
##bind namespace=                                                                                                                   
##bind script=script                                                                                                                
##parameters=sender='',to='',cc='',bcc='',subject='',body=''
##                                                                        

request = context.REQUEST
session = request.SESSION
session['setup_email'] = True
session['sender'] = sender
session['to'] = to
session['cc'] = cc
session['bcc'] = bcc
session['title'] = subject
session['body'] = body

request.RESPONSE.redirect(context.absolute_url() + '/createObject?type_name=Email+message')
