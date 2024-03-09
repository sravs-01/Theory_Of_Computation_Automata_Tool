import collections
import json
from graphviz import Digraph

non_symbols = ['+', '*', '.', '(', ')']
nfa = {}

class charType:
    SYMBOL = 1
    CONCAT = 2
    UNION  = 3
    KLEENE = 4

class NFAState:
    def __init__(self):
        self.next_state = {}

class ExpressionTree:
    def __init__(self, charType, value=None):
        self.charType = charType
        self.value = value
        self.left = None
        self.right = None

def make_exp_tree(regexp):
    stack = []
    for c in regexp:
        if c == "+":
            z = ExpressionTree(charType.UNION)
            z.right = stack.pop()
            z.left = stack.pop()
            stack.append(z)
        elif c == ".":
            z = ExpressionTree(charType.CONCAT)
            z.right = stack.pop()
            z.left = stack.pop()
            stack.append(z)
        elif c == "*":
            z = ExpressionTree(charType.KLEENE)
            z.left = stack.pop()
            stack.append(z)
        elif c == "(" or c == ")":
            continue
        else:
            stack.append(ExpressionTree(charType.SYMBOL, c))
    return stack[0]

def compPrecedence(a, b):
    p = ["+", ".", "*"]
    return p.index(a) > p.index(b)

def compute_regex(exp_t):
    if exp_t.charType == charType.CONCAT:
        return do_concat(exp_t)
    elif exp_t.charType == charType.UNION:
        return do_union(exp_t)
    elif exp_t.charType == charType.KLEENE:
        return do_kleene_star(exp_t)
    else:
        return eval_symbol(exp_t)

def eval_symbol(exp_t):
    start = NFAState()
    end = NFAState()
    start.next_state[exp_t.value] = [end]
    return start, end

def do_concat(exp_t):
    left_nfa = compute_regex(exp_t.left)
    right_nfa = compute_regex(exp_t.right)

    # Merge the end state of the left NFA with the start state of the right NFA
    left_nfa[1].next_state.update(right_nfa[0].next_state)
    
    return left_nfa[0], right_nfa[1]

def solveBracket(regex, end_state, states):
    """
        This function used to solve the regex inside a bracket and save the new states to the current available states
    """

    # initialization for the new states to be created must start with the last created state + 1
    b_start = end_state + 1
    b_prev = end_state + 1
    b_char = end_state + 1
    b_end = end_state + 1
    # create new state to indicate we are working with bracket regex
    states.update( { b_end : { "isTerminatingState": False } })
    # start looping over the regex inside the bracket to transform it
    index = 0
    while(index < len(regex)):
        # in case of oring operation found 
        if regex[index] == '|' or regex[index] == '+':
            # solve it using oring function (function description below) 
            index, prev, start,end = oring(index+1, regex, states , b_end)
            # create new 2 states to connect the oring branches
            states.update( { end+1 : { "isTerminatingState": False, "ε" : b_prev , "ε " : prev } })
            states.update( { end+2 : { "isTerminatingState": False} })
            states[end].update({"ε" : end+2})
            states[b_end].update({"ε" : end+2})
            #update the indices used to loop in states
            b_char = end + 1
            b_end = end +2
            b_start = b_end
            b_prev = end + 1
        # in case of new bracket found
        elif regex[index] == '(':
            # get the regex inside that bracket
            open_brackets = 1
            closed_brackets = 0
            sub_regex = ""
            j = index+1
            while(j<len(regex)):
                if regex[j] == '(':
                    open_brackets +=1
                elif regex[j] == ')':
                    closed_brackets +=1
                if (open_brackets == closed_brackets):
                    break
                sub_regex += regex[j]
                j += 1
            # then solve it using this function recursively
            prev , start, end = solveBracket(sub_regex, b_end, states) 
            # connect the new bracket regex with the current one with epsilon state
            states[b_end].update({"ε" : prev})
            b_end = end
            b_start = b_end
            b_char = prev
            # update the current index to start after the solved bracket
            index = index + len(sub_regex) + 2
        # in case of special character found
        elif regex[index] == '\\':
            # read the charactr after the \ and make a normal transition from the current state to new one using that character
            index += 1
            states[b_end].update({regex[index] : (b_end+1)})
            b_end +=1
            states.update( { b_end : { "isTerminatingState": False } })
            b_char = b_start
            b_start = b_end
            # increment the regex looping index     
            index += 1
        # in case of partitioning found
        elif regex[index] == '*':
            # create two states using tompthons rules as described in the slides
            b_end += 1
            states[b_start].update({" ε " : b_char, "  ε  " : b_end })
            states[b_char].update({"ε            " : b_end})
            states.update( { b_end : { "isTerminatingState": False} })
            b_start = b_end
            # increment the regex looping index     
            index += 1
        # in case of anding
        else:
            # make new state and new transaction from the current state to the new one using that char in the regex
            b_end +=1
            states[b_start].update( { regex[index] : b_end })
            states.update( { b_end : { "isTerminatingState": False } })
            b_char = b_start
            b_start = b_end    
            # increment the regex looping index     
            index += 1          
    # return information about the states added by this function when it's called     
    return b_prev, b_start, b_end


def oring(index , regex, states , end_state):
    """
        This function used to solve the regex after or operation and save the new states to the current available states
    """

    # initialization for the new states to be created must start with the last created state + 1
    oring_start = end_state + 1
    oring_prev = end_state + 1
    oring_prev_char = end_state + 1
    oring_end = end_state + 1
    # create new state to indicate we are working with bracket regex
    states.update( { oring_end : { "isTerminatingState": False } })

    # loop over the regex
    while(index < len(regex)):
        # in case of oring so the regex after oring operation was solved so return its states
        if regex[index] == '|' or regex[index] == '+':
            return index, oring_prev, oring_start, oring_end
        # in case of special character found
        elif regex[index] == '\\':
            # take the next character after \ 
            index += 1
            oring_end +=1
            # make a transition from the current state to new one using that character
            states[oring_start].update({regex[index] : (oring_end)})
            states.update( { oring_end : { "isTerminatingState": False } })
            # update states indeces
            oring_prev_char = oring_start
            oring_start = oring_end
        # in case of bracket found
        elif regex[index] == '(':
            # get the regex inside that bracket
            open_brackets = 1
            closed_brackets = 0
            sub_regex = ""
            j = index+1
            while(j<len(regex)):
                if regex[j] == '(':
                    open_brackets +=1
                elif regex[j] == ')':
                    closed_brackets +=1
                if (open_brackets == closed_brackets):
                    break
                sub_regex += regex[j]
                j += 1
            # solve that regex using the bracket solver function
            prev , start, end = solveBracket(sub_regex, oring_end, states) 
            # connect the resulting states with the current state using one spsilon move
            states[oring_end].update({"ε" : prev})
            # update the states indeces
            oring_end = end
            oring_start = oring_end
            oring_prev_char = prev
            # continue looping over the regex after that bracket
            index = index + len(sub_regex) + 1
        # in case of repition found
        elif regex[index] == '*':
            # create two state and connect between them using tompthon rule as decribed in the slides
            oring_end += 1
            states[oring_start].update({"   ε   " : oring_prev_char, "     ε     " : oring_end })
            states[oring_prev_char].update({"ε        " : oring_end})
            states.update( { oring_end : { "isTerminatingState": False} })
            oring_start = oring_end
        # in case of anding 
        else:
            # make a transition from the current state to new state using that input
            oring_end +=1
            states[oring_start].update( { regex[index] : oring_end })
            states.update( { oring_end : { "isTerminatingState": False } })
            oring_prev_char = oring_start
            oring_start = oring_end   
        # update the regex counter to continue looping over it      
        index += 1        
    # return information about the states added by this function when it's called     
    return len(regex), oring_prev, oring_start, oring_end

def transform(regex):
    states = { 0 : { "isTerminatingState": False } }
    start_state = 0
    end_state   = 0
    prev_char = 0
    prev_start  = 0
    n = len(regex)
    i = 0
    while i < n:
        # in case of special character found
        if regex[i] == '\\' :
            # take the next character after \ 
            i += 1
            # make a transition from the current state to new one using that character
            end_state += 1
            states[start_state].update({regex[i] : end_state})
            states.update( { end_state : { "isTerminatingState": False } })
            prev_char = start_state
            start_state = end_state
            # update the regex counter to continue looping over it  
            i +=1
        # in case of open bracket solve the bracket in another function and update i and states in that function 
        elif regex[i] == '(':
            # get the regex inside that bracket
            open_brackets = 1
            closed_brackets = 0
            sub_regex = ""
            j = i+1
            while(j<n):
                if regex[j] == '(':
                    open_brackets +=1
                elif regex[j] == ')':
                    closed_brackets +=1
                if (open_brackets == closed_brackets):
                    break
                sub_regex += regex[j]
                j += 1
            # solve that regex using the bracket solver function
            prev , start, end = solveBracket(sub_regex, end_state, states) 
            # connect the resulting states with the current state using one spsilon move
            states[end_state].update({"ε" : prev})
            # update the states indeces
            end_state = end
            start_state = end_state
            prev_char = prev
            # continue looping over the regex after that bracket
            i = i + len(sub_regex) + 2
        # in case of oring 
        elif regex[i] == '|' or regex[i] == '+':
            # solve it using oring function (function description above) 
            i, prev, start,end = oring(i+1, regex, states , end_state)
            # create new 2 states to connect the oring branches
            states.update( { end+1 : { "isTerminatingState": False, "     ε     " : prev_start , "      ε       " : prev } })
            states.update( { end+2 : { "isTerminatingState": False} })
            states[end].update({"ε" : end+2})
            states[end_state].update({"ε" : end+2})
            #update the state indices 
            prev_char = end + 1
            end_state = end +2
            start_state = end_state
            prev_start = end + 1
        # in case of repetition
        elif regex[i] == '*':
            # create two state and connect between them using tompthon rule as decribed in the slides
            end_state += 1
            states[start_state].update({"ε   " : prev_char, "ε    " : end_state })
            states[prev_char].update({"ε     " : end_state})
            states.update( { end_state : { "isTerminatingState": False} })
            start_state = end_state
            # update the regex counter to continue looping over it  
            i += 1
        # in case of anding
        else:
            # make a transition from the current state to new state using that input
            end_state += 1
            states[start_state].update({regex[i] : end_state})
            states.update( { end_state : { "isTerminatingState": False } })
            prev_char = start_state
            start_state = end_state
            # update the regex counter to continue looping over it  
            i += 1

    states[end_state]["isTerminatingState"] = True
    states = collections.OrderedDict(sorted(states.items()))
    
    results = {}
    results.update({"startingState" : ("S" + str(prev_start))})
    for key , value in states.items():
        entry = {}
        for k,v in value.items():
            if k == "isTerminatingState":
                entry.update({k : v})
            else:
                entry.update(({k : ("S" + str(v))})) 
        results.update({("S"+ str(key)) : entry})
    with open('out/nfa.json', 'w') as fp:
        json.dump(results, fp, ensure_ascii=False)
    
    # Update the results to replace 'λ' with 'ε' and remove epsilon transitions
    updated_results = {}
    for key, value in results.items():
        updated_entry = {}
        for k, v in value.items():
            if k == 'ε':
                updated_entry.update({'epsilon': v})
            elif not k.startswith('ε'):
                updated_entry.update({k: v})
        updated_results.update({key: updated_entry})

    with open('out/nfa_updated.json', 'w') as fp:
        json.dump(updated_results, fp, ensure_ascii=False)

    return updated_results

def do_union(exp_t):
    start = NFAState()
    end = NFAState()

    first_nfa = compute_regex(exp_t.left)
    second_nfa = compute_regex(exp_t.right)

    start.next_state['λ'] = [first_nfa[0], second_nfa[0]]
    first_nfa[1].next_state['λ'] = [end]
    second_nfa[1].next_state['λ'] = [end]

    return start, end

def do_kleene_star(exp_t):
    start = NFAState()
    end = NFAState()

    starred_nfa = compute_regex(exp_t.left)

    start.next_state['λ'] = [starred_nfa[0], end]
    starred_nfa[1].next_state['λ'] = [starred_nfa[0], end]

    return start, end

def arrange_transitions(state, states_done, symbol_table):
    global nfa

    if state in states_done:
        return

    states_done.append(state)

    for symbol in list(state.next_state):
        if symbol not in nfa['letters']:
            nfa['letters'].append(symbol)
        for ns in state.next_state[symbol]:
            if ns not in symbol_table:
                symbol_table[ns] = sorted(symbol_table.values())[-1] + 1
                q_state = "Q" + str(symbol_table[ns])
                nfa['states'].append(q_state)
            nfa['transition_function'].append(["Q" + str(symbol_table[state]), symbol, "Q" + str(symbol_table[ns])])

        for ns in state.next_state[symbol]:
            arrange_transitions(ns, states_done, symbol_table)

def notation_to_num(str):
    return int(str[1:])

def final_st_dfs():
    global nfa
    for st in nfa["states"]:
        count = 0
        for val in nfa['transition_function']:
            if val[0] == st and val[2] != st:
                count += 1
        if count == 0 and st not in nfa["final_states"]:
            nfa["final_states"].append(st)

def arrange_nfa(fa):
    global nfa
    nfa['states'] = []
    nfa['letters'] = []
    nfa['transition_function'] = []
    nfa['start_states'] = []
    nfa['final_states'] = []
    q_1 = "Q" + str(1)
    nfa['states'].append(q_1)
    arrange_transitions(fa[0], [], {fa[0] : 1})
    
    st_num = [notation_to_num(i) for i in nfa['states']]

    nfa["start_states"].append("Q1")
    final_st_dfs()

def add_concat(regex):
    global non_symbols
    l = len(regex)
    res = []
    for i in range(l - 1):
        res.append(regex[i])
        if regex[i] not in non_symbols:
            if regex[i + 1] not in non_symbols or regex[i + 1] == '(':
                res += '.'
        if regex[i] == ')' and regex[i + 1] == '(':
            res += '.'
        if regex[i] == '*' and regex[i + 1] == '(':
            res += '.'
        if regex[i] == '*' and regex[i + 1] not in non_symbols:
            res += '.'
        if regex[i] == ')' and regex[i + 1] not in non_symbols:
            res += '.'

    res += regex[l - 1]
    return res

def compute_postfix(regexp):
    stk = []
    res = ""

    for c in regexp:
        if c not in non_symbols or c == "*":
            res += c
        elif c == ")":
            while len(stk) > 0 and stk[-1] != "(":
                res += stk.pop()
            stk.pop()
        elif c == "(":
            stk.append(c)
        elif len(stk) == 0 or stk[-1] == "(" or compPrecedence(c, stk[-1]):
            stk.append(c)
        else:
            while len(stk) > 0 and stk[-1] != "(" and not compPrecedence(c, stk[-1]):
                res += stk.pop()
            stk.append(c)

    while len(stk) > 0:
        res += stk.pop()

    return res

def polish_regex(regex):
    reg = add_concat(regex)
    regg = compute_postfix(reg)
    return regg

def load_regex():
    regex = input("Enter a regular expression: ")
    return regex

def epsilon_closure(state, closure):
    closure.add(tuple(state))

    if 'ε' in state.next_state:
        for next_state in state.next_state['ε']:
            if next_state not in closure:
                epsilon_closure(next_state, closure)

def convert_epsilon_nfa_to_nfa(epsilon_nfa):
    nfa_states = {}
    symbol_table = {}
    start_state = epsilon_nfa[list(epsilon_nfa.keys())[0]]
    symbol_table[tuple(start_state)] = 1
    nfa_states[start_state] = epsilon_closure(start_state, set())

    states_queue = collections.deque(list(nfa_states[start_state]))

    while states_queue:
        current_state = states_queue.popleft()

        for symbol in epsilon_nfa['letters']:
            target_states = set()

            for epsilon_state in nfa_states[current_state]:
                if symbol in epsilon_state.next_state:
                    target_states.update(epsilon_state.next_state[symbol])

            for target_state in target_states:
                epsilon_closure(target_state, target_states)

            if target_states:
                target_states_key = tuple(sorted(list(target_states)))

                if target_states_key not in nfa_states:
                    symbol_table[target_states_key] = sorted(symbol_table.values())[-1] + 1
                    nfa_states[target_states_key] = target_states
                    states_queue.append(target_states_key)

    nfa = {
        'states': [],
        'letters': list(epsilon_nfa['letters']),
        'transition_function': [],
        'start_states': ["Q1"],
        'final_states': []
    }

    for key, value in nfa_states.items():
        nfa['states'].append("Q" + str(symbol_table[key]))

        if epsilon_nfa[1] in value:
            nfa['final_states'].append("Q" + str(symbol_table[key]))

        for symbol in epsilon_nfa['letters']:
            target_states_key = tuple(sorted(list(value)))

            if symbol != 'ε':
                target_state = tuple(sorted(list(value)))
                nfa['transition_function'].append(["Q" + str(symbol_table[key]), symbol, "Q" + str(symbol_table[target_state])])

    return nfa

def visualize_nfa():
    dot = Digraph()
    dot.graph_attr['rankdir'] = 'LR'
    dot.node_attr['shape'] = 'circle'

    for i in range(len(nfa['states'])):
        dot.node(nfa['states'][i], label=nfa['states'][i], shape='doublecircle' if nfa['states'][i] in nfa['final_states'] else 'circle')

    for transition in nfa['transition_function']:
        dot.edge(transition[0], transition[2], label=transition[1] if transition[1] != 'λ' else 'λ', fontsize='10')

    dot.render(filename='nfa_visualization', format='pdf', view=True)

def output_nfa():
    global nfa
    with open('nfa_output.json', 'w') as outjson:
        outjson.write(json.dumps(nfa, indent=4))


def solveBracket(regex, end_state, states):
    """
        This function used to solve the regex inside a bracket and save the new states to the current available states
    """

    # initialization for the new states to be created must start with the last created state + 1
    b_start = end_state + 1
    b_prev = end_state + 1
    b_char = end_state + 1
    b_end = end_state + 1
    # create new state to indicate we are working with bracket regex
    states.update( { b_end : { "isTerminatingState": False } })
    # start looping over the regex inside the bracket to transform it
    index = 0
    while(index < len(regex)):
        # in case of oring operation found 
        if regex[index] == '|' or regex[index] == '+':
            # solve it using oring function (function description below) 
            index, prev, start,end = oring(index+1, regex, states , b_end)
            # create new 2 states to connect the oring branches
            states.update( { end+1 : { "isTerminatingState": False, "ε" : b_prev , "ε " : prev } })
            states.update( { end+2 : { "isTerminatingState": False} })
            states[end].update({"ε" : end+2})
            states[b_end].update({"ε" : end+2})
            #update the indices used to loop in states
            b_char = end + 1
            b_end = end +2
            b_start = b_end
            b_prev = end + 1
        # in case of new bracket found
        elif regex[index] == '(':
            # get the regex inside that bracket
            open_brackets = 1
            closed_brackets = 0
            sub_regex = ""
            j = index+1
            while(j<len(regex)):
                if regex[j] == '(':
                    open_brackets +=1
                elif regex[j] == ')':
                    closed_brackets +=1
                if (open_brackets == closed_brackets):
                    break
                sub_regex += regex[j]
                j += 1
            # then solve it using this function recursively
            prev , start, end = solveBracket(sub_regex, b_end, states) 
            # connect the new bracket regex with the current one with epsilon state
            states[b_end].update({"ε" : prev})
            b_end = end
            b_start = b_end
            b_char = prev
            # update the current index to start after the solved bracket
            index = index + len(sub_regex) + 2
        # in case of special character found
        elif regex[index] == '\\':
            # read the charactr after the \ and make a normal transition from the current state to new one using that character
            index += 1
            states[b_end].update({regex[index] : (b_end+1)})
            b_end +=1
            states.update( { b_end : { "isTerminatingState": False } })
            b_char = b_start
            b_start = b_end
            # increment the regex looping index     
            index += 1
        # in case of partitioning found
        elif regex[index] == '*':
            # create two states using tompthons rules as described in the slides
            b_end += 1
            states[b_start].update({" ε " : b_char, "  ε  " : b_end })
            states[b_char].update({"ε            " : b_end})
            states.update( { b_end : { "isTerminatingState": False} })
            b_start = b_end
            # increment the regex looping index     
            index += 1
        # in case of anding
        else:
            # make new state and new transaction from the current state to the new one using that char in the regex
            b_end +=1
            states[b_start].update( { regex[index] : b_end })
            states.update( { b_end : { "isTerminatingState": False } })
            b_char = b_start
            b_start = b_end    
            # increment the regex looping index     
            index += 1          
    # return information about the states added by this function when it's called     
    return b_prev, b_start, b_end


def oring(index , regex, states , end_state):
    """
        This function used to solve the regex after or operation and save the new states to the current available states
    """

    # initialization for the new states to be created must start with the last created state + 1
    oring_start = end_state + 1
    oring_prev = end_state + 1
    oring_prev_char = end_state + 1
    oring_end = end_state + 1
    # create new state to indicate we are working with bracket regex
    states.update( { oring_end : { "isTerminatingState": False } })

    # loop over the regex
    while(index < len(regex)):
        # in case of oring so the regex after oring operation was solved so return its states
        if regex[index] == '|' or regex[index] == '+':
            return index, oring_prev, oring_start, oring_end
        # in case of special character found
        elif regex[index] == '\\':
            # take the next character after \ 
            index += 1
            oring_end +=1
            # make a transition from the current state to new one using that character
            states[oring_start].update({regex[index] : (oring_end)})
            states.update( { oring_end : { "isTerminatingState": False } })
            # update states indeces
            oring_prev_char = oring_start
            oring_start = oring_end
        # in case of bracket found
        elif regex[index] == '(':
            # get the regex inside that bracket
            open_brackets = 1
            closed_brackets = 0
            sub_regex = ""
            j = index+1
            while(j<len(regex)):
                if regex[j] == '(':
                    open_brackets +=1
                elif regex[j] == ')':
                    closed_brackets +=1
                if (open_brackets == closed_brackets):
                    break
                sub_regex += regex[j]
                j += 1
            # solve that regex using the bracket solver function
            prev , start, end = solveBracket(sub_regex, oring_end, states) 
            # connect the resulting states with the current state using one spsilon move
            states[oring_end].update({"ε" : prev})
            # update the states indeces
            oring_end = end
            oring_start = oring_end
            oring_prev_char = prev
            # continue looping over the regex after that bracket
            index = index + len(sub_regex) + 1
        # in case of repition found
        elif regex[index] == '*':
            # create two state and connect between them using tompthon rule as decribed in the slides
            oring_end += 1
            states[oring_start].update({"   ε   " : oring_prev_char, "     ε     " : oring_end })
            states[oring_prev_char].update({"ε        " : oring_end})
            states.update( { oring_end : { "isTerminatingState": False} })
            oring_start = oring_end
        # in case of anding 
        else:
            # make a transition from the current state to new state using that input
            oring_end +=1
            states[oring_start].update( { regex[index] : oring_end })
            states.update( { oring_end : { "isTerminatingState": False } })
            oring_prev_char = oring_start
            oring_start = oring_end   
        # update the regex counter to continue looping over it      
        index += 1        
    # return information about the states added by this function when it's called     
    return len(regex), oring_prev, oring_start, oring_end

if __name__ == "__main__":
    reg = load_regex()
    pr = polish_regex(reg)
    et = make_exp_tree(pr)
    fa = compute_regex(et)
    arrange_nfa(fa)
    
    nfa_result = convert_epsilon_nfa_to_nfa(nfa)
    
    visualize_nfa(nfa_result)
    output_nfa(nfa_result)