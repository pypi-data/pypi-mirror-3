from setuptools import setup, find_packages

version = '0.11'

setup(name="intstr",
        version=version,
        description="int encode to string & string decode to int , can use in url shorten with a auto incr id",
        long_description=""" 

for example::

    import string

    ALPHABET = string.ascii_uppercase + string.ascii_lowercase + \
               string.digits + '-_'


    intstr = IntStr(ALPHABET)

    s = intstr.encode(1234567)
    print s 
    print intstr.decode(s)


    intstr = IntStr(ALPHABET,"$")

    s = intstr.encode(-1234567)
    print s 
    print intstr.decode(s)

""",
        author="zuroc",
        author_email="zsp007@gmail.com",
        packages=find_packages(),
        zip_safe=False
)
