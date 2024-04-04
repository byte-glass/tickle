# b.py


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
            payout = immutables.Map(player1 = 0, player2 = 0), 
            pot = 2, 
            to_act = 'player1', 
            actions = [])

def act_bet(h):
    with h.mutate() as m:
        y = h.get('payout')
        m.set('payout', y.set('player1', y.get('player1') - 1))
        m.set('pot', h.get('pot') + 1)
        m.set('actions', h.get('actions') + [Action.bet])
        m.set('to_act', 'player2')
        m.set('round', Round.bet)
        h1 = m.finish()
    return h1

def act_call(h):
    with h.mutate() as m:
        y = h.get('payout')
        p0 = y.set('player2', y.get('player2') - 1)
        pot = h.get('pot') + 1
        hands = h.get('hands')
        if hands.get('player1') < hands.get('player2'):
            p = p0.set('player1', p0.get('player1') + pot)
        elif hands.get('player1') > hands.get('player2'):
            p = p0.set('player2', p0.get('player2') + pot)
        else:
            p = p0.set('player1', p0.get('player1') + pot // 2).set('player2', p0.get('player2') + pot // 2)
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


## model

def rho(h):
    p = h.get('to_act')
    if p == 'player1':
        a = [1, 0]
    else:
        a = [0, 1]
    c = [0, 0, 0]
    c[h.get('hands').get(p) - 1] = 1
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

def complete_hand(h, choice):
    if is_complete(h):
        return h
    else:
        return complete_hand(act(h, choice(h)), choice)

### does `phi` sit inside `complete_hand`, viz

def complete(h, f):
    if is_complete(h):
        return h
    else: 
        return complete(act(h, phi(f)(h)), f)

def run(h, f, collector):
    if is_complete(h):
        collector['actions'] = h.get('actions')
        return
    else:
        run(act(h, phi(f)(h)), f, collector)
        n = len(Action)
        r = [0 for _ in range(n)]
        p = h.get('to_act')
        for (i, a) in enumerate(Action):
            if a in actions(h):
                r[i] = complete(act(h, a), f).get('payout').get(p)
        collector['Xy'].append((rho(h), r))
        return


## "test" collector

h = deal()
complete_hand(h, phi(random_choice))
complete(h, random_choice)

collector = {'actions': None, 'Xy': []}
run(h, random_choice, collector)

collector = {'actions': None, 'Xy': []}; run(deal(), random_choice, collector); collector


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
