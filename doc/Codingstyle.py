""" This one line outlines the module content 

Here we see the detailed Discription of the Module:
Make clear how to comment and structure your code so that other can read and use it.
Have a look at the content of https://github.com/alnkpa/pycc/wiki/Coding-style
"""
import sys # import in the beginning

class OurClass:
    """ This is one sentence describing the class' use 

After two new lines the detailed description of the class follows
SOME_CONSTANT is used as example for constants and 
    should be described here.
    The tab makes clear this belongs to the line above.
"""

    SOME_CONSTANT= "something that will not change is all capital"

    #this is a comment, regarding the following method
    def ourMethod(self, a, b, c):
        """ ourMethod(a,b,c) sets teh value of variable

set variable to the sum of a,b,c and 
return None
"""
      self.variable = a + b + c

    # use newlines between methods
    def getVariable(self):
        """getVariable() returns the value of variable as int."""
        # short > long
        return int(self.variable)

# some things do not need an explanation
__all__= ['OurClass']

if __name__ == '__main__':
    try:
       # testing OurClass() on errors during creation
       o= OurClass()
    except:
        errortype, error, traceback= sys.exc_info()
        print("always show when there is an unexpected error %s" % error)

# Rules are made to break them.
# And in case you did well you will not get harmed.
