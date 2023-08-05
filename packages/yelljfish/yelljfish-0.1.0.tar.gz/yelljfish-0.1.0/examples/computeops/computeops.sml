fun hsum n = ((n - 1) * n) div 2
fun computeops start 0 = start
  | computeops start runs = computeops (start + hsum start) (runs - 1)
fun computeops start runs = foldr
