# c.py


import enum
import immutables
import random
import operator


Round = enum.Enum('Round', 'deal bet complete')
Action = enum.Enum('Action', 'bet call fold')

## game

def deal():
    return immutables.Map(
            round = Round.deal, 
            hands = {'player1': random.randint(1, 3), 'player2': random.randint(1, 3)}, 
            payout = immutables.Map(player1 = 0.0, player2 = -2.0), 
            pot = 2.0, 
            to_act = 'player1', 
            actions = [])

def act_bet(h):
    with h.mutate() as m:
        y = h.get('payout')
        m.set('payout', y.set('player1', y.get('player1') - 1.0))
        m.set('pot', h.get('pot') + 1.0)
        m.set('actions', h.get('actions') + [Action.bet])
        m.set('to_act', 'player2')
        m.set('round', Round.bet)
        h1 = m.finish()
    return h1

def act_call(h):
    with h.mutate() as m:
        y = h.get('payout')
        p0 = y.set('player2', y.get('player2') - 1.0)
        pot = h.get('pot') + 1.0
        hands = h.get('hands')
        if hands.get('player1') < hands.get('player2'):
            p = p0.set('player1', p0.get('player1') + pot)
        elif hands.get('player1') > hands.get('player2'):
            p = p0.set('player2', p0.get('player2') + pot)
        else:
            p = p0.set('player1', p0.get('player1') + pot / 2).set('player2', p0.get('player2') + pot / 2)
        m.set('payout', p)
        m.set('actions', h.get('actions') + [Action.call])
        m.pop('pot')
        m.pop('to_act')
        m.set('round', Round.complete)
        h1 = m.finish()
    return h1

def act_fold(h):
    with h.mutate() as m:
        y = h.get('payout')
        if h.get('to_act') == 'player1':
            p = y.set('player2', y.get('player2') + h.get('pot'))
        elif h.get('to_act') == 'player2':
            p = y.set('player1', y.get('player1') + h.get('pot'))
        else:
            print("act_fold: unrecognised player to act " + str(h.get('to_act')))
        m.set('payout', p)
        m.set('actions', h.get('actions') + [Action.fold])
        m.pop('pot')
        m.pop('to_act')
        m.set('round', Round.complete)
        h1 = m.finish()
    return h1

def act(h, a):
    if a == Action.bet:
        return act_bet(h)
    elif a == Action.call:
        return act_call(h)
    elif a == Action.fold:
        return act_fold(h)
    else: 
        print("act: unrecognised action " + str(a))

def actions(h):
    r = h.get('round')
    if r == Round.deal:
        return [Action.bet, Action.fold]
    elif r == Round.bet:
        return [Action.call, Action.fold]
    elif r == Round.complete:
        return []
    else:
        print("actions: unrecognised round " + str(r))

def is_complete(h):
    return h.get('round') == Round.complete

def get_action(h):
    d = str(h.get('hands').get(h.get('to_act')))
    z = actions(h)
    p = '{' + d + '} ' + z[0].name + ' or ' + z[1].name + '? '
    a = input(p)
    if a == 'b' and Action.bet in z:
        return Action.bet 
    elif a == 'c' and Action.call in z:
        return Action.call
    elif a == 'f' and Action.fold in z:
        return Action.fold
    else:
        return get_action(h)

    
def play(choice):
    p = 0
    while True:
        h = complete(deal(), {'player1': get_action, 'player2': choice})
        y = h.get('payout').get('player1')
        p += y
        print(str(h.get('actions')) + ' ' + str(y) + '[' + str(p) + ']')
        h = complete(deal(), {'player2': get_action, 'player1': choice})
        y = h.get('payout').get('player2')
        p += y
        print(str(h.get('actions')) + ' ' + str(y) + '[' + str(p) + ']')
        

## model

def rho(h):
    p = h.get('to_act')
    if p == 'player1':
        a = [1.0, 0.0]
    else:
        a = [0.0, 1.0]
    c = [0.0, 0.0, 0.0]
    c[h.get('hands').get(p) - 1] = 1.0
    a.extend(c)
    return a

def random_choice(_x):
    return [random.random() for _ in range(len(Action))]

def max_action(h, u):
    p = [(u[i], a) for (i, a) in enumerate(Action) if a in actions(h)]
    return max(p, key=operator.itemgetter(0))[1]

def phi(f):
    return lambda h: max_action(h, f(rho(h)))

## collector

def complete(h, s):
    if is_complete(h):
        return h
    else:
        p = h.get('to_act')
        return complete(act(h, s[p](h)), s)

def run(h, s, collector):
    if is_complete(h):
        return
    else:
        p = h.get('to_act')
        run(act(h, s[p](h)), s, collector)
        n = len(Action)
        r = [0 for _ in range(n)]
        for (i, a) in enumerate(Action):
            if a in actions(h):
                r[i] = complete(act(h, a), s).get('payout').get(p)
        collector['x'].append(rho(h))
        collector['y'].append(r)
        return

def batch(s, n):
    x = []
    y = []
    while len(y) < n:
        collector = {'x': [], 'y': []}
        run(deal(), s, collector)
        x.extend(collector['x'])
        y.extend(collector['y'])
    return x[:n], y[:n]


## "test" batch

s = {'player1': phi(random_choice), 'player2': phi(random_choice)}

batch(s, 8)

## "test" run and collector

s = {'player1': phi(random_choice), 'player2': phi(random_choice)}

h = deal()

collector = {'x': [], 'y': []}

run(h, s, collector)

collector = {'x': [], 'y': []}; run(h, s, collector); collector
 

## "test" play

play(phi(random_choice))

## "test" complete

s = {'player1': get_action, 'player2': phi(random_choice)}
s = {'player2': get_action, 'player1': phi(random_choice)}
s = {'player1': phi(random_choice), 'player2': phi(random_choice)}

complete(deal(), s)

## "test" model

h = deal()
rho(h)
u = random_choice(rho(h))
max_action(h, u)
phi(random_choice)(h)

## "test" game

h = deal()
act_bet(h)
act_bet(deal())
act_call(act_bet(h))
act_call(act_bet(deal()))
act_fold(h)
act_fold(act_bet(h))
act_call(act_bet(h))
act_call(act_bet(deal()))


### end
