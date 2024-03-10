# Visuals borrowed from Mr. Shlok Pandey's github account: b30wulffz
from cgitb import small
from graphviz import Digraph
import tempfile

EPSILON = "e"
OPERATORS = ["+", "*", ")", "(", "?"]
RANK_OPERATORS = ['+', '?', '*']
NFA_STACK = []
COUNTER = 0

########################
"""
NFA is defined as a dictionary
{
   "states": [
       <state_ids>,
       ...
   ],
   "initial_state": <initial_state_id>,
   "final_states": [
       <state_ids>,
       ...
   ],
   "alphabet": [
      "$",
       <symbols>,
      ...
   ],
   "transition_function": {
       <state_id>: {
           <symbol>: [
               <state_ids>,
           ],
           ... # transition for all alphabet symbols shoud be present here
       },
       ...
   }
}
"""

"""
DFA is also defined similarly
{
   "states": [
       "phi",
       <state_ids>,
       ...
    ],
    "initial_state": <state_id>,
    "final_states":[
       <state_ids>,
       ...
    ],
    "alphabet": [
       <symbols>,
       ...
    ],
    "transition_function": {
        <state_id>: {
            <symbol>: <state_id>,
            ... # transition for all alphabet symbols shoud be present here. In case of no transition, symbol must point to phi
        },
        ...
    },
    "reachable_states": [
        <state_ids>,
        ...
    ],
    "final_reachable_states": [
        <state_ids>,
        ...
    ],
}
"""
###############################

def process(infix):
    newInfix = ""

    #iterate through infix, if two adjacent characters are in OPERATORS, add a '.' between them

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

###############################
# REGEX TO NFA
# Input: string reg_exp
# Output: NFA nfa such that L(nfa) = L(reg_exp)

def regex_to_nfa(reg_exp):

    global NFA_STACK
    global COUNTER

    reg_exp = "".join(process(reg_exp))


    for symbol in reg_exp:
        nfa = {
        "states": [],  # contains state IDs
        "initial_state": -1,  # contains initial state IDs
        "final_states": [],  # contains final state IDs
        "alphabet": [],  # contains all symbols
        "transition_function": {}  # contains transition functions for alphabet
        }

        #Kleene Star
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

        #Concatenation
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
        
        #Union
        elif symbol == "+":
            # Case 4 - union of two expressions
    
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

            #iterate through nfa2 final states and add transition to nfa 
            for state in left["final_states"]:
                nfa["transition_function"][state] = {
                    EPSILON: [COUNTER + 1]
                }
            #iterate through nfa3 final states and add transition to nfa
            for state in right["final_states"]:
                nfa["transition_function"][state] = {
                    EPSILON: [COUNTER + 1]
                }

        #Single Character 
        else:
            
            nfa["states"] = [COUNTER, COUNTER + 1]
            nfa["initial_state"] = COUNTER
            nfa["final_states"] = [COUNTER + 1]

            # Case 1 - single letter
            if symbol != "":
                
                nfa["alphabet"] = [symbol]
                nfa["transition_function"] = {
                    COUNTER: {
                        symbol: [COUNTER + 1]
                    },
                    COUNTER + 1: {}
                }

            # Case 2 - empty string
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

###############################
# Input: NFA nfa, string s
# Output: 1 if s is accepted by nfa, 0 otherwise.

def in_language(nfa, s):
    InLang = 0
    InLang += in_lang_helper(nfa, s, nfa["initial_state"])
    return InLang
    
def in_lang_helper(nfa, s, transtate):
    i = 0
    #print(s)
    #print("current state: " + str(transtate))
    for state in nfa["final_states"]:
        #print("final state: " + str(state))
        if (s == "" and transtate == state):
            return 1;
            
    for index1,symbol in enumerate(nfa["transition_function"][transtate]):
        for index2,newState in enumerate(nfa["transition_function"][transtate][symbol]):
            if (symbol == s[0:1]):
                #print(newState)
                i += in_lang_helper(nfa, s[1:], newState)
            elif (symbol == "e"):
                #print(newState)
                i += in_lang_helper(nfa, s[0:], newState)
    return i;

###############################

# DRAW NFA / DFA
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

    # mark goal states
    g.attr('node', shape='doublecircle')
    for state in nfa['final_states']:
        g.node(state_name[state])

    # add an initial edge
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

def draw_dfa(dfa, title=""):
    state_name = {}
    i = 0
    for state in dfa["reachable_states"]:
        if state == "phi":
            state_name[state] = u'\u03A6'
        else:
            state_name[state] = "q{}".format(i)
            i += 1

    g = Digraph()
    g.attr(rankdir='LR')

    if title == "":
        title = r'\n\nDFA'
    else:
        title = r'\n\nDFA : '+title
    g.attr(label=title, fontsize='30')

    # mark goal states
    g.attr('node', shape='doublecircle')
    for state in dfa["final_reachable_states"]:
        g.node(state_name[state])

    # add an initial edge
    g.attr('node', shape='none')
    g.node("")

    g.attr('node', shape='circle')
    g.edge("", state_name[dfa["initial_state"]])

    for state in dfa["reachable_states"]:
        for symbol in dfa["transition_function"][state].keys():
            transition_state = dfa["transition_function"][state][symbol]
            g.edge(state_name[state],
                   state_name[transition_state], label=symbol)

    g.view(tempfile.mktemp('.gv'))

################################
    
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