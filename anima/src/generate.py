import re

INCLUDE_RE = r'{{include:([^}]+)}}'
HEADING_RE = r'{{(\d):([^}]+)}}'


root = open('root.html','rt',encoding='utf-8').read()
match = re.search(INCLUDE_RE, root)
while match != None:
    fname = match.group(1)+".html"
    doc = open(fname,'rt',encoding='utf-8').read()
    (a, b) = match.span(0)

    match = re.search(INCLUDE_RE, doc)
    if match != None:
        raise Exception("in {}: {{{{include:}}}} directives can only appear in the root file.".format(fname))

    root = root[:a]+doc+root[b:]
    match = re.search(INCLUDE_RE, root)


# includes processed, now extract headings
currentCounts = [0,0,0,0]
currentLevel = 0

headings = []

match = re.search(HEADING_RE, root)
while match != None:
    (a, b) = match.span(0)
    level = int(match.group(1))-1
    text = match.group(2)
    if level > currentLevel:
        # subheading
        currentLevel += 1
        currentCounts[currentLevel] = 0
    elif level == currentLevel:
        # current-level heading
        currentCounts[currentLevel] += 1
        headings.append((currentCounts[:], text))
        
        prefix = ""
        showPrefix = currentCounts[3] == 0 # only show prefix for h1-h3
        for n in currentCounts:
            if n == 0: break
            prefix += str(n)+"."

        text = "<h{} id=\"{}\">{}{}</h{}>".format(currentLevel+1, prefix[:-1], prefix+" " if showPrefix else "", text, currentLevel+1)
        print(text)
        root = root[:a]+text+root[b:]
    elif level < currentLevel:
        # parent heading
        currentCounts[currentLevel] = 0
        currentLevel -= 1
    match = re.search(HEADING_RE, root)

# add toc
toc = "<ul class=\"toc\">"
for (counts, title) in headings:
    if counts[3] != 0: continue # only generate toc entries for h1-h3
    depth = len(list(filter(lambda x: x > 0, counts)))
    prefix = ""
    for n in counts:
        if n == 0: break
        prefix += str(n)+"."
    toc += "<li class=\"depth-{}\"><a href=\"#{}\">{}{}</a></li>".format(depth, prefix[:-1], prefix+" ", title)
toc += "</ul>"

root = root.replace("{{toc}}", toc)

open('../index.html','wt',encoding='utf-8').write(root)