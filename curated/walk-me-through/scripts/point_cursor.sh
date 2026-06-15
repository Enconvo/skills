#!/bin/bash
# point_cursor.sh — live-tutoring cursor pointer.
# Moves the real macOS mouse so the user SEES what is being explained,
# like a human tutor pointing at the screen. Requires cliclick (brew install cliclick).
#
# Subcommands:
#   circle  CX CY [RADIUS] [LOOPS] [STEPS] [WAIT_MS]   draw circle(s) around a point
#   point   X Y [BOUNCES]                              move to a point + small wiggle to draw the eye
#   underline X1 Y X2 [SWEEPS] [WAIT_MS]               sweep horizontally (underline a label/row)
#   move    X Y                                         just move there
#
# Coordinates are macOS logical points (top-left origin) — the same space as a
# non-Retina screenshot / Screen Doodle. On a 2x Retina display divide raw pixels by 2.

set -euo pipefail
CLICLICK="$(command -v cliclick || echo /opt/homebrew/bin/cliclick)"
SUB="${1:-circle}"; shift || true

if [ ! -x "$CLICLICK" ]; then
  echo "point_cursor.sh requires cliclick. Install it with: brew install cliclick" >&2
  exit 127
fi

case "$SUB" in
  circle)
    CX=${1:?center x}; CY=${2:?center y}; R=${3:-70}; LOOPS=${4:-3}; STEPS=${5:-40}; WAIT=${6:-10}
    ARGS=$(python3 -c "import math,sys; cx,cy,r,loops,steps,wait=map(float,sys.argv[1:7]); steps=int(steps); loops=int(loops); wait=int(wait); p=['m:%d,%d'%(round(cx+r),round(cy))]; [p.extend(['m:%d,%d'%(round(cx+r*math.cos(2*math.pi*i/steps)),round(cy+r*math.sin(2*math.pi*i/steps))),'w:%d'%wait]) for i in range(loops*steps+1)]; print(' '.join(p))" "$CX" "$CY" "$R" "$LOOPS" "$STEPS" "$WAIT")
    "$CLICLICK" $ARGS ;;
  point)
    X=${1:?x}; Y=${2:?y}; B=${3:-3}
    ARGS=$(python3 -c "import sys; x,y,b=int(sys.argv[1]),int(sys.argv[2]),int(sys.argv[3]); p=['m:%d,%d'%(x,y),'w:120']; [p.extend(['m:%d,%d'%(x,y-9),'w:70','m:%d,%d'%(x,y),'w:70']) for _ in range(b)]; print(' '.join(p))" "$X" "$Y" "$B")
    "$CLICLICK" $ARGS ;;
  underline)
    X1=${1:?x1}; Y=${2:?y}; X2=${3:?x2}; S=${4:-3}; WAIT=${5:-8}
    ARGS=$(python3 -c "import sys; x1,y,x2,s,wait=map(int,sys.argv[1:6]); steps=30; p=['m:%d,%d'%(x1,y)]; [p.extend(['m:%d,%d'%(round((a+(b-a)*i/steps)),y),'w:%d'%wait]) for k in range(s) for (a,b) in [((x1,x2) if k%2==0 else (x2,x1))] for i in range(steps+1)]; print(' '.join(p))" "$X1" "$Y" "$X2" "$S" "$WAIT")
    "$CLICLICK" $ARGS ;;
  move)
    "$CLICLICK" m:${1:?x},${2:?y} ;;
  *) echo "unknown subcommand: $SUB" >&2; exit 1 ;;
esac
