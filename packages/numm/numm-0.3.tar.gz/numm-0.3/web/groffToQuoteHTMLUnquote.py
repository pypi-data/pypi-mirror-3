import os, subprocess, glob, re

def groffToQuoteHTMLUnquote(path):

    cmd = ['groff', '-Tascii', '-man', path]
    sp = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    stdout, stderr = sp.communicate()

    quoteHTMLunquote = "<pre>%s</pre>" % (stdout)

    # vt2html = [('[1m', '<b>'),
    #            ('[0m', '</b>')]

    typewriter = [(re.compile(r'([^\_])\1', re.MULTILINE), r'<b>\1</b>'),
                  (re.compile(r'\_(.)', re.MULTILINE), r'<i>\1</i>'),
                  (re.compile(r'\+o', re.MULTILINE), r'&#9679;')]

    for pattern,repl in typewriter:
        quoteHTMLunquote = re.sub(pattern, repl, quoteHTMLunquote)

    return quoteHTMLunquote

if __name__=='__main__':
    paths = glob.glob('../doc/*[0-9]')
    for path in paths:
        open(os.path.basename(path) + '.html', 'w').write(groffToQuoteHTMLUnquote(path))
