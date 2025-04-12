# Pat In
params:
- current state
- current drugs
- med hist
# Processing
## stage 1: preprocessing
convertions:
- cur drugs -> tech-drug
- cur state -> tech-state
- med hist  -> tech-state

## stage 2: canditates
coverage:
match tech-drug <-> tech-state write in map
map\[state\] = \[drugs*\]

## stage 3: select candidate
first score:
- availiability ($av$)
- confirmed ($c$)
- similarity ($c$)

# Output

# stack
- back/front: py + django
- db: postgress + pgvector
