

def matches_md5( plain, hashed ):
    from hashlib import md5
    m = md5()
    m.update( plain )
    return m.hexdigest() == hashed
