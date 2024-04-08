# tickle -- counter factual regret minimisation

## one card lowball

see c.py and m.py

## next steps
 - introduce match of n hands between two players, use play against random choice (or previous model) to measure effect of training
 - what is effect of `soft_sample` in use of model??

## latest
 - nn model -- training and convergence not well understood
 - c.py -- improved version of b.py, introduce `batch` with float values ready for pytorch
 - refactor `complete` to take choice function for each player (map from players to choice functions), this will make `play` simpler (more symmetrical between players)
 - play -- play hands and keep track of winnings
 - b.py -- improved version of a.py


#### end
