from TwitterTest import CMUTweetTagger

query = input("yo: ")
l = CMUTweetTagger.runtagger_parse([query])

print(l)
