# ohhh we have a loop around the imports
# workaround: only import torii instead the module carrier
from raptus import torii

def sdir(value):
    biggest = 0
    att = dir(value)
    for i in att:
        if biggest < len(i):
            biggest = len(i)
    for i in att:
        try:
            content = repr(getattr(value,i))[:60]
        except:
            content = '????'
            pass
        conversation(torii.carrier.PrintText(i+' '* (biggest - len(i))+content))


def ls(node):
    for i in node.getChildNodes():
        conversation(torii.carrier.PrintText(repr(i)))
