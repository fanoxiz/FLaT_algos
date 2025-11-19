from itertools import product

class Grammar:
  def __init__(self, N, Sigma, rules, S, to_be_parsed=True):
    self.N = set(N)
    self.Sigma = set(Sigma)
    self.S = S
    self.P = []
    
    if to_be_parsed:
      self.Parse(rules)
    else:
      self.P = rules

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
      lines.append(f"{left} -> {' '.join(right)}")
      
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
    
    for p in product(*possibilities):
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

  return Grammar(new_N, new_Sigma, new_P_3, new_S, to_be_parsed=False)

###
