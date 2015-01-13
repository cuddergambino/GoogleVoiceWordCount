from googlevoice import Voice
import sys
import BeautifulSoup
import re
import operator
import collections
from firebase import firebase

def extractsms(htmlsms) :
    """
    extractsms  --  extract SMS messages from BeautifulSoup tree of Google Voice SMS HTML.

    Output is a list of dictionaries, one per message.
    """
    #max = 50
    msgitems = []										# accumulate message items here
    #	Extract all conversations by searching for a DIV with an ID at top level.
    tree = BeautifulSoup.BeautifulSoup(htmlsms)			# parse HTML into tree
    conversations = tree.findAll("div",attrs={"id" : True},recursive=False)
    for conversation in conversations :
        #	For each conversation, extract each row, which is one SMS message.
        rows = conversation.findAll(attrs={"class" : "gc-message-sms-row"})
        for row in rows :								# for all rows
            #	For each row, which is one message, extract all the fields.
            msgitem = {"id" : conversation["id"]}		# tag this message with conversation ID
            spans = row.findAll("span",attrs={"class" : True}, recursive=False)
            for span in spans :							# for all spans in row
                cl = span["class"].replace('gc-message-sms-', '')
                msgitem[cl] = (" ".join(span.findAll(text=True))).strip()	# put text in dict
            msgitems.append(msgitem)					# add msg dictionary to list
            #max-=1
            #if max == 0:
            #    return msgitems
    return msgitems


###########-- Data Mining --#################################

# Table to hold { Word : Count }
out_words = {'NOWORDS': -1}

# Go through gvoice sms
    # msg = {u'text': u'...', u'from': u'Rollin Baker:', 'id': u'de29237d1e64887f058bc463e525876e83d49b3f', u'time': u'10:44 PM'}
def sms_out_word_count(rtable):
    voice = Voice()
    voice.login()
    
    pageNumber = 1
    maxPageNumber = 5;     # set to -1 for all pages
    count = 0
    messages = 0

    while True:
        print "Reading page " + str(pageNumber) + "..."
        voice.sms(pageNumber)
        msgs = extractsms(voice.sms.html)
        for msg in msgs:
            if msg['from'] == 'Me:':
                messages+=1
                wordList = re.sub("[(!,*\-\.)]", " ",  msg['text']).split()
                for word in wordList:
                    word = word.lower()
                    if word in rtable:
                        rtable[word]+=1
                    else:
                        rtable[word] = 1
                    count+=1
        # my real max is about 984
        if len(msgs) == 0 or pageNumber==maxPageNumber:
            break;
        pageNumber+=1

    # Print Entries, low->highest
    print "Words sent: " + str(count) + " in " + str(messages) + " text messages"
    return count

sent_texts = sms_out_word_count(out_words)

def printWordsUsed(dict) :
    ordered_list = sorted(dict.items(), key=operator.itemgetter(1))
    # word[0] = string, word[1] = count
    for word in ordered_list:
        # print words with >=5 occurances
        if(word[1] > 5):
            print str(word[1]) + ": " + word[0]
    print "Total words: " + str(len(dict))
printWordsUsed(out_words)



###########-- Store Data --#################################

# Store to Firebase
def postToFirebase(firebase, dataTypeName, dict):
    for key,value in dict.items():
        result = firebase.post(dataTypeName, {key:value}, {'print': 'pretty'}, {'X_FANCY_HEADER': 'VERY FANCY'})
        print result

#firebase = firebase.FirebaseApplication('https://language-choice.firebaseio.com', None)
#dataTypeName = '/word-count'
#postToFirebase(firebase, dataTypeName, table)
#result = firebase.post(dataTypeName, table, {'print': 'pretty'}, {'X_FANCY_HEADER': 'VERY FANCY'})
#print result

######################-- Clipboard --########################
