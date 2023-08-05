#
# Copyright (c) 2006-2011, Prometheus Research, LLC
# See `LICENSE` for license information, `AUTHORS` for the list of authors.
#


"""
:mod:`htsql.tr.bind`
====================

This module implements the binding process.
"""


from ..util import maybe, listof, tupleof, similar
from ..adapter import Adapter, Protocol, adapts
from ..domain import (BooleanDomain, IntegerDomain, DecimalDomain,
                      FloatDomain, UntypedDomain)
from ..classify import normalize
from .error import BindError
from .syntax import (Syntax, QuerySyntax, SegmentSyntax, SelectorSyntax,
                     ApplicationSyntax, FunctionSyntax, MappingSyntax,
                     OperatorSyntax, QuotientSyntax, SieveSyntax, LinkSyntax,
                     HomeSyntax, AssignmentSyntax, SpecifierSyntax, GroupSyntax,
                     IdentifierSyntax, WildcardSyntax, ReferenceSyntax,
                     ComplementSyntax, StringSyntax, NumberSyntax)
from .binding import (Binding, WrappingBinding, QueryBinding, SegmentBinding,
                      RootBinding, HomeBinding, FreeTableBinding,
                      AttachedTableBinding, ColumnBinding, QuotientBinding,
                      KernelBinding, ComplementBinding, LinkBinding,
                      SieveBinding, SortBinding, CastBinding, RescopingBinding,
                      AssignmentBinding, DefinitionBinding, SelectionBinding,
                      RerouteBinding, ReferenceRerouteBinding, AliasBinding,
                      LiteralBinding,
                      Recipe, LiteralRecipe, SelectionRecipe,
                      FreeTableRecipe, AttachedTableRecipe,
                      ColumnRecipe, KernelRecipe, ComplementRecipe,
                      SubstitutionRecipe, BindingRecipe, ClosedRecipe,
                      PinnedRecipe, AmbiguousRecipe)
from .lookup import (lookup_attribute, lookup_reference, lookup_complement,
                     lookup_attribute_set, lookup_reference_set,
                     expand, direct, guess_name, lookup_command)
from .coerce import coerce


class BindingState(object):
    """
    Encapsulates the (mutable) state of the binding process.

    State attributes:

    `root` (:class:`htsql.tr.binding.RootBinding`)
        The root naming scope.

    `scope` (:class:`htsql.tr.binding.Binding`)
        The current naming scope.
    """

    def __init__(self, environment=None):
        # The root lookup scope.
        self.root = None
        # The current lookup scope.
        self.scope = None
        # The stack of previous lookup scopes.
        self.scope_stack = []
        # References in the root scope.
        self.environment = environment

    def set_root(self, root):
        """
        Sets the root lookup context.

        This function initializes the lookup context stack and must be
        called before any calls of :meth:`push_scope` and :meth:`pop_scope`.

        `root` (:class:`htsql.tr.binding.RootBinding`)
            The root lookup scope.
        """
        # Check that the lookup stack is not initialized.
        assert self.root is None
        assert self.scope is None
        assert isinstance(root, RootBinding)
        self.root = root
        self.scope = root
        # Add global references.
        if self.environment is not None:
            for name, recipe in self.environment:
                name = normalize(name)
                self.scope = DefinitionBinding(self.scope, name, True, None,
                                               recipe, self.scope.syntax)

    def flush(self):
        """
        Clears the lookup scopes.
        """
        # We expect the lookup scope stack to be empty and the current
        # scope to coincide with the root scope.
        assert self.root is not None
        assert not self.scope_stack
        #assert self.root is self.scope
        self.root = None
        self.scope = None

    def push_scope(self, scope):
        """
        Sets the new lookup scope.

        This function stores the current scope in the stack and makes
        the given binding the new lookup scope.  Use the :attr:`scope`
        attribute to get the current scope; :meth:`pop_scope` to restore
        the previous scope.

        `scope` (:class:`htsql.tr.binding.Binding`)
            The new lookup scope.
        """
        # Sanity check on the argument.
        assert isinstance(scope, Binding)
        # Ensure that the root scope was set.
        assert self.root is not None
        # Save the current lookup scope.
        self.scope_stack.append(self.scope)
        # Assign the new lookup scope.
        self.scope = scope

    def pop_scope(self):
        """
        Restores the previous lookup scope.

        This functions restores the previous lookup scope from the stack.
        Use the :attr:`scope` attribute to get the current scope;
        :meth:`push_scope` to change the current scope.
        """
        # Restore the prevous lookup scope from the stack.
        self.scope = self.scope_stack.pop()

    def bind(self, syntax, scope=None):
        """
        Binds the given syntax node using the current binding state.

        Returns a binding node.

        `syntax` (:class:`htsql.tr.syntax.Syntax`)
            The syntax node to bind.

        `scope` (:class:`htsql.tr.binding.Binding` or ``None``)
            If set, the lookup scope is set to `scope` when
            binding the syntax node.
        """
        return bind(syntax, self, scope)

    def use(self, recipe, syntax, scope=None):
        """
        Applies a recipe to produce a binding node.

        Returns a binding node.

        `recipe` (:class:`htsql.tr.binding.Recipe`)
            The recipe to apply.

        `syntax` (:class:`htsql.tr.syntax.Syntax`)
            The syntax node associated with the recipe.

        `scope` (:class:`htsql.tr.binding.Binding` or ``None``)
            If set, the lookup scope is set to `scope` when
            binding the syntax node.
        """
        # If passed, set the new lookup scope.
        if scope is not None:
            self.push_scope(scope)
        # Realize and apply `BindByRecipe` adapter.
        bind = BindByRecipe(recipe, syntax, self)
        binding = bind()
        # Restore the old lookup scope.
        if scope is not None:
            self.pop_scope()
        # Return the generated binding node.
        return binding

    def call(self, syntax, scope=None):
        """
        Binds a global function or a global identifier.

        Returns a binding node.

        `syntax` (:class:`htsql.tr.syntax.Syntax`)
            The syntax node to bind.

        `scope` (:class:`htsql.tr.binding.Binding` or ``None``)
            If set, the lookup context is set to `scope` when
            binding the syntax node.
        """
        # If passed, set the new lookup scope.
        if scope is not None:
            self.push_scope(scope)
        # Realize and apply `BindByName` protocol.
        bind = BindByName(syntax, self)
        binding = bind()
        # Restore the old lookup scope.
        if scope is not None:
            self.pop_scope()
        # Return the generated binding node.
        return binding


class Bind(Adapter):
    """
    Translates a syntax node to a binding node.

    This is an interface adapter; see subclasses for implementations.

    The binding process resolves identifiers against database objects,
    resolves and validates operators and function calls, and determine
    types of all expression.

    The :class:`Bind` adapter has the following signature::

        Bind: (Syntax, BindingState) -> Binding

    The adapter is polymorphic on the `Syntax` argument.

    `syntax` (:class:`htsql.tr.syntax.Syntax`)
        The syntax node to bind.

    `state` (:class:`BindingState`)
        The current state of the binding process.
    """

    adapts(Syntax)

    def __init__(self, syntax, state):
        assert isinstance(syntax, Syntax)
        assert isinstance(state, BindingState)
        self.syntax = syntax
        self.state = state

    def __call__(self):
        # The default implementation raises an error.  It is actually
        # unreachable since we provide an implementation for all syntax nodes.
        raise BindError("unable to bind a node", self.syntax.mark)


def hint_choices(choices):
    # Generate a hint from a list of choices.
    assert isinstance(choices, listof(unicode))
    if not choices:
        return None
    chunks = ["did you mean:"]
    if len(choices) == 1:
        chunks.append("'%s'" % choices[0].encode('utf-8'))
    else:
        chunks.append(", ".join("'%s'" % choice.encode('utf-8')
                                for choice in choices[:-1]))
        chunks.append("or")
        chunks.append("'%s'" % choices[-1].encode('utf-8'))
    return " ".join(chunks)


class BindQuery(Bind):

    adapts(QuerySyntax)

    def __call__(self):
        # Initialize the lookup scope with a root node.
        root = RootBinding(self.syntax)
        self.state.set_root(root)
        # Bind the segment node if it is available.
        segment = None
        if self.syntax.segment is not None:
            # FIXME: refactor the top-level syntax nodes.
            if self.syntax.segment.branch is not None:
                segment = self.state.bind(self.syntax.segment)
        # Shut down the lookup scope stack.
        self.state.flush()
        if segment is not None:
            if lookup_command(segment) is not None:
                return segment
        # Construct and return the top-level binding node.
        return QueryBinding(root, segment, self.syntax)


class BindSegment(Bind):

    adapts(SegmentSyntax)

    def __call__(self):
        # FIXME: an empty segment syntax should not be generated.
        if self.syntax.branch is None:
            raise BindError("output columns are not specified",
                            self.syntax.mark)
        # Bind the segment expression.
        seed = self.state.bind(self.syntax.branch)
        if lookup_command(seed) is not None:
            return seed
        # Extract output flow and columns.
        bindings = []
        recipes = expand(seed)
        if recipes is None:
            bindings.append(seed)
            seed = None
        else:
            for syntax, recipe in recipes:
                binding = self.state.use(recipe, syntax, scope=seed)
                binding = RescopingBinding(binding, seed, binding.syntax)
                bindings.append(binding)
        # Validate the types of the output columns.
        elements = []
        for binding in bindings:
            domain = coerce(binding.domain)
            if domain is None:
                raise BindError("output column must be scalar",
                                binding.mark)
            element = CastBinding(binding, domain, binding.syntax)
            elements.append(element)
        # Complain on an empty selector.
        # FIXME: an empty selector should be valid.
        if not elements:
            raise BindError("output columns are not specified",
                            self.syntax.mark)
        # Generate a binding node.
        return SegmentBinding(self.state.scope, seed, elements, self.syntax)


class BindSelector(Bind):

    adapts(SelectorSyntax)

    def __call__(self):
        # Determine the base of the selection.
        scope = self.state.scope
        if self.syntax.lbranch is not None:
            scope = self.state.bind(self.syntax.lbranch)
        self.state.push_scope(scope)
        # Extract selector elements.
        elements = []
        for branch in self.syntax.rbranches:
            binding = self.state.bind(branch)
            # Handle in-selector assignments.
            if isinstance(binding, AssignmentBinding):
                if len(binding.terms) != 1:
                    raise BindError("qualified definition is not allowed"
                                    " for an in-selector assignment",
                                    binding.mark)
                if binding.parameters is not None:
                    raise BindError("parameterized definition is not allowed"
                                    " for an in-selector assignment",
                                    binding.mark)
                name, is_reference = binding.terms[0]
                if is_reference:
                    recipe = BindingRecipe(self.state.bind(binding.body))
                else:
                    recipe = SubstitutionRecipe(scope, [],
                                                None, binding.body)
                recipe = ClosedRecipe(recipe)
                syntax = binding.syntax
                if isinstance(syntax, AssignmentSyntax):
                    syntax = syntax.lbranch
                binding = self.state.use(recipe, syntax)
                scope = DefinitionBinding(scope, name, is_reference,
                                          None, recipe, scope.syntax)
                self.state.pop_scope()
                self.state.push_scope(scope)
            # Extract nested selectors, if any.
            bindings = []
            recipes = expand(binding, is_hard=False)
            if recipes is not None:
                seed = binding
                for syntax, recipe in recipes:
                    binding = self.state.use(recipe, syntax)
                    binding = RescopingBinding(binding, seed, binding.syntax)
                    bindings.append(binding)
            else:
                bindings.append(binding)
            # Handle in-selector direction decorators.
            order = []
            for binding in bindings:
                direction = direct(binding)
                if direction is not None:
                    order.append(binding)
            if order:
                scope = SortBinding(scope, order, None, None, scope.syntax)
                self.state.pop_scope()
                self.state.push_scope(scope)
            elements.extend(bindings)
        self.state.pop_scope()
        # Generate a selection scope.
        return SelectionBinding(scope, elements, self.syntax)


class BindApplication(Bind):

    adapts(ApplicationSyntax)

    def __call__(self):
        # Look for the parameterized attribute in the current local scope.
        recipe = lookup_attribute(self.state.scope,
                                  self.syntax.name, len(self.syntax.arguments))
        if recipe is not None:
            binding = self.state.use(recipe, self.syntax)
        # If not found, look for a global function.
        else:
            binding = self.state.call(self.syntax)
        return binding


class BindOperator(Bind):

    adapts(OperatorSyntax)

    def __call__(self):
        # Look for the operator in the global scope.  We skip the local scope
        # as there is no way to add an operator to a local scope.
        return self.state.call(self.syntax)


class BindQuotient(Bind):

    adapts(QuotientSyntax)

    def __call__(self):
        # Get the seed of the quotient.
        seed = self.state.bind(self.syntax.lbranch)
        # get the kernel expressions.
        elements = []
        binding = self.state.bind(self.syntax.rbranch, scope=seed)
        recipes = expand(binding, is_hard=False)
        if recipes is not None:
            for syntax, recipe in recipes:
                element = self.state.use(recipe, syntax, scope=binding)
                element = RescopingBinding(element, binding, element.syntax)
                elements.append(element)
        else:
            elements.append(binding)
        # Validate types of the kernel expressions.
        kernels = []
        for element in elements:
            domain = coerce(element.domain)
            if domain is None:
                raise BindError("quotient column must be scalar",
                                element.mark)
            kernel = CastBinding(element, domain, element.syntax)
            kernels.append(kernel)
        # Generate the quotient scope.
        quotient = QuotientBinding(self.state.scope, seed, kernels,
                                   self.syntax)
        # Assign names to the kernel and the complement links when possible.
        binding = quotient
        name = guess_name(seed)
        if name is not None:
            recipe = ComplementRecipe(quotient)
            recipe = ClosedRecipe(recipe)
            binding = DefinitionBinding(binding, name, False, None, recipe,
                                        self.syntax)
        for index, kernel in enumerate(kernels):
            name = guess_name(kernel)
            if name is not None:
                recipe = KernelRecipe(quotient, index)
                recipe = ClosedRecipe(recipe)
                binding = DefinitionBinding(binding, name, False, None, recipe,
                                            self.syntax)
        return binding


class BindSieve(Bind):

    adapts(SieveSyntax)

    def __call__(self):
        # Get the sieve base.
        base = self.state.bind(self.syntax.lbranch)
        # Bind the filter and force the Boolean type on it.
        filter = self.state.bind(self.syntax.rbranch, scope=base)
        filter = CastBinding(filter, coerce(BooleanDomain()), filter.syntax)
        # Produce a sieve scope.
        return SieveBinding(base, filter, self.syntax)


class BindLink(Bind):

    adapts(LinkSyntax)

    def __call__(self):
        # Bind the origin images.
        origin_images = []
        binding = self.state.bind(self.syntax.lbranch)
        recipes = expand(binding, is_hard=False)
        if recipes is not None:
            for syntax, recipe in recipes:
                element = self.state.use(recipe, syntax)
                element = RescopingBinding(element, binding, element.syntax)
                origin_images.append(element)
        else:
            origin_images.append(binding)
        # Bind the target scope.
        home = HomeBinding(self.state.scope, self.syntax)
        seed = self.state.bind(self.syntax.rbranch, scope=home)
        # Bind the target images; if not provided, reuse the syntax node
        # of the origin images.
        binding = seed
        target_images = []
        recipes = expand(seed, is_hard=False)
        if recipes is None:
            binding = self.state.bind(self.syntax.lbranch, scope=seed)
            recipes = expand(binding, is_hard=False)
        if recipes is not None:
            for syntax, recipe in recipes:
                element = self.state.use(recipe, syntax, scope=seed)
                element = RescopingBinding(element, binding, element.syntax)
                target_images.append(element)
        else:
            target_images.append(binding)
        # Correlate origin and target images.
        if len(origin_images) != len(target_images):
            raise BindError("unbalanced origin and target columns",
                            self.syntax.mark)
        images = []
        for origin_image, target_image in zip(origin_images, target_images):
            domain = coerce(origin_image.domain, target_image.domain)
            if domain is None:
                raise BindError("cannot coerce origin and target columns"
                                " to a common type", self.syntax.mark)
            origin_image = CastBinding(origin_image, domain,
                                       origin_image.syntax)
            target_image = CastBinding(target_image, domain,
                                       target_image.syntax)
            images.append((origin_image, target_image))
        # Generate a link scope.
        return LinkBinding(self.state.scope, seed, images, self.syntax)


class BindHome(Bind):

    adapts(HomeSyntax)

    def __call__(self):
        # Make the home scope.
        home = HomeBinding(self.state.scope, self.syntax)
        # Bind the operand against the home scope.
        return self.state.bind(self.syntax.rbranch, scope=home)


class BindAssignment(Bind):

    adapts(AssignmentSyntax)

    def __call__(self):
        # Parse the left side of the assignment.  It takes one of the forms:
        #   $reference := ...
        #   identifier := ...
        #   identifier(parameter,...) := ...
        #   parent. ... .identifier(parameter,...) := ...
        #   parent. ... .$identifier(parameter,...) := ...

        # The dot-separated names and reference indicators.
        terms = []
        parameters = None
        syntax = self.syntax.lbranch
        # Is it a reference?
        # Expect a dot-separated list of identifiers followed
        # by an optional function call or a reference.
        # Dot-separated identifiers.
        head = None
        # An identifier, a reference, or a function call.
        tail = syntax
        if isinstance(syntax, SpecifierSyntax):
            head = syntax.lbranch
            tail = syntax.rbranch
        # Parse and validate the qualifier.
        if head is not None:
            while isinstance(head, SpecifierSyntax):
                syntax = head.rbranch
                if not isinstance(syntax, IdentifierSyntax):
                    raise BindError("an identifier is expected",
                                    syntax.mark)
                terms.insert(0, (syntax.value, False))
                head = head.lbranch
            if not isinstance(head, IdentifierSyntax):
                raise BindError("an identifier is expected", head.mark)
            terms.insert(0, (head.value, False))
        # Parse and validate the target identifier, reference or function call.
        if isinstance(tail, IdentifierSyntax):
            terms.append((tail.value, False))
        elif isinstance(tail, ReferenceSyntax):
            terms.append((tail.identifier.value, True))
        elif isinstance(tail, FunctionSyntax):
            terms.append((tail.name, False))
            parameters = []
            for argument in tail.arguments:
                if isinstance(argument, IdentifierSyntax):
                    parameters.append((argument.value, False))
                elif isinstance(argument, ReferenceSyntax):
                    parameters.append((argument.identifier.value, True))
                else:
                    raise BindError("an identifier is expected",
                                    argument.mark)
        else:
            raise BindError("an identifier is expected", tail.mark)
        # The right side of the assignment expression.
        body = self.syntax.rbranch
        # Generate an assignment node.
        return AssignmentBinding(self.state.scope, terms, parameters, body,
                                 self.syntax)


class BindSpecifier(Bind):

    adapts(SpecifierSyntax)

    def __call__(self):
        # Expression:
        #   parent . child
        # evaluates `child` in the scope of `parent`.
        scope = self.state.bind(self.syntax.lbranch)
        binding = self.state.bind(self.syntax.rbranch, scope=scope)
        return binding


class BindGroup(Bind):

    adapts(GroupSyntax)

    def __call__(self):
        # Bind the expression in parenthesis, then wrap the result
        # to attach the original syntax node.
        binding = self.state.bind(self.syntax.branch)
        return WrappingBinding(binding, self.syntax)


class BindIdentifier(Bind):

    adapts(IdentifierSyntax)

    def __call__(self):
        # Look for the identifier in the current lookup scope.
        recipe = lookup_attribute(self.state.scope, self.syntax.value)
        if recipe is not None:
            binding = self.state.use(recipe, self.syntax)
        # If not found, try the global scope.
        else:
            binding = self.state.call(self.syntax)
        return binding


class BindWildcard(Bind):

    adapts(WildcardSyntax)

    def __call__(self):
        # Get all public columns in the current lookup scope.
        recipes = expand(self.state.scope)
        if recipes is None:
            raise BindError("cannot expand '*' since output columns"
                            " are not defined", self.syntax.mark)
        # If a position is given, extract a specific element.
        if self.syntax.index is not None:
            try:
                index = int(self.syntax.index.value)
            except ValueError:
                raise BindError("an integer value is required",
                                self.syntax.mark)
            index -= 1
            if not (0 <= index < len(recipes)):
                raise BindError("value in range 1-%s is required"
                                % len(recipes), self.syntax.mark)
            syntax, recipe = recipes[index]
            syntax = syntax.clone(mark=self.syntax.mark)
            return self.state.use(recipe, syntax)
        # Otherwise, generate a selection node.
        elements = []
        for syntax, recipe in recipes:
            syntax = syntax.clone(mark=self.syntax.mark)
            element = self.state.use(recipe, syntax)
            elements.append(element)
        return SelectionBinding(self.state.scope, elements, self.syntax)


class BindReference(Bind):

    adapts(ReferenceSyntax)

    def __call__(self):
        # Look for a reference, complain if not found.
        recipe = lookup_reference(self.state.scope,
                                  self.syntax.identifier.value)
        if recipe is None:
            model = self.syntax.identifier.value.lower()
            names = lookup_reference_set(self.state.scope)
            choices = [u"$"+name for name in sorted(names)
                                 if similar(model, name)]
            hint = hint_choices(choices)
            raise BindError("unrecognized reference '%s'"
                            % self.syntax, self.syntax.mark,
                            hint=hint)
        return self.state.use(recipe, self.syntax)


class BindComplement(Bind):

    adapts(ComplementSyntax)

    def __call__(self):
        # Look for a complement, complain if not found.
        recipe = lookup_complement(self.state.scope)
        if recipe is None:
            raise BindError("'^' could only be used in a quotient scope",
                            self.syntax.mark)
        return self.state.use(recipe, self.syntax)


class BindString(Bind):

    adapts(StringSyntax)

    def __call__(self):
        # Bind a quoted literal.  Note that a quoted literal not necessarily
        # represents a string value; its initial domain is untyped.
        binding = LiteralBinding(self.state.scope,
                                 self.syntax.value,
                                 UntypedDomain(),
                                 self.syntax)
        return binding


class BindNumber(Bind):

    adapts(NumberSyntax)

    def __call__(self):
        # Bind an unquoted (numeric) literal.

        # Create an untyped literal binding.
        binding = LiteralBinding(self.state.scope,
                                 self.syntax.value,
                                 UntypedDomain(),
                                 self.syntax)

        # Cast the binding to an appropriate numeric type.
        if self.syntax.is_exponential:
            domain = coerce(FloatDomain())
        elif self.syntax.is_decimal:
            domain = coerce(DecimalDomain())
        elif self.syntax.is_integer:
            domain = coerce(IntegerDomain())
        binding = CastBinding(binding, domain, self.syntax)
        return binding


class BindByName(Protocol):
    """
    Binds a application node.

    This is an abstract protocol interface that provides a mechanism
    for name-based dispatch of application syntax nodes.

    The :class:`BindByName` interface has the following signature::

        BindByName: (ApplicationSyntax, BindingState) -> Binding
        BindByName: (IdentifierSyntax, BindingState) -> Binding

    The protocol is polymorphic on the name and the number of arguments
    of the syntax node.

    To add an implementation of the interface, define a subclass
    of :class:`BindByName` and specify its name and expected number
    of arguments using function :func:`named`.

    Class attributes:

    `names` (a list of names or pairs `(name, length)`)
        List of names the component matches.

        Here `name` is a non-empty string, `length` is an integer or
        ``None``, where ``-1`` indicates any number of arguments, ``None``
        means no arguments are accepted.
    """

    names = []

    @classmethod
    def dominates(component, other):
        # Determine if the component dominates another component
        # assuming that they match the same dispatch key.

        # A component implementing a protocol interface dominates
        # another component if one of the following two conditions
        # holds:

        # (1) The component is a subclass of the other component.
        if issubclass(component, other):
            return True

        # (2) The component and the other component match the
        # same name, but the former requires a fixed number of
        # arguments while the latter accepts a node with any
        # number of arguments.
        for name in component.names:
            arity = -1
            if isinstance(name, tuple):
                name, arity = name
            name = name.lower()
            for other_name in other.names:
                other_arity = -1
                if isinstance(other_name, tuple):
                    other_name, other_arity = other_name
                other_name = other_name.lower()
                if name == other_name:
                    if arity != -1 and other_arity == -1:
                        return True

        return False

    @classmethod
    def matches(component, dispatch_key):
        # Check if the component matches the given function name
        # and the number of arguments.
        assert isinstance(dispatch_key, tupleof(unicode, maybe(int)))

        # The name and the number of arguments of the call node.
        key_name, key_arity = dispatch_key
        # We want to compare names case insensitive.  Unfortunately,
        # we cannot use `normalize` from `htsql.tr.lookup` since it
        # mangles symbols.
        key_name = key_name.lower()

        # Check if any of the component names matches the given name.
        for name in component.names:
            # `name` could be either a string or a pair of a string
            # and an integer.  The former assumes that the component
            # accepts call nodes with any number of arguments.
            arity = -1
            if isinstance(name, tuple):
                name, arity = name
            name = name.lower()
            # Check if the component name matches the node name.
            if name == key_name:
                if ((arity == key_arity) or
                        (arity == -1 and key_arity is not None)):
                    return True

        # None of the names matched the dispatch key.
        return False

    @classmethod
    def dispatch(interface, syntax, *args, **kwds):
        assert isinstance(syntax, (ApplicationSyntax, IdentifierSyntax))
        # We override `dispatch` since, as opposed to regular protocol
        # interfaces, we also want to take into account not only the
        # function name, but also the number of arguments.
        if isinstance(syntax, ApplicationSyntax):
            name = syntax.name
            arity = len(syntax.arguments)
        elif isinstance(syntax, IdentifierSyntax):
            name = syntax.value
            arity = None
        return (name, arity)

    def __init__(self, syntax, state):
        assert isinstance(syntax, (ApplicationSyntax, IdentifierSyntax))
        assert isinstance(state, BindingState)
        self.syntax = syntax
        self.state = state
        # Extract commonly accessed attributes of the call node.
        if isinstance(syntax, ApplicationSyntax):
            self.name = syntax.name
            self.arguments = syntax.arguments
        elif isinstance(syntax, IdentifierSyntax):
            self.name = syntax.value
            self.arguments = None

    def __call__(self):
        # The default implementation; override in subclasses.
        hint = None
        # Generate a hint with a list of alternative names.
        model = self.name.lower()
        arity = None
        if self.arguments is not None:
            arity = len(self.arguments)
        attributes = lookup_attribute_set(self.state.scope)
        global_attributes = set()
        for component in BindByName.implementations():
            for component_name in component.names:
                component_arity = -1
                if isinstance(component_name, tuple):
                    component_name, component_arity = component_name
                if isinstance(component_name, str):
                    component_name = component_name.decode('utf-8')
                component_name = component_name.lower()
                global_attributes.add((component_name, component_arity))
        all_attributes = sorted(attributes|global_attributes)
        if hint is None and arity is None:
            names = lookup_reference_set(self.state.scope)
            if model in names:
                hint = "did you mean: a reference '$%s'" % model.encode('utf-8')
        if hint is None and arity is None:
            if any(model == sample
                   for sample, sample_arity in all_attributes
                   if sample_arity is not None):
                hint = "did you mean: a function '%s'" % model.encode('utf-8')
        if hint is None and arity is None:
            choices = [sample
                       for sample, sample_arity in all_attributes
                       if sample_arity is None and sample != model
                            and similar(model, sample)]
            hint = hint_choices(choices)
        if hint is None and arity is not None \
                and not isinstance(self.syntax, OperatorSyntax):
            arities = [sample_arity
                       for sample, sample_arity in all_attributes
                       if sample == model and
                            sample_arity not in [None, -1, arity]]
            if arities:
                required_arity = []
                arities.sort()
                if len(arities) == 1:
                    required_arity.append(str(arities[0]))
                else:
                    required_arity.append(", ".join(str(sample_arity)
                                    for sample_arity in arities[:-1]))
                    required_arity.append("or")
                    required_arity.append(str(arities[-1]))
                if required_arity[-1] == "1":
                    required_arity.append("argument")
                else:
                    required_arity.append("arguments")
                required_arity = " ".join(required_arity)
                raise BindError("function '%s' requires %s; got %s"
                                % (self.syntax.identifier,
                                   required_arity, arity),
                                self.syntax.mark)
        if hint is None and arity is not None:
            if any(model == sample
                   for sample, sample_arity in all_attributes
                   if sample_arity is None):
                hint = "did you mean: an attribute '%s'" % model.encode('utf-8')
        if hint is None and arity is not None:
            choices = [sample
                       for sample, sample_arity in all_attributes
                       if sample_arity in [-1, arity] and sample != model
                            and similar(model, sample)]
            hint = hint_choices(choices)
        scope_name = guess_name(self.state.scope)
        if scope_name is not None:
            scope_name = scope_name.encode('utf-8')
        if isinstance(self.syntax, (FunctionSyntax, MappingSyntax)):
            raise BindError("unrecognized function '%s'"
                            % self.syntax.identifier,
                            self.syntax.mark, hint=hint)
        if isinstance(self.syntax, OperatorSyntax):
            raise BindError("unrecognized operator '%s'"
                            % self.syntax.symbol.encode('utf-8'),
                            self.syntax.mark, hint=hint)
        if isinstance(self.syntax, IdentifierSyntax):
            raise BindError("unrecognized attribute '%s'%s"
                            % (self.syntax,
                               " in scope of '%s'" % scope_name
                               if scope_name is not None else ""),
                            self.syntax.mark, hint=hint)


class BindByRecipe(Adapter):
    """
    Applies a recipe to generate a binding node.

    This is an abstract adapter that generates new binding nodes
    from binding recipes.  The :class:`BindByRecipe` interface
    has the following signature::

        BindByRecipe: (Recipe, Syntax, BindingState) -> Binding

    The adapter is polymorphic by the first argument.

    `recipe` (:class:`htsql.tr.binding.Recipe`)
        A recipe to apply.

    `syntax` (:class:`htsql.tr.syntax.Syntax`)
        The syntax node associated with the recipe.

    `state` (:class:`BindingState`)
        The current binding state.
    """

    adapts(Recipe)

    def __init__(self, recipe, syntax, state):
        assert isinstance(recipe, Recipe)
        assert isinstance(syntax, Syntax)
        assert isinstance(state, BindingState)
        self.recipe = recipe
        self.syntax = syntax
        self.state = state

    def __call__(self):
        # The default implementation should not be reachable.
        raise BindError("unable to bind a node", self.syntax.mark)


class BindByLiteral(BindByRecipe):

    adapts(LiteralRecipe)

    def __call__(self):
        return LiteralBinding(self.state.scope,
                              self.recipe.value,
                              self.recipe.domain,
                              self.syntax)


class BindBySelection(BindByRecipe):

    adapts(SelectionRecipe)

    def __call__(self):
        elements = []
        for recipe in self.recipe.recipes:
            element = self.state.use(recipe, self.syntax)
            elements.append(element)
        return SelectionBinding(self.state.scope, elements, self.syntax)


class BindByFreeTable(BindByRecipe):

    adapts(FreeTableRecipe)

    def __call__(self):
        # Produce a free table scope.
        return FreeTableBinding(self.state.scope,
                                self.recipe.table,
                                self.syntax)


class BindByAttachedTable(BindByRecipe):

    adapts(AttachedTableRecipe)

    def __call__(self):
        # Produce a sequence of joined tables.
        binding = self.state.scope
        for join in self.recipe.joins:
            binding = AttachedTableBinding(binding, join, self.syntax)
        return binding


class BindByColumn(BindByRecipe):

    adapts(ColumnRecipe)

    def __call__(self):
        # Generate a link associated with the column.
        link = None
        if self.recipe.link is not None:
            link = self.state.use(self.recipe.link, self.syntax)
        # Produce a column scope.
        return ColumnBinding(self.state.scope, self.recipe.column,
                             link, self.syntax)


class BindByKernel(BindByRecipe):

    adapts(KernelRecipe)

    def __call__(self):
        # Generate a kernel expression of a quotient scope.
        return KernelBinding(self.state.scope, self.recipe.quotient,
                             self.recipe.index, self.syntax)


class BindByComplement(BindByRecipe):

    adapts(ComplementRecipe)

    def __call__(self):
        # Generate a complement link to a quotient scope.
        return ComplementBinding(self.state.scope,
                                 self.recipe.quotient, self.syntax)


class BindBySubstitution(BindByRecipe):

    adapts(SubstitutionRecipe)

    def __call__(self):
        # Bind the given syntax node in place of an identifier
        # or a function call.

        # Check if the recipe has a qualifier.
        if self.recipe.terms:
            # Find the same identifier in the base scope.
            assert isinstance(self.syntax, IdentifierSyntax)
            name, is_reference = self.recipe.terms[0]
            arity = None
            if (len(self.recipe.terms) == 1 and
                    self.recipe.parameters is not None):
                arity = len(self.recipe.parameters)
            recipe = lookup_attribute(self.recipe.base, self.syntax.value)
            if recipe is None:
                raise BindError("unrecognized attribute '%s'" % self.syntax,
                                self.syntax.mark)
            binding = self.state.use(recipe, self.syntax)
            # Check if the term is a reference.
            if is_reference:
                # Must the the last term in the assignment.
                assert len(self.recipe.terms) == 1
                # Bind the reference against the scope where it is defined.
                body = self.state.bind(self.recipe.body, scope=binding)
                recipe = BindingRecipe(body)
            # Augment the scope with the tail of the recipe.
            else:
                recipe = SubstitutionRecipe(binding, self.recipe.terms[1:],
                                            self.recipe.parameters,
                                            self.recipe.body)
            recipe = ClosedRecipe(recipe)
            binding = DefinitionBinding(binding, name, is_reference, arity,
                                        recipe, self.syntax)
            return binding

        # Otherwise, bind the syntax node associated with the recipe.
        # Bind against the current scope, but route all lookup requests
        # to the scope where the recipe was defined.
        scope = self.state.scope
        scope = RerouteBinding(scope, self.recipe.base, scope.syntax)
        # Bind the parameters.
        if self.recipe.parameters is not None:
            assert isinstance(self.syntax, ApplicationSyntax)
            assert len(self.syntax.arguments) == len(self.recipe.parameters)
            for (name, is_reference), syntax in zip(self.recipe.parameters,
                                                    self.syntax.arguments):
                binding = self.state.bind(syntax)
                recipe = BindingRecipe(binding)
                recipe = ClosedRecipe(recipe)
                scope = DefinitionBinding(scope, name, is_reference, None,
                                          recipe, scope.syntax)
        # Bind the syntax node associated with the recipe.
        binding = self.state.bind(self.recipe.body, scope=scope)
        # Hide all referenced defined there.
        binding = ReferenceRerouteBinding(binding, self.state.scope,
                                          binding.syntax)
        return binding


class BindByBinding(BindByRecipe):

    adapts(BindingRecipe)

    def __call__(self):
        return self.recipe.binding


class BindByClosed(BindByRecipe):

    adapts(ClosedRecipe)

    def __call__(self):
        # Generate a binding from the given recipe.
        binding = self.state.use(self.recipe.recipe, self.syntax)
        # Force the current syntax node to the binding.
        return AliasBinding(binding, self.syntax)


class BindByPinned(BindByRecipe):

    adapts(PinnedRecipe)

    def __call__(self):
        # Bind the given recipe in the specified scope.
        binding = self.state.use(self.recipe.recipe, self.syntax,
                                 scope=self.recipe.scope)
        return binding


class BindByAmbiguous(BindByRecipe):

    adapts(AmbiguousRecipe)

    def __call__(self):
        syntax = self.syntax
        if isinstance(self.syntax, (FunctionSyntax, MappingSyntax)):
            syntax = self.syntax.identifier
        hint = None
        if self.recipe.alternatives:
            alternatives = self.recipe.alternatives
            choices = ["try "]
            if len(alternatives) == 1:
                choices.append(repr(alternatives[0].encode('utf-8')))
            else:
                choices.extend(", ".join(repr(alternative.encode('utf-8'))
                                         for alternative in alternatives[:-1]))
                choices.append(" or ")
                choices.append(repr(alternatives[-1].encode('utf-8')))
            hint = "".join(choices)
        raise BindError("ambiguous name '%s'" % syntax,
                        self.syntax.mark, hint=hint)


def bind(syntax, state=None, scope=None, environment=None):
    """
    Binds the given syntax node.

    `syntax` (:class:`htsql.tr.syntax.Syntax`)
        The syntax node to bind.

    `state` (:class:`BindingState` or ``None``).
        The binding state to use.  If not set, a new binding state
        is created.

    `scope` (:class:`htsql.tr.binding.Binding` or ``None``)
        If specified, updates the lookup scope when binding
        the node.
    """
    # Create a new binding state if necessary.
    if state is None:
        state = BindingState(environment)
    # If passed, set the new lookup scope.
    if scope is not None:
        state.push_scope(scope)
    # Realize and apply the `Bind` adapter.
    bind = Bind(syntax, state)
    binding = bind()
    # Restore the old lookup scope.
    if scope is not None:
        state.pop_scope()
    # Return the binding node.
    return binding


