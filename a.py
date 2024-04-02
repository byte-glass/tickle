# a.py


import enum
import immutables
import random

Round = enum.Enum('Round', 'deal bet complete')
Action = enum.Enum('Action', 'bet call fold')

def deal():
    return immutables.Map(round = Round.deal, hands = {'player1': random.randint(1, 3), 'player2': random.randint(1, 3)}, pot = 2, to_act = 'player1', actions = [])
    

def act_bet(h):
    with h.mutate() as m:
        m.set('to_act', 'player2')
        m.set('round', Round.bet)
        m.set('pot', h.get('pot') + 1)
        m.set('actions', h.get('actions') + [Action.bet])
        h1 = m.finish()
    return h1


def act_call(h):
    with h.mutate() as m:
        pot = h.get('pot') + 1
        hands = h.get('hands')
        if hands.get('player1') < hands.get('player2'):
            p = {'player1': pot, 'player2': 0}
        elif hands.get('player1') > hands.get('player2'):
            p = {'player1': 0, 'player2': pot}
        else:
            p = {'player1': pot // 2, 'player2': pot // 2}
        m.set('payout', p)
        m.set('actions', h.get('actions') + [Action.call])
        m.pop('pot')
        m.pop('to_act')
        m.set('round', Round.complete)
        h1 = m.finish()
    return h1


def act_fold(h):
    with h.mutate() as m:
        if h.get('to_act') == 'player1':
            p = {'player1': 0, 'player2': h.get('pot')}
        elif h.get('to_act') == 'player2':
            p = {'player1': h.get('pot'), 'player2': 0}
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



def random_choice(h, _p):
    return random.sample(actions(h), 1)[0]

def is_complete(h):
    return h.get('round') == Round.complete

def complete_hand(h, choice):
    if is_complete(h):
        return h
    else:
        return complete_hand(act(h, choice(h, h.get('to_act'))), choice)


def run(h, choice, collector):
    if is_complete(h):
        collector.update({'hand': h})
        return
    else:
        run(act(h, choice(h, h.get('to_act'))), choice, collector)
        outcomes = {a: complete_hand(act(h, a), choice).get('payout') for a in actions(h)}
        collector.update({'outcomes': [(h, outcomes)] + collector.get('outcomes')})
        return


random.seed(103)

h = deal()

collector = {'hand': None, 'outcomes': []}
run(h, random_choice, collector)


complete_hand(h, random_choice)
complete_hand(deal(), random_choice)

act_fold(h)

act_bet(h)
act_fold(act_bet(h))
act_call(act_bet(h))

act_call(act_bet(deal()))



### end
