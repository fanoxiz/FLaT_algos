from grammar import Grammar

class Earley:
  def fit(self, G: Grammar):
    self.g = G
    self.rules = {}
    for left, right in G.P:
      if left not in self.rules:
        self.rules[left] = []
      self.rules[left].append(right)

  def predict(self, word: str) -> bool:
    n = len(word)
    D = [[] for _ in range(n + 1)]
    D_sets = [set() for _ in range(n + 1)]

    def add_state(state, j):
      if state not in D_sets[j]:
        D_sets[j].add(state)
        D[j].append(state)

    if self.g.S in self.rules:
      for right_prod in self.rules[self.g.S]:
        add_state((self.g.S, tuple(right_prod), 0, 0), 0)

    for j in range(n + 1):
      i = 0
      while i < len(D[j]):
        left, right, cur_pos, start_pos = D[j][i]
        i += 1

        # Complete
        if cur_pos == len(right):
          for p_item in D[start_pos]:
            p_left, p_right, p_cur_pos, p_start_pos = p_item
            if p_cur_pos < len(p_right) and p_right[p_cur_pos] == left:
              new_item = (p_left, p_right, p_cur_pos + 1, p_start_pos)
              add_state(new_item, j)
          continue


        next_sym = right[cur_pos]

        # Scan
        if next_sym in self.g.Sigma:
          if j < n and word[j] == next_sym:
            new_item = (left, right, cur_pos + 1, start_pos)
            add_state(new_item, j + 1)

        # Predict
        elif next_sym in self.g.N:
          if next_sym in self.rules:
            for prod in self.rules[next_sym]:
              new_item = (next_sym, tuple(prod), 0, j)
              add_state(new_item, j)

    for item in D[n]:
      left, right, cur_pos, start_pos = item
      if left == self.g.S and cur_pos == len(right) and start_pos == 0:
        return True
        
    return False
  
###
