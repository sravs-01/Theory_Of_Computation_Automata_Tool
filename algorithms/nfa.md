# NFA Construction Algorithm

The following algorithm outlines the process of creating a Non-deterministic Finite Automaton (NFA).

## Input:
   - Set of states \( Q \)
   - Alphabet \( \Sigma \)
   - Transition function \( \delta \)
   - Start state \( q_0 \)
   - Set of accepting states \( F \)

## NFA Construction Steps:

1. **Initialize NFA:**
   - Create a set of states \( Q \).
   - Define the alphabet \( \Sigma \).
   - Define the transition function \( \delta \) that maps each state and input symbol to a set of states (may be empty or contain multiple states).
   - Specify the start state \( q_0 \).
   - Specify the set of accepting states \( F \).

2. **Example Transition Function:**
   - \( \delta(q, a) = \{ p, r \} \)  *(If there is a transition from state \( q \) to either \( p \) or \( r \) on input symbol \( a \))*

3. **Epsilon Closure Function:**
   - Compute the epsilon closure \( \text{ε-closure}(q) \):
     \[ \text{ε-closure}(q) = \{ q \} \cup \{ p \in Q \,|\, (q, \epsilon) \xrightarrow{*} p \} \]
     *(Epsilon closure is the set of states reachable from \( q \) through epsilon transitions.)*

4. **Accepting States:**
   - Specify the set of accepting states \( F \).

---