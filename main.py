from cyk import CockeYoungerKasami
from grammar import Grammar

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

def main():
  try:
    (N, Sigma, P, S), words = ReadInput()
    g = Grammar(N, Sigma, P, S)
    algo = CockeYoungerKasami()
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

###
