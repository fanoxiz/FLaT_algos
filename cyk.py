from grammar import Grammar, ToCNF

class CockeYoungerKasami:

  def __init__(self):
    self.g_cnf = None
    self.s_nullable = False
    self.binary_rules = {}
    self.term_rules = {}

  def fit(self, G: Grammar):
    nullable = set()
    while True:
      changed = False
      for head, body in G.P:
        if len(body) == 0 or all(sym in nullable for sym in body):
          if head not in nullable:
            nullable.add(head)
            changed = True
      if not changed:
        break
    self.s_nullable = (G.S in nullable)

    self.g_cnf = ToCNF(G)

    self.binary_rules = {}
    self.term_rules = {}
    
    for head, body in self.g_cnf.P:
      if len(body) == 1:
        term = body[0]
        if term not in self.term_rules:
          self.term_rules[term] = []
        self.term_rules[term].append(head)
      elif len(body) == 2:
        pair = (body[0], body[1])
        if pair not in self.binary_rules:
          self.binary_rules[pair] = []
        self.binary_rules[pair].append(head)
      else:
        raise Exception("Не НФХ")

  def predict(self, word: str) -> bool:
    if word == "":
      return self.s_nullable

    n = len(word)

    dp = [[set() for _ in range(n)] for _ in range(n)]

    for i in range(n):
      char = word[i]
      if char in self.term_rules:
        dp[i][i].update(self.term_rules[char])

    for length in range(2, n + 1):
      for i in range(n - length + 1):
        j = i + length - 1
        
        for k in range(i, j):
          left_cell = dp[i][k]
          right_cell = dp[k + 1][j]
          
          if not left_cell or not right_cell:
            continue
          
          for B in left_cell:
            for C in right_cell:
              if (B, C) in self.binary_rules:
                dp[i][j].update(self.binary_rules[(B, C)])

    return self.g_cnf.S in dp[0][n - 1]

###
