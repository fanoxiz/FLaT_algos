import pytest
import io
import cyk

TEST_DATA = [
    
# ПСП

("""1 2 2
S
()
S -> (S)S
S -> 
S
5
(())
)(
(()())
())())
((((())
""", 

["Yes", "No", "Yes", "No", "No"]),

# Арифметика

("""2 4 4
S A
i+()
S -> S+A
S -> A
A -> (S)
A -> i
S
5
()
i+i
(i+i)+i
i+
i+i)
""", 

["No", "Yes", "Yes", "No", "No"])
]

@pytest.mark.parametrize("input_str, expected", TEST_DATA)
def test_cyk_algo(monkeypatch, input_str, expected):
  monkeypatch.setattr('sys.stdin', io.StringIO(input_str))
  (N, Sigma, P, S), words = cyk.ReadInput()
  g = cyk.Grammar(N, Sigma, P, S)
  algo = cyk.CYK()
  algo.fit(g)
  results = []
  for w in words:
    res = ("Yes" if algo.predict(w) else "No")
    results.append(res)

  assert results == expected
