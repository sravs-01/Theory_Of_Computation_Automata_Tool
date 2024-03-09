from graphviz import Digraph
from time import sleep
from regular_language_utils import *
from collections import defaultdict

class State:
    def __init__(self, name):
        self.name = name
        self.transitions = defaultdict(set)
        self.transitions["E"].add(self)

    def __str__(self):
        transitions_count = {key: len(transitions) for key, transitions in self.transitions.items()}
        return f"{{ State: {self.name} | Transitions: {transitions_count} }}"

    def add_transition(self, next_state, symbol):
        self.transitions[symbol].add(next_state)

    def get_transitions(self, symbol):
        return self.transitions[symbol]

    def get_name(self):
        return self.name

class Automata:
    def __init__(self, states, sigma, init, final):
        self.states = states
        self.sigma = sigma
        self.init = init
        self.final = final

    def get_states(self):
        return self.states

    def get_sigma(self):
        return self.sigma

    def get_init(self):
        return self.init

    def get_final(self):
        return self.final

class Stack:
    def __init__(self):
        self.stack = []

    def push(self, item):
        self.stack.append(item)

    def pop(self):
        return self.stack.pop()

    def empty(self):
        return len(self.stack) == 0

    def top(self):
        return self.stack[-1]

def isOperator(token):
    return token in ['*', '.', '+']

def isSymbol(token):
    return token.isalnum()

def precedenceOf(op):
    return ['+', '.', '*'].index(op) if op in ['+', '.', '*'] else -1

def convert_to_nfa(regex):
    infix_regex = regex[0]
    prev = regex[0]

    for i in range(1, len(regex)):
        if (isSymbol(regex[i]) and (isSymbol(prev) or prev == ')' or prev == '*')) or (regex[i] == '(' and isSymbol(prev)):
            infix_regex += '.'
        infix_regex += regex[i]
        prev = regex[i]

    infix_regex = '(' + infix_regex + ')'
    print('infix regex:', infix_regex)

    postfix_regex = ''
    stack = Stack()

    for token in infix_regex:
        if isSymbol(token):
            postfix_regex += token
        elif isOperator(token):
            while stack.top() != '(' and precedenceOf(stack.top()) >= precedenceOf(token):
                postfix_regex += stack.pop()
            stack.push(token)
        elif token == '(':
            stack.push(token)
        elif token == ')':
            while stack.top() != '(':
                postfix_regex += stack.pop()
            stack.pop()

    stack = Stack()

    for token in postfix_regex:
        if isSymbol(token):
            stack.push(token)
        else:
            if token == '*':
                A = stack.pop()
                stack.push(f'({A})*')
            elif token == '.':
                B = stack.pop()
                A = stack.pop()
                stack.push(f'({A}.{B})')
            elif token == '+':
                B = stack.pop()
                A = stack.pop()
                stack.push(f'({A}+{B})')

    print("Grouped regex:", stack.top())

    node_count = 0
    dot = Digraph()
    dot.graph_attr['rankdir'] = 'LR'
    dot.node_attr['shape'] = 'circle'

    stack = Stack()

    for token in postfix_regex:
        if isSymbol(token):
            symbol = token
            nodes = subgraphForSymbol(dot, symbol, node_count)
            node_count += 2
            stack.push(nodes)
        else:
            if token == '*':
                nodes = stack.pop()
                newNodes = subgraphForClosure(dot, nodes, node_count)
                node_count += 1
                stack.push(newNodes)
            elif token == '.':
                nodes1 = stack.pop()
                nodes0 = stack.pop()
                newNodes = subgraphForConcatenation(dot, nodes0, nodes1)
                stack.push(newNodes)
            elif token == '+':
                nodes1 = stack.pop()
                nodes0 = stack.pop()
                newNodes = subgraphForUnion(dot, nodes0, nodes1, node_count)
                node_count += 2
                stack.push(newNodes)

    finalNodes = stack.pop()

    dot.node('BEGIN', '', shape='none')
    dot.edge('BEGIN', finalNodes[0], label='start')
    dot.node(finalNodes[1], shape='doublecircle')

    sleep(2)

    dot.render(filename='nfa_demo.gv', view=True)

# Function to convert epsilon-NFA to NFA
def convert_epsilon_nfa_to_nfa(epsilon_nfa):
    nfa_states = {}
    epsilon_closure_cache = {}

    def epsilon_closure(state):
        if state not in epsilon_closure_cache:
            closure = set()
            stack = [state]

            while stack:
                current_state = stack.pop()
                closure.add(current_state)
                transitions = epsilon_nfa.getQ(current_state, "E")

                for next_state in transitions:
                    if next_state not in closure:
                        stack.append(next_state)

            epsilon_closure_cache[state] = closure

        return epsilon_closure_cache[state]

    for state_name, state_obj in epsilon_nfa.getQs().items():
        nfa_states[state_name] = set()
        epsilon_closure_set = epsilon_closure(state_name)

        for epsilon_state in epsilon_closure_set:
            nfa_states[state_name].update(epsilon_state.getQ("E"))

    # Build the NFA
    nfa_states_objects = {state_name: State(state_name) for state_name in nfa_states}
    sigma = epsilon_nfa.getSig()
    init = epsilon_nfa.getInit()
    final = epsilon_nfa.getFinal()

    for state_name, state_obj in nfa_states_objects.items():
        for symbol in sigma:
            target_states = set()
            for epsilon_state_name in nfa_states[state_name]:
                target_states.update(epsilon_state_name.getQ(symbol))
            target_states_closure = set()
            for target_state in target_states:
                target_states_closure.update(epsilon_closure(target_state))
            state_obj.addQ(target_states_closure, symbol)

    return Automata(nfa_states_objects, sigma, init, final)

# Example usage
regex_input = input("Enter a regular expression: ")
convert_to_nfa(regex_input)