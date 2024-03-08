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

---