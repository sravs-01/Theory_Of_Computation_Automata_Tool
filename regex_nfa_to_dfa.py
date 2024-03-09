from graphviz import Digraph
from time import sleep
from regular_language_utils import *
from collections import defaultdict
from pprint import pprint

class State:
    def __init__(self, name):
        self.name = name
        self.transitions = defaultdict(set)
        self.transitions["E"] = {self}

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
    infix_regex = regex
    postfix_regex = ''
    stack = Stack()

    for token in infix_regex:
        if isSymbol(token):
            postfix_regex += token
        elif token == '(':
            stack.push(token)
        elif token == ')':
            while not stack.empty() and stack.top() != '(':
                postfix_regex += stack.pop()
            stack.pop()  # Discard '('
        elif isOperator(token):
            while not stack.empty() and precedenceOf(stack.top()) >= precedenceOf(token):
                postfix_regex += stack.pop()
            stack.push(token)

    while not stack.empty():
        postfix_regex += stack.pop()

    print('postfix regex:', postfix_regex)

    nfa_stack = Stack()

    for token in postfix_regex:
        if isSymbol(token):
            # Create a new NFA state for the symbol
            new_state = State(token)
            nfa_stack.push(new_state)
        elif isOperator(token):
            if token == '*':
                A = nfa_stack.pop()
                # Create an epsilon closure state
                epsilon_state = State('eps_' + A.get_name())
                # Add epsilon transitions from epsilon state to A and back
                epsilon_state.add_transition(epsilon_state, 'E')
                epsilon_state.add_transition(A, 'E')
                A.add_transition(epsilon_state, 'E')
                nfa_stack.push(epsilon_state)  # Push epsilon closure state
            elif token == '.':
                B = nfa_stack.pop()
                A = nfa_stack.pop()
                # Add transition from A to B on any symbol
                A.add_transition(B, B.get_name())  # Use symbol name as transition label
                nfa_stack.push(A)
            elif token == '+':
                B = nfa_stack.pop()
                A = nfa_stack.pop()
                # Create epsilon closure states for A and B
                epsilon_state_A = State('eps_' + A.get_name())
                epsilon_state_B = State('eps_' + B.get_name())
                # Add epsilon transitions for closure
                epsilon_state_A.add_transition(epsilon_state_A, 'E')
                epsilon_state_B.add_transition(epsilon_state_B, 'E')
                A.add_transition(epsilon_state_A, 'E')
                B.add_transition(epsilon_state_B, 'E')
                # Connect epsilon states with original states
                epsilon_state_A.add_transition(B, 'E')
                epsilon_state_B.add_transition(A, 'E')
                nfa_stack.push(epsilon_state_A)  # Push combined epsilon closure

    # After processing, the top of the stack holds the final NFA
    if not nfa_stack.empty() and isinstance(nfa_stack.top(), State):
        initial_state = State('INITIAL_STATE')  # Create a new State for the initial state
        nfa = Automata(set(state.get_name() for state in nfa_stack.top().transitions.keys()),
                    set(transition for state in nfa_stack.top().transitions.values() for transition in state),
                    initial_state,  # Use the new initial state
                    set(state.get_name() for state in nfa_stack.top().get_final()))
        print("Grouped regex:", nfa)
        return convert_epsilon_nfa_to_dfa(nfa)
    else:
        print("Empty stack after processing.")
        return None

# Function to convert epsilon-NFA to NFA (modified to handle epsilon transitions)
def convert_epsilon_nfa_to_dfa(epsilon_nfa):
    nfa_states = {}
    epsilon_closure_cache = {}

    def epsilon_closure(states):
        closure = set()
        stack = list(states)

        while stack:
            current_state = stack.pop()
            if current_state not in closure:
                closure.add(current_state)
                transitions = current_state.transitions.get("E", set())
                stack.extend(transitions)

        return closure

    for state_name, state_obj in epsilon_nfa.states.items():
        nfa_states[state_name] = set()
        epsilon_closure_set = epsilon_closure({state_name})
        nfa_states[state_name].update(epsilon_closure_set)

    # Build the DFA
    sigma = epsilon_nfa.get_sigma()
    init = epsilon_nfa.get_init()
    final = epsilon_nfa.get_final()

    for state_name, state_obj in nfa_states.items():
        for symbol in sigma:
            target_states = set()
            for epsilon_state_name in nfa_states[state_name]:
                target_states.update(epsilon_nfa.states[epsilon_state_name].get(symbol, set()))
            target_states_closure = epsilon_closure(target_states)
            epsilon_nfa.states[state_name].transitions[symbol] = target_states_closure

    return epsilon_nfa

def get_user_input():
    regex = input("Enter a regular expression: ")
    alphabet = set(regex) - set('()|*')
    extra = ''
    alphabet = alphabet.union(set(extra))

    F = input("Enter final states (comma-separated): ").split(',')

    return regex, alphabet, F

def stringify(state):
    return '{' + ','.join(state) + '}'

def build_dfa(Q, q0, alphabet, delta_dict, F):
    dot = Digraph()
    dot.graph_attr['rankdir'] = 'LR'
    dot.node_attr['shape'] = 'circle'

    dfa_states = [[q0]]
    dfa_delta = []
    new_dfa_states = [[q0]]

    while len(new_dfa_states) > 0:
        current_state = new_dfa_states[0]
        new_dfa_states = new_dfa_states[1:]

        print('Current state: ', current_state)

        for symbol in alphabet:
            next_states = []
            for nfa_state in current_state:
                for x in delta_dict[nfa_state][symbol]:
                    if x not in next_states:
                        next_states.append(x)
            next_states = sorted(next_states)
            dfa_delta.append([current_state, symbol, next_states])
            print('Symbol: ', symbol, ' States: ', next_states)

            if next_states not in dfa_states:
                dfa_states.append(next_states)
                new_dfa_states.append(next_states)
        print()

    print('dfa_states', dfa_states)
    print()

    print('dfa_delta')
    pprint(dfa_delta)

    for state in dfa_states:
        name = stringify(state)
        dot.node(name, name)

    for transition in dfa_delta:
        x, s, y = transition
        nameX = stringify(x)
        nameY = stringify(y)
        dot.edge(nameX, nameY, label=s)

    dot.node('BEGIN', '', shape='none')
    dot.edge('BEGIN', stringify([q0]), label='start')

    for dfa_state in dfa_states:
        for final_state in F:
            if final_state in dfa_state:
                name = stringify(dfa_state)
                dot.node(name, name, shape='doublecircle')

    dot.render(filename='gv_dfa_nfa', view=True)

def test_dfa(dfa_states, delta_dict, q0, F):
    while True:
        input_str = input("Enter a string to test (type 'exit' to stop): ")
        if input_str.lower() == 'exit':
            break

        q = [q0]
        for symbol in input_str:
            next_states = []
            for nfa_state in q:
                if symbol in delta_dict[nfa_state]:
                    next_states.extend(delta_dict[nfa_state][symbol])

            if not next_states:
                print(f"No transition for symbol '{symbol}' in current state(s) {q}.")
                break

            q = sorted(list(set(next_states)))

        accepted = any(set(q) & set(F))
        if accepted:
            print("Accepted!")
        else:
            print("Not accepted.")

def convert_nfa_to_dfa(alphabet, delta_dict, F):
    dfa_states = []
    dfa_delta = []

    q0 = ['BEGIN']  # Assuming you have a special start state 'BEGIN'
    new_dfa_states = [q0]

    while new_dfa_states:
        current_state = new_dfa_states.pop(0)
        dfa_states.append(current_state)

        for symbol in alphabet:
            next_states = []
            for nfa_state in current_state:
                next_states.extend(delta_dict[nfa_state][symbol])

            next_states = sorted(list(set(next_states)))

            if next_states not in dfa_states:
                new_dfa_states.append(next_states)

            dfa_delta.append([current_state, symbol, next_states])

    return dfa_states, dfa_delta

def build_nfa(alphabet, delta_dict, F):
    dot = Digraph()
    dot.graph_attr['rankdir'] = 'LR'
    dot.node_attr['shape'] = 'circle'

    nfa_states = set()
    for state in delta_dict:
        nfa_states.add(state)
        for symbol, next_states in delta_dict[state].items():
            nfa_states.update(next_states)

    for state in nfa_states:
        dot.node(state, state)

    for state in delta_dict:
        for symbol, next_states in delta_dict[state].items():
            for next_state in next_states:
                dot.edge(state, next_state, label=symbol)

    dot.node('BEGIN', '', shape='none')
    dot.edge('BEGIN', start_state, label='start')

    for final_state in F:
        dot.node(final_state, final_state, shape='doublecircle')

    dot.render(filename='gv_nfa', view=True)

if __name__ == "__main__":
    regex, alphabet, F = get_user_input()

    # Convert regex to NFA
    nfa = convert_to_nfa(regex)

    # Check if nfa is None before trying to build and display
    if nfa is not None:
        # Build NFA
        build_nfa(nfa.get_sigma(), nfa.get_states(), nfa.get_final())

        # Convert NFA to DFA and build DFA
        dfa_states, dfa_delta = convert_nfa_to_dfa(nfa.get_sigma(), nfa.get_states(), nfa.get_final())
        build_dfa(dfa_states, dfa_delta, nfa.get_final())

        # Testing
        test_dfa(dfa_states, dfa_delta, dfa_states[0], nfa.get_final())
    else:
        print("Error: Unable to convert regex to NFA.")