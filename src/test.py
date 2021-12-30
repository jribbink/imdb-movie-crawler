max_val = 0
max_x = None
for x in range(0,1000000):
  y = (2200000-38.5*x)/35
  P = 1.1 * x + y - x*y/(10**8)
  if(P > max_val and y > 0):
    max_val = P
    max_x = x

print(max_val + " x: " + max_x)