## Parse through the pdf document, filter through key words, return the phrases where the key words are found

## make sure that the file can be parsed through
def parseFile(file)
    if words in file != 0:
        return "success"
    return "fail to parse file"

# keywords is the array that is inputted by the user. Search for keywords and extract the phrase/sentence
def searchFile(file, keywords):
    phrases = {}
    for word in keywords:
        if word in file:
            phrases[word] = extract_phrase()
        return "finished search"
    return "no keywords found"


# Highlight the parts that are extracted for users
def highlight(file,text)
    for text in searchFile(file):
        highlight(text)
        return "highlight complete"
    return "failed to highlight document"
