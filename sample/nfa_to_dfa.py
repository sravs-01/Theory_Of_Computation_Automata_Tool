from graphviz import Digraph
from pprint import pprint

from tabulate import tabulate as tb

def get_user_input():
    Q = input("Enter NFA states (comma-separated): ").split(',')
    q0 = input("Enter initial state: ")
    alphabet = input("Enter alphabet symbols (comma-separated): ").split(',')
    
    delta = []
    print("Enter transitions (enter 'done' to finish): ")
    while True:
        transition = input("Enter transition (e.g., A,0,B): ")
        if transition.lower() == 'done':
            break
        delta.append(transition.split(','))

    F = input("Enter final states (comma-separated): ").split(',')

    return Q, q0, alphabet, delta, F

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

    # Print Transition Table
    header = ['State'] + alphabet
    table_data = []
    for state in dfa_states:
        row = [stringify(state)]
        for symbol in alphabet:
            next_states = []
            for transition in dfa_delta:
                if transition[0] == state and transition[1] == symbol:
                    next_states = transition[2]
            row.append(stringify(next_states))
        table_data.append(row)

    print("\nTransition Table:")
    print(tb(table_data, headers=header, tablefmt='grid'))

    # Draw the DFA diagram
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

    dot.render(filename='gv_dfa.gv', view=True)
    
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

if __name__ == "__main__":
    Q, q0, alphabet, delta, F = get_user_input()

    # Preprocessing of input
    delta_dict = {}
    for state in Q:
        delta_dict[state] = {}
        for symbol in alphabet:
            delta_dict[state][symbol] = []

    for transition in delta:
        x, s, y = transition  # Extract x, s, and y from the transition tuple
        delta_dict[x][s].append(y)

    pprint(delta_dict)
    print()

    build_dfa(Q, q0, alphabet, delta_dict, F)

    # Testing
    test_dfa(Q, delta_dict, q0, F)
