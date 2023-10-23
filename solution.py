import math


def gcde(a, b):
  if a == 0:
    return b, 0, 1

  gcd, x1, y1 = gcde(b % a, a)

  x = y1 - (b // a) * x1
  y = x1

  return gcd, x, y


def gcd(a, b):
  return gcde(a, b)[0]


def a(p):
  g = abs(gcd(p[0], p[1]))
  return (p[0] // g, p[1] // g)


def d2(p):
  return p[0] * p[0] + p[1] * p[1]


def v(p, p0):
  return (p[0] - p0[0], p[1] - p0[1])


def faster_solution(dim, p, t, d):
  md2 = d * d
  w, h = dim
  KX, KY = (p[0] + d + w - 1) // w + 1, (p[1] + d + h - 1) // h + 1

  def quadrant(d, K, p, t, dir, count_edges):
    d0, d1 = d
    K0, K1 = K
    dir0, dir1 = dir
    hits = 0
    # X Positive
    occupieds = {a(v(t, p))}
    f0 = True
    for k0 in range(0, dir0 * (K0 + 1), dir0):
      f0 = not f0

      MAX1 = min(
          #int(math.ceil(math.sqrt(max(md2 - d0 * d0 * k0 * k0, 0))) / d1),
          float('inf'),  #dir * k0,
          # K1,
          max(K0, K1)) + 1

      f1 = True
      for k1 in range(0, dir1 * (K1 + 1), dir1):
        f1 = not f1
        if k0 == 0 and k1 == 0:
          continue

        vp = v((k0 * d0 + ((d0 - p[0]) if f0 else p[0]), k1 * d1 +
                ((d1 - p[1]) if f1 else p[1])), p)
        ap = a(vp)
        d2vp = d2(vp)
        vt = v((k0 * d0 + ((d0 - t[0]) if f0 else t[0]), k1 * d1 +
                ((d1 - t[1]) if f1 else t[1])), p)
        at = a(vt)
        d2vt = d2(vt)

        if (not (k0 == 0 or k1 == 0)
            or count_edges) and d2vt > 0 and d2vt <= md2 and not (
                ap == at and d2vp < d2vt) and at not in occupieds:
          hits += 1

        occupieds.update((ap, at))

    return hits

  q0 = quadrant(dim, (KX, KY), p, t, (1, 1), True)
  q1 = quadrant(dim, (KX, KY), p, t, (-1, 1), False)

  q2 = quadrant(dim, (KX, KY), p, t, (-1, -1), True)
  q3 = quadrant(dim, (KX, KY), p, t, (1, -1), False)

  return (d2(v(t, p)) <= md2) + q0 + q1 + q2 + q3


def solution(dim, p, t, d):
  """Alternative solution which uses Bezout's identity to
     find a lattice point in the direction of the target-of-interest.
     This lattice point is corrected to the lattice point nearest to (0,0),
     still in the same direction. If it's closer than the ToI, it blocks the
     line of sight to the ToI.
     This version is slower than faster_solution, but uses O(1) memory"""
  md2 = d * d
  w, h = dim
  us = (p, t, (w + w - p[0], p[1]), (w + w - t[0], t[1]),
        (w + w - p[0], h + h - p[1]), (w + w - t[0], h + h - t[1]),
        (p[0], h + h - p[1]), (t[0], h + h - t[1]))
  KX, KY = (p[0] + d + w - 1) // w, (p[1] + d + h - 1) // h
  hits = +(d2(v(t, p)) <= md2) # No-bounce solution

  for kx in range(-KX, KX + 1):
    #lky = int(math.sqrt(max(md2 - kx*kx, 0))) + 1 # Slower than just checking. Will be faster for some d/dim[0]
    lky = KY
    for ky in range(-lky, lky + 1):
      if kx == 0 and ky == 0:
        continue

      fx = kx & 1 == 1
      fy = ky & 1 == 1

      vx, vy = (-p[0] + kx * w + ((w - t[0]) if fx else t[0]),
                -p[1] + ky * h + ((h - t[1]) if fy else t[1]))

      d2v = d2((vx, vy))
      if d2v > md2:
        continue

      # Handle all other possible points (shooter, target)*4 - 1
      a = 2 * vy * w
      b = -2 * vx * h
      cb = p[0] * vy - p[1] * vx

      for u in us:
        vux, vuy = v(u, p)

        if (vux, vuy) == (vx, vy):
          continue

        c = cb + u[1] * vx - u[0] * vy

        if c == 0:
          # Handle the degenerate case first
          kkx, kky = (0, 0)
          if u == p or vux * vx < 0:
            kkx = h * vx // gcd(w * vy, h * vx)
            kkx = int(math.copysign(kkx, kx))
            kky = (kkx * w * vy // h // vx) if vx else vy // (2 * h)
        else:
          # The general case: Calculate the Bachet-Bezout coefficients
          # to find the ~nearest lattice point on the same line, for the reduced problem
          g, x, y = gcde(a, b)

          q, r = divmod(c, g)
          if r != 0:
            continue

          # Get lattice point in the correct direction
          kkx = x * q
          kky = y * q

          # Find the nearest in the actual lattice now that we have a starting point
          kkx2w = kkx*2*w
          sign = int(math.copysign(1, kx))
          flip = vx * (kkx2w + vux) < 0  # kx kkx differ in sign

          dx0 = abs(b // g)
          w2dx0 = w * 2 * dx0
          r = (abs(vux + kkx2w) + (w2dx0 - 1) * flip) // w2dx0
          dx = (sign if flip else -sign) * r * dx0
          kkx += dx
          kky -= dx * a // b

        if d2((-p[0] + u[0] + 2 * w * kkx, -p[1] + u[1] + 2 * h * kky)) < d2v:
          break

      else:
        hits += 1
  return hits


def search():
    import random as r
    gen = 0
    while True:
        gen += 1
        if gen % 10 == 0:
            print(gen)
        while True:
            d = (r.randrange(2, 1250), r.randrange(2, 1250))
            if d != (2, 2):
                break

        p = (r.randrange(1, d[0]), r.randrange(1, d[1]))
        while True:
            t = (r.randrange(1, d[0]), r.randrange(1, d[1]))
            if t != p:
                break

        radius = r.randrange(1, 10000)


        fs = faster_solution(d, p, t, radius)
        s = solution(d, p, t, radius)

        if fs != s:
            print('({}, {}, {}, {}): {} != {}'.format(d, p, t, radius, fs, s))


if __name__ == '__main__':
    search()

