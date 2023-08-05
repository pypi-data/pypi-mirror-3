# HCE Bee
# Copyright 2009 Max Battcher. Licensed for use under the Ms-RL. See LICENSE.
from core import check_action, GUARANTEED_ROLL, INFLUENCES, max_influence, \
    max_recovery, ROLL_EFFECT
import random

def exert(lifewheel, **kwargs):
    """
    Lifewheel will is exerted to perform actions.
    """
    for inf in INFLUENCES:
        if inf in kwargs:
            if lifewheel['will'] < kwargs[inf]:
                lifewheel['warnings'].append('Not enough will to move %s to %s' % (
                    kwargs[inf], inf))
            else:
                maxinf = max_influence(lifewheel, inf)
                if kwargs[inf] > maxinf:
                    lifewheel['warnings'].append('Over-exerted: %s > %s' % (
                        kwargs[inf], maxinf))
                lifewheel['will'] -= kwargs[inf]
                lifewheel[inf] = lifewheel[inf] + kwargs[inf]

def _register_exert(subp):
    parser = subp.add_parser('exert')
    for inf in INFLUENCES:
        parser.add_argument("--%s" % inf, type=int)
    parser.set_defaults(func=exert)

def act(lifewheel, influence=None, domain=False, profession=None, **kwargs):
    """
    Performing an unopposed action
    """
    lifewheel['last_influence'] = influence
    cando, is_guaranteed = check_action(lifewheel, False, influence, heroic,
        profession)
    if not cando:
        lifewheel['errors'].append('%s does not have enough will exerted to perform.' %
            lifewheel['name'])
        return
    if is_guaranteed:
        self.game.lastroll = GUARANTEED_ROLL
    else:
        self.game.lastroll = random.randint(0, 9)
    inf = lifewheel['influence']
    maxinf = max_influence(lifewheel, influence)
    if inf > maxinf:
        # Excess influence is "spent"
        lifewheel['influence'] = maxinf
        lifewheel['will_spent'] += maxinf - inf
    self.game.cureffect, self.game.curtiming = ROLL_EFFECT[self.game.lastroll]

def _register_act(subp):
    parser = subp.add_parser('act')
    parser.add_argument('influence')
    parser.add_argument('--domain')
    parser.add_argument('--profession')
    parser.set_defaults(func=act)

def contest(lifewheel, influence=None, heroic=None, profession=None,
        object=None, **kwargs):

    # TODO: Use the object, for potential defense

    self.game.lastinfluence = influence
    cando, is_guaranteed = check_action(self.lifewheel, True, influence, heroic,
        profession)
    if not cando:
        self.errors.append('%s does not have enough will exerted to perform.' %
            self.lifewheel.name)
        return
    if is_guaranteed:
        self.game.lastroll = GUARANTEED_ROLL
    else:
        self.game.lastroll = random.randint(0, 9)
    inf = getattr(self.lifewheel, influence)
    maxinf = max_influence(self.lifewheel, influence)
    if inf > maxinf:
        # Excess influence is "spent"
        setattr(self.lifewheel, influence, maxinf)
        self.lifewheel.will_spent += maxinf - inf
        if self.lifewheel.key() not in self.updated:
            self.updated.append(self.lifewheel.key())
    self.game.cureffect, self.game.curtiming = ROLL_EFFECT[self.game.lastroll]
    self.gameupdated = True

def _register_contest(subp):
    parser = subp.add_parser('contest')
    parser.add_argument('influence')
    parser.add_argument('--domain')
    parser.add_argument('--profession')
    parser.add_argument('--object')
    parser.set_defaults(func=contest)

def lose(lifewheel, count=0, **kwargs):
    """
    Sometimes lifewheels lose ego when performances are unfavorable.
    """
    tokens = min(lifewheel['ego'], count)
    lifewheel['ego'] -= tokens
    lifewheel['ego_spilt'] += tokens
    if tokens < count:
        lifewheels['warnings'].append('%s had fewer than %s ego left.' % (
            lifewheel['name'], count))
    if lifewheel['ego'] <= 0:
        lifewheel['ego'] = 0
        lifewheel['active'] = False
        lifewheel['warnings'].append('%s has passed out.' % lifewheel['name'])

def _register_lose(subp):
    parser = subp.add_parser('lose')
    parser.add_argument('count', type=int)
    parser.set_defaults(func=lose)

def regain(lifewheel, count=None, what=None, **kwargs):
    """
    Eventually lifewheels regain
    """
    mr = max_recovery(lifewheel)
    if count is not None and count > mr:
        lifewheel['warnings'].append("%s is greater than %s's expected maximum recovery (%s)." % (
            count, lifewheel['name'], mr))
    elif count is None:
        count = mr

    if what is None:
        tokens = min(lifewheel['will_spent'], count)
        lifewheel['will_spent'] -= tokens
        lifewheel['will'] += tokens
        if count > tokens:
            what = 'ego'
            count -= tokens
    if what == 'ego':
        tokens = min(lifewheel['ego_spilt'], count)
        lifewheel['ego_spilt'] -= tokens
        lifewheel['ego'] += tokens
    elif what == 'will':
        tokens = min(lifewheel['will_spent'], count)
        lifewheel['will_spent'] -= tokens
        lifewheel['will'] += tokens

def _register_regain(subp):
    parser = subp.add_parser('regain')
    parser.add_argument('--count', type=int, default=None)
    parser.add_argument('--what', choices=('ego', 'will'), default=None)
    parser.set_defaults(func=regain)

def register_commands(subp):
    _register_exert(subp)
    _register_act(subp)
    _register_contest(subp)
    _register_lose(subp)
    _register_regain(subp)

# vim: ai et ts=4 sts=4 sw=4
