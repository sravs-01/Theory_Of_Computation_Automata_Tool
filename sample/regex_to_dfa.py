import json
from graphviz import Digraph

# NFA info
states = []
letters = []
transition_function = []
final_states = []
start_states = ["Q0"]

possible_expressions = ["*", "#", "+"]

# Helpers
all_from_states = []
all_to_states = []

# Symbols, types of operations
INPUT_SYMBOL = 0
CONCATENATE_EXPRESSION = 1
UNION_EXPRESSION = 2
KLEENE_STAR_EXPRESSION = 3

class RegexTree:
    def __init__(self, char_type, value=None, left_child=None, right_child=None):
        self.char_type = char_type
        self.value = value
        self.left_child = left_child
        self.right_child = right_child
        
class State:
    def __init__(self):
        self.to_state = {}
  
def obtain_regular_expression_tree(regular_expression):
    tree_stack = []
    for curr_char in regular_expression:
        if not curr_char.isalnum():
            if curr_char == "*":
                left_child = tree_stack.pop()
                new_reg_tree = RegexTree(char_type=KLEENE_STAR_EXPRESSION, value=None, left_child=left_child, right_child=None)
            elif curr_char == "+":
                right_child = tree_stack.pop()
                left_child = tree_stack.pop()
                new_reg_tree = RegexTree(char_type=UNION_EXPRESSION, value=None, left_child=left_child, right_child=right_child)
            elif curr_char == "#":
                right_child = tree_stack.pop()
                left_child = tree_stack.pop()
                new_reg_tree = RegexTree(char_type=CONCATENATE_EXPRESSION, value=None, left_child=left_child, right_child=right_child)
            tree_stack.append(new_reg_tree)
        else:
            new_reg_tree = RegexTree(char_type=INPUT_SYMBOL, value=curr_char, left_child=None, right_child=None)
            tree_stack.append(new_reg_tree)
    return tree_stack[0]

def is_concatenation(regular_expression, i):
    if i == 0:
        return False
    if not (regular_expression[i-1].isalnum() or regular_expression[i-1] in [")", "*"]):
        return False
    if not (regular_expression[i].isalnum() or regular_expression[i] == "("):
        return False
    return True

def convert_to_postfix(regular_expression):
    global possible_expressions
    updated_regular_expression = []
    for i in range(len(regular_expression)):
        if is_concatenation(regular_expression, i):
            updated_regular_expression.append("#")
        updated_regular_expression.append(regular_expression[i])
    regular_expression = updated_regular_expression 
    operators_stack = []
    output_queue = ""
    for curr_char in regular_expression:
        if curr_char.isalnum() or curr_char == "*":
            output_queue = output_queue + curr_char
        elif curr_char == "(":
            operators_stack.append(curr_char)
        elif curr_char == ")":
            while len(operators_stack) != 0 and operators_stack[-1] != "(":
                output_queue = output_queue + operators_stack.pop()
            operators_stack.pop()
        elif len(operators_stack) == 0 or operators_stack[-1] == "(" or possible_expressions.index(curr_char) < possible_expressions.index(operators_stack[-1]):
            operators_stack.append(curr_char)
        else:
            while len(operators_stack) != 0 and operators_stack[-1] != "(" and not possible_expressions.index(curr_char) < possible_expressions.index(operators_stack[-1]):
                output_queue = output_queue + operators_stack.pop()
            operators_stack.append(curr_char)
    while len(operators_stack) != 0:
        output_queue = output_queue + operators_stack.pop()
    return output_queue

def parseRegularExpression(regular_expression_tree):
    if regular_expression_tree.char_type == UNION_EXPRESSION:
        return parseRegularExpressionUnion(regular_expression_tree)
    if regular_expression_tree.char_type == CONCATENATE_EXPRESSION:
        return parseRegularExpressionConcatenation(regular_expression_tree)
    if regular_expression_tree.char_type == INPUT_SYMBOL:
        return parseRegularExpressionSymbol(regular_expression_tree)
    return parseRegularExpressionKleeneStar(regular_expression_tree)

def parseRegularExpressionSymbol(regular_expression_tree):
    f_state = State()
    t_state   = State()  
    f_state.to_state[regular_expression_tree.value] = [t_state]
    return f_state, t_state

def parseRegularExpressionConcatenation(regular_expression_tree):
    nfa_1  = parseRegularExpression(regular_expression_tree.left_child)
    nfa_2 = parseRegularExpression(regular_expression_tree.right_child)
    nfa_1[1].to_state['$'] = [nfa_2[0]]
    return nfa_1[0], nfa_2[1]

def parseRegularExpressionUnion(regular_expression_tree):
    f_state = State()
    t_state   = State()
    nfa_1   = parseRegularExpression(regular_expression_tree.left_child)
    nfa_2 = parseRegularExpression(regular_expression_tree.right_child)
    f_state.to_state['$'] = [nfa_1[0], nfa_2[0]]
    nfa_1[1].to_state['$'] = [t_state]
    nfa_2[1].to_state['$'] = nfa_1[1].to_state['$']
    return f_state, t_state

def parseRegularExpressionKleeneStar(regular_expression_tree):
    f_state = State()
    t_state   = State()
    sub_nfa = parseRegularExpression(regular_expression_tree.left_child)
    f_state.to_state['$'] = [sub_nfa[0], t_state]
    sub_nfa[1].to_state['$'] = f_state.to_state['$']
    return f_state, t_state

def obtainNFA(curr_state, visited_states, list_of_symbols, final_state):
    global states
    global letters
    global transition_function
    global all_from_states
    global all_to_states
    global final_states
    if curr_state == final_state:
        final_states = ["Q" + str(list_of_symbols[final_state])]
    if curr_state not in visited_states:
        visited_states.append(curr_state)
        for symbol in list(curr_state.to_state):
            
            original_state = "Q" + str(list_of_symbols[curr_state])
            if original_state not in states:
                states.append(original_state)
            if original_state not in all_from_states:
                all_from_states.append(original_state)
                
            input_letter = symbol
            if input_letter not in letters:
                letters.append(input_letter)
                
            for ns in curr_state.to_state[symbol]:
                if ns not in list_of_symbols:
                    list_of_symbols[ns] = 1 + sorted(list_of_symbols.values())[-1]
                
                new_state = "Q" + str(list_of_symbols[ns])
                if new_state not in states:
                    states.append(new_state)
                if new_state not in all_to_states:
                    all_to_states.append(new_state)
                    
                transition_function.append([original_state, input_letter, new_state])
                 
            for ns in curr_state.to_state[symbol]:
                obtainNFA(ns, visited_states, list_of_symbols, final_state)

# Read input from input.json
try:
    regex = input("Enter the regular expression: ")

    postfix_regex = convert_to_postfix(regex)
    regular_expression_tree = obtain_regular_expression_tree(postfix_regex)
    finite_automata = parseRegularExpression(regular_expression_tree)
    obtainNFA(finite_automata[0], [], {finite_automata[0]: 0}, finite_automata[1])

    NFA = {
        "states": states,
        "letters": letters,
        "transition_function": transition_function,
        "start_states": start_states,
        "final_states": final_states
    }

    # Write output to output.json
    with open('output.json', 'w') as f:
        json.dump(NFA, f, indent=4)
    
    # Read output from output.json
    with open('output.json', 'r') as f:
        nfa_data = json.load(f)

    # Create a Digraph object
    dot = Digraph(comment='NFA')

    # Add states to the diagram
    for state in nfa_data['states']:
        dot.node(state)

    # Add transitions to the diagram
    for transition in nfa_data['transition_function']:
        dot.edge(transition[0], transition[2], label=transition[1])

    # Save the diagram to a file
    dot.render('nfa_diagram', format='png', cleanup=True)

    print("NFA diagram generated successfully.")

except Exception as e:
    print(f"An error occurred: {e}")
