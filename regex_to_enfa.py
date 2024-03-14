from cgitb import small
from graphviz import Digraph
import tempfile
from tabulate import tabulate as tb

EPSILON = "e"
OPERATORS = ["+", "*", ")", "(", "?"]
RANK_OPERATORS = ['+', '?', '*']
NFA_STACK = []
COUNTER = 0

def process(infix):
    newInfix = ""


    for index,char in enumerate(infix):
        newInfix = newInfix + char

        if index == len(infix)-1:
            break

        nextChar = infix[index+1]

        if char == ")" and nextChar == "(":
            newInfix = newInfix + "?"
        
        if char not in OPERATORS and nextChar == "(":
            newInfix = newInfix + "?"

        if char == ")" and nextChar not in OPERATORS:
            newInfix = newInfix + "?"

        if char not in OPERATORS and nextChar not in OPERATORS:
            newInfix = newInfix + "?"

        if char == "*" and nextChar not in OPERATORS:
            newInfix = newInfix + "?"

    return shunt(newInfix)

def shunt(infix):
    """
    Shunting-yard algorithm
    """
    output = []
    operatorStack = []
    for symbol in infix:
        if symbol == "(":
            operatorStack.append(symbol)
        elif symbol == ")":
            top_token = operatorStack.pop()
            while top_token != "(":
                output.append(top_token)
                top_token = operatorStack.pop()

        elif symbol in RANK_OPERATORS:
            while len(operatorStack) > 0 and operatorStack[-1] in RANK_OPERATORS and RANK_OPERATORS.index(symbol) <= RANK_OPERATORS.index(operatorStack[-1]):
                output.append(operatorStack.pop())
            operatorStack.append(symbol)

        else:
            output.append(symbol)

    while len(operatorStack) > 0:
        output.append(operatorStack.pop())

    return output

def regex_to_nfa(reg_exp):

    global NFA_STACK
    global COUNTER

    reg_exp = "".join(process(reg_exp))


    for symbol in reg_exp:
        nfa = {
        "states": [],  
        "initial_state": -1,  
        "final_states": [],  
        "alphabet": [],  
        "transition_function": {}  
        }

        if symbol == "*":

            left = NFA_STACK.pop()

            nfa["states"] = [COUNTER, COUNTER + 1] + left["states"]
            nfa["initial_state"] = COUNTER
            nfa["final_states"] = [COUNTER + 1]
            nfa["alphabet"] = left["alphabet"]
            nfa["transition_function"] = {
                COUNTER: {
                    EPSILON: [COUNTER + 1, left["initial_state"]],
                },
                COUNTER + 1: {}
            }

            nfa["transition_function"].update(left["transition_function"])

            for state in left["final_states"]:
                nfa["transition_function"][state] = {
                    EPSILON: [COUNTER + 1, left["initial_state"]]
                }

        elif symbol == "?":

            right = NFA_STACK.pop()
            left = NFA_STACK.pop()

            nfa["states"] = left["states"] + right["states"]
            nfa["initial_state"] = left["initial_state"]
            nfa["final_states"] = right["final_states"]
            nfa["alphabet"] = left["alphabet"] + right["alphabet"]
            nfa["transition_function"] = {
                COUNTER: {
                    EPSILON: [left["initial_state"]],
                },
                COUNTER + 1: {}
            }

            nfa["transition_function"].update(left["transition_function"])
            nfa["transition_function"].update(right["transition_function"])

            for state in left["final_states"]:
                nfa["transition_function"][state] = {
                    EPSILON: [right["initial_state"]]
                }
        
        elif symbol == "+":
    
            right = NFA_STACK.pop()
            left = NFA_STACK.pop()

            nfa["states"] = [COUNTER, COUNTER + 1] + left["states"] + right["states"]
            nfa["initial_state"] = COUNTER
            nfa["final_states"] = [COUNTER + 1]
            nfa["alphabet"] = left["alphabet"] + right["alphabet"]
            nfa["transition_function"] = {
                COUNTER: {
                    EPSILON: [left["initial_state"], right["initial_state"]],
                    
                },
                COUNTER + 1: {}
            }
            
            nfa["transition_function"].update(left["transition_function"])
            nfa["transition_function"].update(right["transition_function"])

            for state in left["final_states"]:
                nfa["transition_function"][state] = {
                    EPSILON: [COUNTER + 1]
                }
            for state in right["final_states"]:
                nfa["transition_function"][state] = {
                    EPSILON: [COUNTER + 1]
                }

        else:
            
            nfa["states"] = [COUNTER, COUNTER + 1]
            nfa["initial_state"] = COUNTER
            nfa["final_states"] = [COUNTER + 1]

            if symbol != "":
                
                nfa["alphabet"] = [symbol]
                nfa["transition_function"] = {
                    COUNTER: {
                        symbol: [COUNTER + 1]
                    },
                    COUNTER + 1: {}
                }

            elif symbol:

                nfa["alphabet"] = [""]
                nfa["transition_function"] = {
                    COUNTER: {
                        EPSILON: [COUNTER + 1]
                    },
                    COUNTER + 1: {}
                }

        NFA_STACK.append(nfa)
        COUNTER += 2    
    return nfa

def in_language(nfa, s):
    InLang = 0
    InLang += in_lang_helper(nfa, s, nfa["initial_state"])
    return InLang
    
def in_lang_helper(nfa, s, transtate):
    i = 0
    
    for state in nfa["final_states"]:
        if (s == "" and transtate == state):
            return 1;
            
    for index1,symbol in enumerate(nfa["transition_function"][transtate]):
        for index2,newState in enumerate(nfa["transition_function"][transtate][symbol]):
            if (symbol == s[0:1]):
                i += in_lang_helper(nfa, s[1:], newState)
            elif (symbol == "e"):
                i += in_lang_helper(nfa, s[0:], newState)
    return i;

def draw_nfa(nfa, title=""):
    state_name = {}
    i = 0
    for state in nfa["states"]:
        state_name[state] = "q{}".format(i)
        i += 1
    
    g = Digraph()
    g.attr(rankdir='LR')

    if title == "":
        title = r'\n\nNFA'
    else:
        title = r'\n\nNFA : '+title
    g.attr(label=title, fontsize='30')

    g.attr('node', shape='doublecircle')
    for state in nfa['final_states']:
        g.node(state_name[state])

    g.attr('node', shape='none')
    g.node("")

    g.attr('node', shape='circle')
    g.edge("", state_name[nfa["initial_state"]])

    for state in nfa["states"]:
        for symbol in nfa["transition_function"][state]:
            for transition_state in nfa["transition_function"][state][symbol]:
                g.edge(state_name[state], state_name[transition_state],
                       label=symbol if symbol != EPSILON else u'\u03F5')

    g.view(tempfile.mktemp('.gv'))

    header = ['State'] + list(nfa["alphabet"]) + ['ε']
    table_data = []

    for state in nfa["states"]:
        row = [state_name[state]]
        for symbol in nfa["alphabet"]:
            next_states = nfa["transition_function"][state].get(symbol, [])
            row.append(", ".join([state_name[next_state] for next_state in next_states]))
        epsilon_transitions = nfa["transition_function"][state].get(EPSILON, [])
        row.append(", ".join([state_name[epsilon_transition] for epsilon_transition in epsilon_transitions]))
        table_data.append(row)

    print("\nTransition Table:")
    print(tb(table_data, headers=header, tablefmt='grid'))

def validate_strings(nfa, strings):
    for string in strings:
        result = in_language(nfa, string)
        if result:
            print(f"String '{string}' is valid.")
        else:
            print(f"String '{string}' is not valid.")

regex_input = input("Enter a regular expression: ")
nfa = regex_to_nfa(regex_input)
draw_nfa(nfa, regex_input)

while True:
    test_string = input("Enter a test string (type 'exit' to stop testing): ")

    if test_string.lower() == 'exit':
        break

    validate_strings(nfa, [test_string])