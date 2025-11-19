import itertools

def ReadInput():
  _, _, P_len = map(int, input().split())
  N = list(non_term.strip() for non_term in input().split())
  Sigma = list(input().strip())
  P = []
  for _ in range(P_len):
    P.append(input())
  S = input()

  words = []
  m = int(input())
  for _ in range(m):
    words.append(input().strip())

  return ((N, Sigma, P, S), words)

class Grammar:
  def __init__(self, non_terminals, terminals, raw_rules, start_symbol):
    self.N = set(non_terminals)
    self.Sigma = set(terminals)
    self.S = start_symbol
    self.P = [] 
    self.Parse(raw_rules)

  def Parse(self, raw_rules):
    if self.S not in self.N:
      raise ValueError("Стартовый символ не найден в списке нетерминалов")

    for rule in raw_rules:
      if "->" not in rule:
        raise ValueError("Некорректный формат правила")

      left, right = rule.split("->")
      left = left.strip()
      right = right.strip()

      if left not in self.N:
        raise ValueError(f"Левая часть правила {left} не является нетерминалом")
      
      clean_right = []

      for char in right:
        if char.isspace(): 
          continue
        
        if char not in self.N and char not in self.Sigma:
          raise ValueError(f"В правиле {rule} неизвестный символ")
        
        clean_right.append(char)

      self.P.append((left, clean_right))

  def __repr__(self):
    lines = [f"Start Symbol: {self.S}"]
    sorted_rules = sorted(self.P, key=lambda x: (x[0] != self.S, x[0], str(x[1])))
    for left, right in sorted_rules:
      lines.append(f"{left} -> {" ".join(right)}")
      
    return "\n".join(lines)

def ToCNF(g: Grammar) -> Grammar:
  new_P_0 = g.P.copy()
  new_N = g.N.copy()
  new_Sigma = g.Sigma.copy()
  new_S = g.S

  id_counter = 0
  def GetNewNonterm():
    nonlocal id_counter
    id_counter += 1
    sym = f"T_{id_counter}" 
    new_N.add(sym)
    return sym

  # 1: Удаление eps правил
  nullable = set()
  while True:
    changed = False
    for left, right in new_P_0:
      if len(right) == 0 or all(sym in nullable for sym in right):
        if left not in nullable:
          nullable.add(left)
          changed = True
    if not changed:
      break

  new_P_1 = []
  seen_rules = set()

  for left, right in new_P_0:
    if len(right) == 0:
      continue

    possibilities = []
    for sym in right:
      if sym in nullable:
        possibilities.append([sym, None])
      else:
        possibilities.append([sym])
    
    for p in itertools.product(*possibilities):
      new_right = [sym for sym in p if sym is not None]
      if not new_right:
        continue
      
      rule_tuple = (left, tuple(new_right))
      if rule_tuple not in seen_rules:
        seen_rules.add(rule_tuple)
        new_P_1.append((left, list(new_right)))

  new_P_0 = new_P_1

  # 2: Удаление цепных правил
  unit_pairs = {n: {n} for n in new_N}
  
  for left, right in new_P_0:
    if len(right) == 1 and right[0] in new_N:
      unit_pairs[left].add(right[0])

  changed = True
  while changed:
    changed = False
    for a in new_N:
      for b in list(unit_pairs[a]):
        if b in unit_pairs:
          for c in unit_pairs[b]:
            if c not in unit_pairs[a]:
              unit_pairs[a].add(c)
              changed = True

  new_P_2 = []

  non_unit_rules = []
  for left, right in new_P_0:    
    if not (len(right) == 1 and right[0] in new_N):
       non_unit_rules.append((left, right))

  seen_rules_2 = set()
  for a in new_N:
    if a not in unit_pairs:
      continue
    for b in unit_pairs[a]:
      for b_head, b_body in non_unit_rules:
        if b_head == b:
          r_tuple = (a, tuple(b_body))
          if r_tuple not in seen_rules_2:
            seen_rules_2.add(r_tuple)
            new_P_2.append((a, list(b_body)))

  new_P_0 = new_P_2

  # 3: Замена T_a -> a и разбиение
  new_P_3 = []
  term_cache = {}

  for left, right in new_P_0:
    if len(right) == 1 and right[0] in new_Sigma:
      new_P_3.append((left, right))
      continue

    curr_right = []
    for sym in right:
      if sym in new_Sigma:
        if sym not in term_cache:
          new_nt = GetNewNonterm()
          term_cache[sym] = new_nt
          new_P_3.append((new_nt, [sym]))
        curr_right.append(term_cache[sym])
      else:
        curr_right.append(sym)

    while len(curr_right) > 2:
      first = curr_right[0]
      rest = curr_right[1:]
      
      new_nt = GetNewNonterm()
      new_P_3.append((left, [first, new_nt]))
      
      left = new_nt
      curr_right = rest

    new_P_3.append((left, curr_right))

  # чтобы Parse не сломал нетерминалы типа T_a
  g_final = Grammar(new_N, new_Sigma, [], new_S)
  g_final.P = new_P_3
  return g_final

class CYK:
  def __init__(self):
    self.g_cnf = None
    self.s_nullable = False
    self.binary_rules = {}
    self.term_rules = {}

  def fit(self, g: Grammar):
    nullable = set()
    while True:
      changed = False
      for head, body in g.P:
        if len(body) == 0 or all(sym in nullable for sym in body):
          if head not in nullable:
            nullable.add(head)
            changed = True
      if not changed:
        break
    self.s_nullable = (g.S in nullable)

    self.g_cnf = ToCNF(g)

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

def main():
  try:
    (N, Sigma, P, S), words = ReadInput()
    g = Grammar(N, Sigma, P, S)
    algo = CYK()
    algo.fit(g)
    for w in words:
      if algo.predict(w):
        print("Yes")
      else:
        print("No")
  except Exception as e:
    raise e

if __name__ == "__main__":
  main()
