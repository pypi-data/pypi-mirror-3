#
#   Copyright 2011 Olivier Kozak
#
#   This file is part of Mocki.
#
#   Mocki is free software: you can redistribute it and/or modify it under the
#   terms of the GNU Lesser General Public License as published by the Free
#   Software Foundation, either version 3 of the License, or (at your option)
#   any later version.
#
#   Mocki is distributed in the hope that it will be useful, but WITHOUT ANY
#   WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#   FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
#   details.
#
#   You should have received a copy of the GNU Lesser General Public License
#   along with Mocki. If not, see <http://www.gnu.org/licenses/>.
#

"""An easy-to-use but full featured mocking library for Python.

"""
import collections, itertools, threading

class Mock(object):
    """A mock is a callable object that is able to track any call invoked from
    it and that automatically provides on-fly generated mock methods from each
    non existing member accessed.

    To use it, first create a mock giving it a name, then invoke some calls from
    it, with or without args and kwargs :
        >>> mock = Mock('theMock')

        >>> mock()
        >>> mock(1, 2, 3)
        >>> mock(x=7, y=8, z=9)
        >>> mock(1, 2, 3, x=7, y=8, z=9)

    Now, we can ask to verify whether or not a given call was invoked from it :
        >>> from mocki.expectations import once
        >>> from mocki.matchers import thatCall

        >>> mock.verify(thatCall(1, 2, 3, x=7, y=8, z=9)).invoked(once())

    In case of verification failure, an assertion error will be raised with a
    debugging-friendly message indicating the problem :
        >>> mock.verify(thatCall(7, 8, 9, x=1, y=2, z=3)).invoked(once())
        Traceback (most recent call last):
        ...
        AssertionError: Found no matching call invoked from theMock up to now :
          theMock()
          theMock(1, 2, 3)
          theMock(x=7, y=8, z=9)
          theMock(1, 2, 3, x=7, y=8, z=9)

    """
    def __init__(self, name):
        self.name = name
        self.invocations = []
        self.methods = []
        self.stub = lambda call: None

    def __call__(self, *args, **kwargs):
        invocation = CallInvocation(self, Call(*args, **kwargs))
        self.invocations.append(invocation)
        return self.stub(invocation.call)

    def __getattr__(self, methodName):
        """Automatically provides on-fly generated mock methods from each non
        existing member accessed.

        To use it, first create a mock giving it a name, then invoke some calls
        from its mock methods, with or without args and kwargs :
            >>> mock = Mock('theMock')

            >>> mock.method()
            >>> mock.otherMethod(1, 2, 3)
            >>> mock.method(x=7, y=8, z=9)
            >>> mock.otherMethod(1, 2, 3, x=7, y=8, z=9)

        Now, we can ask to verify whether or not a given call was invoked from
        its mock methods :
            >>> from mocki.expectations import once
            >>> from mocki.matchers import thatCall

            >>> mock.otherMethod.verify(thatCall(1, 2, 3, x=7, y=8, z=9)).invoked(once())

        In case of verification failure, an assertion error will be raised with
        a debugging-friendly message indicating the problem :
            >>> mock.otherMethod.verify(thatCall(7, 8, 9, x=1, y=2, z=3)).invoked(once()) # doctest: +ELLIPSIS
            Traceback (most recent call last):
            ...
            AssertionError: Found no matching call invoked from theMock.otherMethod up to now :
              theMock.otherMethod(1, 2, 3)
              theMock.otherMethod(1, 2, 3, x=7, y=8, z=9)

        Actually, since mock methods are mocks themselves, everything possible
        on mocks is also possible on their methods. And everything possible on
        their methods is also possible their methods methods, and so on...

        Note that the following members are reserved and cannot be used as mock
        methods : name, invocations, methods, stub, verify, on.

        """
        method = Mock('%s.%s' % (self.name, methodName))
        setattr(self, methodName, method)
        self.methods.append(method)
        return method

    def verify(self, matcher):
        """Verifies whether or not the given matching calls were invoked.

        To use it, first create a mock to verify :
            >>> mock = Mock('theMock')

        If we ask to verify whether or not a 2nd call was invoked from the mock,
        an assertion error will be raised with a debugging-friendly message
        indicating that no call has been invoked from it up to now :
            >>> from mocki.expectations import once
            >>> from mocki.matchers import thatCall

            >>> mock.verify(thatCall('2ndCall')).invoked(once())
            Traceback (most recent call last):
            ...
            AssertionError: No call invoked from theMock up to now.

        Now, invoke some calls from the mock :
            >>> mock('1stCall')
            >>> mock('2ndCall')
            >>> mock('1stCall')

        If we ask again to verify whether or not the 2nd call was invoked, no
        more assertion error will be raised, which means that it was invoked
        once as expected :
            >>> mock.verify(thatCall('2ndCall')).invoked(once())

        Of course, if we ask the contrary, i.e. whether or not the 2nd call was
        never invoked, an assertion error will be raised again :
            >>> from mocki.expectations import never

            >>> mock.verify(thatCall('2ndCall')).invoked(never())
            Traceback (most recent call last):
            ...
            AssertionError: Found one matching call invoked from theMock up to now :
              theMock('1stCall')
            > theMock('2ndCall')
              theMock('1stCall')

        What is interesting here is the debugging-friendly message attached to
        the assertion error. It clearly shows us which calls were invoked from
        the mock up to now, and among them, which ones are matching with the
        verification statement. Here are some other examples :
            >>> mock.verify(thatCall('1stCall')).invoked(once())
            Traceback (most recent call last):
            ...
            AssertionError: Found 2 matching calls invoked from theMock up to now :
            > theMock('1stCall')
              theMock('2ndCall')
            > theMock('1stCall')

            >>> mock.verify(thatCall('3rdCall')).invoked(once())
            Traceback (most recent call last):
            ...
            AssertionError: Found no matching call invoked from theMock up to now :
              theMock('1stCall')
              theMock('2ndCall')
              theMock('1stCall')

        """
        class OnMockCallVerifier(object):
            def __init__(self, mock, matcher):
                self.mock = mock
                self.matcher = matcher

            def invoked(self, expectation):
                def getMatchingInvocations():
                    return list(filter(lambda invocation: self.matcher(invocation.call), self.mock.invocations))

                def getInvocationsHistory():
                    return '\n'.join(map(lambda invocation: '> %s' % str(invocation) if self.matcher(invocation.call) else '  %s' % str(invocation), self.mock.invocations))

                if not expectation(getMatchingInvocations()):
                    if len(self.mock.invocations) == 0:
                        raise AssertionError('No call invoked from %s up to now.' % self.mock.name)
                    else:
                        if len(getMatchingInvocations()) == 0:
                            raise AssertionError('Found no matching call invoked from %s up to now :\n%s' % (self.mock.name, getInvocationsHistory()))
                        elif len(getMatchingInvocations()) == 1:
                            raise AssertionError('Found one matching call invoked from %s up to now :\n%s' % (self.mock.name, getInvocationsHistory()))
                        else:
                            raise AssertionError('Found %s matching calls invoked from %s up to now :\n%s' % (len(getMatchingInvocations()), self.mock.name, getInvocationsHistory()))

        return OnMockCallVerifier(self, matcher)

    def on(self, matcher):
        """Stubs this mock on invocation to the given matching calls.

        To use it, first create a mock, then stub it, e.g. to return a given
        value on invocation to the given matching calls :
            >>> from mocki.matchers import anyCall
            >>> from mocki.stubs import returnValue

            >>> mock = Mock('theMock')

            >>> mock.on(anyCall()).then(returnValue('value'))

        Now, any matching invocation will return this given value :
            >>> mock('1stCall')
            'value'

            >>> mock('2ndCall')
            'value'

        Sometimes, it can be very useful to override a global stub with a more
        specific one. This is simply done by defining a new specific stub over
        the already existing global one. E.g., here is how to define a specific
        stub for the 2nd call :
            >>> from mocki.matchers import thatCall

            >>> mock.on(thatCall('2ndCall')).then(returnValue('otherValue'))

        Now, the 2nd call will be based on the last specific stub we defined,
        even if the global one is still matching with it :
            >>> mock('1stCall')
            'value'

            >>> mock('2ndCall')
            'otherValue'

        """
        class CallStubber(object):
            def __init__(self, mock, matcher):
                self.mock = mock
                self.matcher = matcher

            def then(self, stub):
                class StubDecorator(object):
                    def __init__(self, stub, matcher, decoratedStub):
                        self.stub = stub
                        self.matcher = matcher
                        self.decoratedStub = decoratedStub

                    def __call__(self, call):
                        if self.matcher(call):
                            return self.stub(call)
                        else:
                            return self.decoratedStub(call)

                self.mock.stub = StubDecorator(stub, self.matcher, self.mock.stub)

        return CallStubber(self, matcher)

class StaticMock(object):
    """Used in with statements to temporary mock static members.

    To use it, you first need a static member to mock :
        >>> class Parent(object):
        ...     @classmethod
        ...     def staticMember(cls):
        ...         return 'value'

    Before the with statement, the static member behaves normally :
        >>> Parent.staticMember()
        'value'

    Within the with statement, the static member lost its normal behavior and
    can be used as any mock (actually, it is a mock) :
        >>> from mocki.expectations import once
        >>> from mocki.matchers import anyCall

        >>> with StaticMock(Parent, 'staticMember'):
        ...     Parent.staticMember.verify(anyCall()).invoked(once())
        Traceback (most recent call last):
        ...
        AssertionError: No call invoked from Parent.staticMember up to now.

    After the with statement, the static member recovers its normal behavior :
        >>> Parent.staticMember()
        'value'

    """
    def __init__(self, parent, memberName):
        self.parent, self.memberName = parent, memberName

    def __enter__(self):
        self.oldValue = getattr(self.parent, self.memberName)
        setattr(self.parent, self.memberName, Mock('%s.%s' % (self.parent.__name__, self.memberName)))

    def __exit__(self, type, value, traceback):
        setattr(self.parent, self.memberName, self.oldValue)

class Call(collections.namedtuple('Call', 'args kwargs')):
    """A call with its args and kwargs.

    """
    def __new__(cls, *args, **kwargs):
        return super(Call, cls).__new__(cls, args, kwargs)

    def __hash__(self):
        return hash(self.args) + hash(tuple(self.kwargs.items()))

    def __repr__(self):
        """This call's representation :
            >>> repr(Call())
            'Call()'

            >>> repr(Call(1, 2.0, '300'))
            "Call(1, 2.0, '300')"

            >>> repr(Call(x=7, y=8.0, z='900'))
            "Call(x=7, y=8.0, z='900')"

            >>> repr(Call(1, 2.0, '300', x=7, y=8.0, z='900'))
            "Call(1, 2.0, '300', x=7, y=8.0, z='900')"

        """
        def getArgsAsCsv():
            return ", ".join(map(repr, self.args))

        def getKwargsAsCsv():
            return ", ".join(map(lambda kwarg: '%s=%r' % kwarg, sorted(self.kwargs.items())))

        if len(self.args) == 0 and len(self.kwargs) == 0:
            return 'Call()'
        elif len(self.kwargs) == 0:
            return 'Call(%s)' % getArgsAsCsv()
        elif len(self.args) == 0:
            return 'Call(%s)' % getKwargsAsCsv()
        else:
            return 'Call(%s, %s)' % (getArgsAsCsv(), getKwargsAsCsv())

class CallInvocation(collections.namedtuple('CallInvocation', 'mock call')):
    """A call invocation represents a call invoked on a particular mock.

    """
    def __str__(self):
        """Returns a pretty string representing this call invocation :
            >>> mock = Mock('theMock')

            >>> print(CallInvocation(mock, Call()))
            theMock()

            >>> print(CallInvocation(mock, Call(1, 2.0, '300')))
            theMock(1, 2.0, '300')

            >>> print(CallInvocation(mock, Call(x=7, y=8.0, z='900')))
            theMock(x=7, y=8.0, z='900')

            >>> print(CallInvocation(mock, Call(1, 2.0, '300', x=7, y=8.0, z='900')))
            theMock(1, 2.0, '300', x=7, y=8.0, z='900')

        """
        def getArgsAsCsv():
            return ", ".join(map(repr, self.call.args))

        def getKwargsAsCsv():
            return ", ".join(map(lambda kwarg: '%s=%r' % kwarg, sorted(self.call.kwargs.items())))

        if len(self.call.args) == 0 and len(self.call.kwargs) == 0:
            return '%s()' % self.mock.name
        elif len(self.call.kwargs) == 0:
            return '%s(%s)' % (self.mock.name, getArgsAsCsv())
        elif len(self.call.args) == 0:
            return '%s(%s)' % (self.mock.name, getKwargsAsCsv())
        else:
            return '%s(%s, %s)' % (self.mock.name, getArgsAsCsv(), getKwargsAsCsv())
