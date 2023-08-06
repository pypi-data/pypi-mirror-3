'''
**simpleinput** implements functions that retrieve user inputs of some 
determined type.

Usage
-----

The functions defined in this module are designed to be a more robust 
alternative to Python's `input` and `raw_input` built-ins. All functions expect
a certain type of input and keeps asking the user for a input of the correct
type if it is not given.

A program that asks for two numbers and prints their sum could be implemented 
naively as

>>> print('Result: ', input('Two numbers:\\n<--') + input()) # doctest: +SKIP
Two numbers:
<-- 1
<-- 2
Result: 3

This is a poor implementation for two reasons: The `input()` built-in executes 
arbitrary Python code that can be exploited by malicious users. If the user 
types some bad numeric value it will fail by printing a nasty traceback and 
shutting down the program. 

The `float_input()` function in this library works similarly, but is safer and 
more user friendly:

>>> print('Result: ', float_input('Two numbers:\\n<--') + float_input()) # doctest: +SKIP
Two numbers:
<-- 1
<-- 2
Result: 3.0

If the user types an invalid numeric string, the new implementation complains 
and asks for a new valid value:

>>> print('Result: ', float_input('Two numbers:\\n<--') + float_input()) # doctest: +SKIP
Two numbers:
<-- 1_2
    error: invalid float!
<-- 1
<-- 2
Result: 3

There are other functions specialized in different types of arguments. See the 
section `API Documentation` for extra help.

Advanced features
-----------------

TODO: document me!

API Documentation
-----------------

Boolean types
`````````````

.. autofunction:: yn_input

.. autofunction:: tf_input


Numeric types
`````````````

.. autofunction:: int_input

.. autofunction:: float_input

.. autofunction:: numeric_input


Other
`````

.. autofunction:: choice_input

'''
from __future__ import absolute_import, print_function, unicode_literals, division
from future_builtins import * #@UnusedWildImport
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
import sys

__all__ = ('Input',
           'yn_input', 'tf_input',
           'int_input', 'float_input', 'numeric_input',
           'choices_input')

class Input(object):
    '''
    Implements various input getters.
    
    The class defines an environment in which the input getters can operate.
    Each environment defines a few functions:
      * ``getinput()``: reads the input from user
      * ``printline(text)``: prints a line of text
      * ``error(text)``: prints an error message
    
    The default implementation reads data in prompt and writes at sys.stdout.
    '''
    def __init__(self, getinput=None, printline=None, error=None): #@ReservedAssignment
        self.printline = printline if printline is not None else sys.stdout.write
        self.error = error if error is not None else self.printline
        self.getinput = self._fmt_input(getinput)

    def _printtext(self, text, end_newline=True):
        '''Prints text using the printline function'''

        return self.printtext(text, self.printline, end_newline)

    #===========================================================================
    # Boolean and numeric
    #===========================================================================
    def yn_input(self, text='<-- ', yes='yes', no='no', yn=(True, False), case=False, first_letter=True, error_msg=None):
        '''Takes a yes/no boolean input
        
        Parameters
        ----------
        text : str
            Text asking for user input.
        yes, no : str
            Strings representing the True and False values
        yn : tuple (yes, no)
            Set the values of each possible yes/no result. The default is 
            (True, False).
        case : bool
            If True, the input is case sensitive.
        first_letter : bool
            If True and the first letter of ``yes`` is different of ``no``, it 
            accepts a single letter as input (e.g., the string "y" becomes
            equivalent to "yes").
        error_msg : str
            A string with the error message. The string is formated using the
            "str.format" method with x.format(yes=yes, no=no, indent=indent). 
            ``yes`` and ``no`` are the same parameters listed above, and 
            ``indent`` is a string with white spaces of the same size of the 
            last line of the prompt text. 
        
        Examples
        --------
        
        >>> value = yn_input('value: ', getinput=['bar', 'y'])
        value: bar
               error: type "yes" or "no".
        value: y
        >>> value
        True'''

        if error_msg is None:
            error_msg = '{indent}error: type "{yes}" or "{no}".\n'
        if yes[0] == no[0]:
            first_letter = False
        yes_v, no_v = yn
        if not case:
            yes, no = yes.lower(), no.lower()

        while True:
            self._printtext(text, False)
            value = self.getinput()
            value = value if case else value.lower()

            if value == yes or (first_letter and yes.startswith(value)):
                return yes_v
            elif value == no or (first_letter and no.startswith(value)):
                return no_v
            else:
                self.error(error_msg.format(indent=self.indent(text),
                                            yes=yes, no=no))

    def tf_input(self, text='<-- ', true='true', false='false', case=False, first_letter=True, error_msg=None):
        '''Similar to `yn_input`, but the default values are 'True' and 'False'.
        
        Parameters
        ----------
        Similar to `yn_input`, but the parameters ``yes``, ``no``  are renamed 
        respectively as ``true``, ``false`` and changing ``yn`` is not 
        supported.
        
        Examples
        --------
        
        >>> value = tf_input('value: ', getinput=['bar', 'true'])
        value: bar
               error: type "true" or "false".
        value: true
        >>> value
        True
        '''
        return self.yn_input(text=text, case=case, first_letter=first_letter, error_msg=error_msg, yes=true, no=false, yn=(True, False))

    def int_input(self, text='<-- ', start=None, end=None, error_range=None,
                  error_msg=None, shift=0):
        '''Takes an integer number as input. 
        
        An alias to `numeric_input` with the parameter ``readnum`` set to the
        builtin function ``int``. 
        
        Examples
        --------
        
        >>> value = int_input('value: ', getinput=['0.1', '1'])
        value: 0.1
               error: must be an integer!
        value: 1
        >>> value
        1
        '''

        if error_msg is None:
            error_msg = '{indent}error: must be an integer!\n'
        return self.numeric_input(text, start, end, error_msg, error_range, shift, int)

    def float_input(self, text='<-- ', start=None, end=None, error_range=None,
                    error_msg=None, shift=0):
        '''Takes an float number as input. 
        
        An alias to `numeric_input` with the parameter ``readnum`` set to the
        builtin function ``float``. 
        
        Examples
        --------
        
        >>> value = float_input('value: ', getinput=['None', '1'])
        value: None
               error: must be a float!
        value: 1
        >>> value
        1.0
        '''

        if error_msg is None:
            error_msg = '{indent}error: must be a float!\n'
        return self.numeric_input(text, start, end, error_msg, error_range, shift, float)

    def numeric_input(self, text='<-- ', start=None, end=None, error_msg=None,
                      error_range=None, shift=0, readnum=None):
        '''Expects a numeric input. Numbers can be integers, floating point, 
        complex or fractions.
        
        Parameters
        ----------
        text : str
            Text asking for user input.
        start, end : int
            Numerical range: result must be greater or equal to ``start`` and
            smaller or equal to ``end``.
        error_range : str
            Error message shown if input does not represent a number. The string
            is formated using a ``indent`` keyword value which is a white space 
            string setting the indentation identical to the user input and with 
            the ``start`` and end ``values``.
        error_msg : str
            Error message shown if input does not represent a number. Is 
            formatted with the same arguments as error_range.
        shift : int
            The result is added to shift.
        readnum : callable
            Function that reads number from strings of text.
            
        Examples
        --------
        
        >>> value = numeric_input('value: ', 1, 10, getinput=['0.1', '5/2'])
        value: 0.1
               error: must in range [1..10]
        value: 5/2
        >>> value
        Fraction(5, 2)
        '''

        if readnum is None:
            def readnum(obj):
                try: return int(obj)
                except ValueError: pass

                try: return float(obj)
                except ValueError: pass

                try: return complex(obj)
                except ValueError: pass

                import fractions
                try: return fractions.Fraction(obj)
                except ValueError: pass

                raise ValueError('not a number: %s' % repr(obj))

        if error_msg is None:
            error_msg = '{indent}error: must be a number!\n'
        if error_range is None:
            error_range = '{indent}error: must in range [{start}..{end}]\n'
        start = start if start is not None else float('-inf')
        end = end if end is not None else float('inf')

        while True:
            self._printtext(text, False)
            num = self.getinput()
            try:
                value = readnum(num)
            except ValueError:
                self.error(error_msg.format(indent=self.indent(text),
                                            start=start, end=end))
                continue
            else:
                if start <= value <= end:
                    return value + shift
                else:
                    self.error(error_range.format(indent=self.indent(text),
                                                  start=start, end=end))

    #===========================================================================
    # Choices
    #===========================================================================
    def choice_input(self, text, choices, enum=None, prompt=None, case=False, sep=') ',
                     ret_choice=True, error_msg=None):
        '''Asks user to choose between a set of options.
        
        Parameters
        ----------
        text : str
            Text introducing the list of choices.
        choices : iterable
            List of all choices.
        enum : iterable
            A list of strings that represents each choice. The default is to 
            enumerate the choices from 1 to len(choices).
        prompt : bool
            The message asking for the user input.
        case : bool
            If True, the input is case sensitive.
        sep : str
            A string separating the enumeration from the choice text. The 
            default string is ') '.
        ret_choice : bool or iterable
            If ret_choice is True (default), it returns the choice given by the 
            user. If it is False, it returns the index of the corresponding 
            choice. If ret_choice is an iterable, it returns ret_choice[idx].
        error_msg : str
            A string with the error message.
            
        Examples
        --------
        
        >>> value = choice_input('Options:', ['foo', 'bar', 'foobar'], getinput=['0', '1'])
        Options:
          1) foo
          2) bar
          3) foobar
        <-- 0
            invalid choice!
        <-- 1
        '''

        if error_msg is None:
            error_msg = '{indent}invalid choice!\n'
        if prompt is None:
            prompt = '<-- '

        # Create choices, enum and ret_choice lists
        choices = list(choices)
        if enum is None:
            enum = [ str(i + 1) for (i, _x) in enumerate(choices)]
        else:
            enum = [ str(i) for (i, _x) in zip(enum, choices)]
        try:
            ret_choice = [ ret for (ret, _x) in zip(ret_choice, choices)]
        except TypeError:
            if ret_choice:
                ret_choice = choices
            else:
                ret_choice = range(len(enum))
        if case:
            ret_mapping = dict(zip(enum, ret_choice))
        else:
            ret_mapping = {k.lower(): v for (k, v) in zip(enum, ret_choice)}

        # Prints initial message:
        self.printline(text + '\n')
        max_size = max(map(len, enum)) + 2
        lines = [ x.rjust(max_size) + sep + y for (x, y) in zip(enum, choices) ]
        self._printtext('\n'.join(lines))

        while True:
            self._printtext(prompt, False)
            value = self.getinput()
            value = value if case else value.lower()

            try:
                return ret_mapping[value]
            except KeyError:
                self.error(error_msg.format(indent=self.indent(prompt)))

    def option_input(self, text, options, case=False, error_msg=None):
        '''User must type one of a set of options.
        
        Parameters
        ----------
        text : str
            Text asking for user input.
        options : iterable
            List of all choices.
        case : bool
            If True, the input is case sensitive.
        error_msg : str
            A string with the error message.
            
        Examples
        --------
        
        >>> beatles = ['John', 'Paul', 'George', 'Ringo']
        >>> value = option_input('A Beatle: ', beatles, error_msg='{indent}not a Beatle!\\n', getinput=['Mick', 'john'])
        A Beatle: Mick
                  not a Beatle!
        A Beatle: john
        >>> print(value)
        John
        '''

        if error_msg is None:
            error_msg = '{indent}invalid choice!\n'

        # Create choices, enum and ret_choice lists
        if not case:
            fmt_options = [ unicode(opt).lower() for opt in options ]
        else:
            fmt_options = [ unicode(opt) for opt in options ]

        while True:
            self._printtext(text, False)
            value = self.getinput()
            value = unicode(value if case else value.lower())

            try:
                idx = fmt_options.index(value)
            except ValueError:
                self.error(error_msg.format(indent=self.indent(text)))
            else:
                return options[idx]

    #===========================================================================
    # Strings
    #===========================================================================
    def str_input(self, text, maxsize=None, encoding='utf8', error_msg=None):
        '''User input as a unicode string.
        
        Parameters
        ----------
        text : str
            Text asking for user input.
        maxsize : int or None
            Maximum length of input string.
        encoding : str
            A string representing the input encoding.
        error_msg : str
            A string with the error message for too large strings.
            
        Examples
        --------
        
        >>> value = str_input('Your name: ', getinput=['Bond. James Bond.'])
        Your name: Bond. James Bond.
        >>> print(value)
        Bond. James Bond.
        '''

        if error_msg is None:
            error_msg = '{indent}too big! \n'

        while True:
            self._printtext(text, False)
            value = self.getinput().decode(encoding)
            if maxsize is not None and len(value) > maxsize:
                self.error(error_msg.format(indent=self.indent(text)))
            else:
                return value

    #===========================================================================
    # Auxiliary functions
    #===========================================================================
    @classmethod
    def indent(cls, text):
        '''Fill all characters of the last line of text with white spaces'''

        return ' ' * len(text.rpartition('\n')[-1])

    @classmethod
    def getinput(cls):
        '''Collects user input.'''

        old = sys.stdout
        try:
            sys.stdout = StringIO()
            result = raw_input()
        finally:
            sys.stdout = old
        return result

    @classmethod
    def printtext(cls, text, printline, end_newline=True):
        '''Uses the printline function to print a text spanning several lines.'''

        lines = text.splitlines()
        for l in lines[:-1]:
            printline(l + '\n')
        if end_newline:
            printline(lines[-1] + '\n')
        else:
            printline(lines[-1])

    @classmethod
    def printcb(cls, text, printline):
        '''Callback function that prints text using the given printline function.'''

        def callback():
            cls.printtext(text, printline)
        return callback


    @classmethod
    def _autodoc(cls, func):
        '''getinput : list or callable
            If it is a list, it corresponds to a list of user inputs that is 
            read sequentially. If it is a callable, it must be a function that
            asks for user input when called with no arguments.
        printline : callable
            Prints data to user. The default implementation simply writes data
            directly to `sys.stdout`.  
        error : callable
            Function that prints error messages to the user. The default 
            implementation simply calls the printline function supplied by the
            callee.
        
        Examples'''
        # Formats documentation for global input functions
        # The above docstring is added to the functions decorated with _autodoc

        doc = getattr(cls, func.__name__).__doc__
        head, _, tail = doc.partition('Examples')
        if 'Parameters' in head:
            doc = head + cls._autodoc.__doc__ + tail

        func.__doc__ = doc
        return func

    def _fmt_input(self, input): #@ReservedAssignment

        if input is None:
            return self.getinput
        elif callable(input):
            return input
        else:
            seq = iter(input)
            def next_item():
                value = next(seq)
                self.printline('%s\n' % value)
                return value
            return next_item

#===============================================================================
# API functions
#===============================================================================
@Input._autodoc
def yn_input(text='<-- ', yes='yes', no='no', yn=(True, False), case=False, first_letter=True, error_msg=None,
             getinput=None, printline=None, error=None):
    kwds = locals()
    inpt = Input(kwds.pop('getinput'), kwds.pop('printline'), kwds.pop('error'))
    return inpt.yn_input(**kwds)

@Input._autodoc
def tf_input(text='<-- ', true='true', false='false', case=False, first_letter=True, error_msg=None,
             getinput=None, printline=None, error=None):
    kwds = locals()
    inpt = Input(kwds.pop('getinput'), kwds.pop('printline'), kwds.pop('error'))
    return inpt.tf_input(**kwds)

@Input._autodoc
def int_input(text='<-- ', start=None, end=None, error_msg=None, error_range=None, shift=0,
              getinput=None, printline=None, error=None):
    kwds = locals()
    inpt = Input(kwds.pop('getinput'), kwds.pop('printline'), kwds.pop('error'))
    return inpt.int_input(**kwds)

@Input._autodoc
def float_input(text='<-- ', start=None, end=None, error_msg=None, error_range=None, shift=0,
              getinput=None, printline=None, error=None):
    kwds = locals()
    inpt = Input(kwds.pop('getinput'), kwds.pop('printline'), kwds.pop('error'))
    return inpt.float_input(**kwds)

@Input._autodoc
def numeric_input(text='<-- ', start=None, end=None, error_msg=None, error_range=None, shift=0, readnum=None,
              getinput=None, printline=None, error=None):
    kwds = locals()
    inpt = Input(kwds.pop('getinput'), kwds.pop('printline'), kwds.pop('error'))
    return inpt.numeric_input(**kwds)

@Input._autodoc
def choice_input(text, choices, enum=None, prompt=None, case=False, ret_choice=True, error_msg=None,
                 getinput=None, printline=None, error=None):
    kwds = locals()
    inpt = Input(kwds.pop('getinput'), kwds.pop('printline'), kwds.pop('error'))
    return inpt.choice_input(**kwds)

@Input._autodoc
def option_input(text, options, case=False, error_msg=None,
                 getinput=None, printline=None, error=None):
    kwds = locals()
    inpt = Input(kwds.pop('getinput'), kwds.pop('printline'), kwds.pop('error'))
    return inpt.option_input(**kwds)

@Input._autodoc
def str_input(text, maxsize=None, encoding='utf8', error_msg=None,
              getinput=None, printline=None, error=None):
    kwds = locals()
    inpt = Input(kwds.pop('getinput'), kwds.pop('printline'), kwds.pop('error'))
    return inpt.str_input(**kwds)

if __name__ == '__main__':
    import doctest
    doctest.testmod()
