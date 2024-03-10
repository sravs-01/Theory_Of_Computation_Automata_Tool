# NFA Construction Algorithm

The following algorithm outlines the process of creating a Non-deterministic Finite Automaton (NFA).

## Input:
   - Set of states _Q_
   - Alphabet _Σ_
   - Transition function _δ_
   - Start state _q₀_
   - Set of accepting states _F_

## NFA Construction Steps:

1. **Initialize NFA:**
   - Create a set of states _Q_.
   - Define the alphabet _Σ_.
   - Define the transition function _δ_ that maps each state and input symbol to a set of states (may be empty or contain multiple states).
   - Specify the start state _δ_.
   - Specify the set of accepting states _F_.

2. **Example Transition Function:**
   - _δ_(q, a) = _{ p, r }_ *(If there is a transition from state _Q_ to either _p_ or _r_ on input symbol _a_)*

3. **Epsilon Closure Function:**
   - Compute the epsilon closure _{ε-closure}(q)_:
     _{ε-closure}(q)_ = _q_ _∪_ {p ∈ Q ∣ (q,ϵ) (∗)-> p}
     *(Epsilon closure is the set of states reachable from _Q_ through epsilon transitions.)*

4. **Accepting States:**
   - Specify the set of accepting states _F_.

5. **Define Transitions:**
   - For each state _q_i_ in _Q_ and each symbol _a_ in _Σ_:
     - Define the transition function _δ(q_i, a)_ that maps to a set of states representing possible transitions on input symbol _a_.

6. **Epsilon Transitions:**
   - Extend the transition function to handle epsilon transitions. For each state _q_i_ in _Q_:
     - If there are epsilon transitions from _q_i_, update the transition function accordingly.

7. **Non-deterministic Aspects:**
   - Highlight that the NFA allows non-deterministic transitions, meaning there can be multiple possible next states for a given state and input symbol.

8. **Multiple Accepting States:**
   - Note that an NFA can have multiple accepting states, and a string is accepted if there exists at least one accepting state in the final 

9. **Output:**
    - The NFA is represented by the set of states _Q_, alphabet _Σ_, transition function _δ_, start state _q₀_, and set of accepting states _F_.

# Overview

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
---