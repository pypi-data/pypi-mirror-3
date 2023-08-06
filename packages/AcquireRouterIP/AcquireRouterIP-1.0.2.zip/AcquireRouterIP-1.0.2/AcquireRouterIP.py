def AcquireRouterIP():
    import urllib.request
    context = urllib.request.urlopen('http://city.ip138.com/city.asp')
    s = str(context.read())
    ip = s[s.find('[')+1:s.find(']')]
    return ip

    
