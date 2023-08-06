# -*- coding: iso-8859-1 -*-
""" We have a string that has both iso-8859-1 and utf-8 characters
So we need to have a single encoded string
"""
# encoded into iso-8859-1 
special_charac_string = '[ÄÁÀÆÇÊËÉÈÎÏÍÌÐÑÕÓÒÔÖØ×ÚÙÛÜÝÞßáàâäãåæçéèêëïîíìðñôöøóõò÷ùúüûÿýþ]'

def noDoubleEncoding(chain) :
    #Do we have a double encoded string ?
    try:
        #do we have full utf-8 ?
        chain.decode('utf-8').encode('utf-8')
    except UnicodeDecodeError:
        #no we don't ; do we have full iso-8859-1 ?
        try:
            chain = chain.encode('iso-8859-15')
            return noDoubleEncoding(chain)
        except UnicodeDecodeError:
            #no we don't 
            chain=chain.decode('iso-8859-15').encode('utf-8')
            for i in special_charac_string :
                bad_char = i.decode('iso-8859-15').encode('utf-8').decode('iso-8859-15').encode('utf-8')
                good_char = i.decode('iso-8859-15').encode('utf-8')
                chain = chain.replace(bad_char, good_char)
            #apostrophes
            chain = chain.replace('\xc3\xa2\xc2\x80\xc2\x99','\xe2\x80\x99')
            #e dans l'o
            chain = chain.replace('\xc3\x85\xc2\x93','\xc5\x93')
            #euro
            chain = chain.replace('xc3\xa2\xc2\x82\xc2\xac','\xe2\x82\xac')
            return chain
    return chain
mychain = 'héhé'
noDoubleEncoding(mychain)
