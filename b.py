# b.py


import enum
import immutables
import random


Round = enum.Enum('Round', 'deal bet complete')
Action = enum.Enum('Action', 'bet call fold')

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


# h = deal()
# 
# act_bet(h)
# 
# act_bet(deal())
# 
# act_call(act_bet(h))
# 
# act_call(act_bet(deal()))
# 
# act_fold(h)
# 
# act_fold(act_bet(h))
# 
# act_call(act_bet(h))
# 
# act_call(act_bet(deal()))


### end
