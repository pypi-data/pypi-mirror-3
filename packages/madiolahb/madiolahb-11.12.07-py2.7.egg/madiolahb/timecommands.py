# HCE Bee
# Copyright 2009 Max Battcher. Licensed for use under the Ms-RL. See LICENSE.
from hce import max_influence, my_effected_time, other_effected_time, tick, \
    time_range, TIME_READY
from models import INFLUENCES

def _crit(self):
    for char in self.activechars:
        if char.time == 0:
            char.recovery = max(0, char.recovery - 1)
            if char.key() not in self.updated:
                self.updated.append(char.key())

def _tick(self):
    if self.game.hold:
        self.game.hold = []
        self.gameupdated = True
    if self.game.active:
        self.game.active = None
        self.game.lastinfluence = None
        self.game.lastroll = None
        self.game.cureffect = None
        self.game.curtiming = None
        self.gameupdated = True
    self.atready = []
    for char in self.activechars:
        if char.time == TIME_READY:
            self.atready.append(char)
    while not self.atready:
        self.tickselapsed += 1
        for char in self.activechars:
            char.time = tick(char.time)
            if char.time == 0 and not char.recovery:
                # The char is no longer waiting for anyone else to 0/ready
                char.time = 1
            if char.time == TIME_READY:
                self.atready.append(char)
                # Flow exerted influence will
                exerted = sum(getattr(char, inf) for inf in INFLUENCES)
                char.will_spot = exerted
                for inf in INFLUENCES:
                    setattr(char, inf, 0)
    for char in self.activechars:
        # Remove newly readied characters from a char's waiting list
        # ASSERT: It shouldn't be possible for multiple timesteps to occur?
        if char.time == 0:
            char.recovery = min(char.recovery - len(self.atready), 0)
        # Update the commit list
        if char.key() not in self.updated:
            self.updated.append(char.key())

def timing(self, subject=None, value=None, **kwargs):
    if value is None: return
    if not self._char(subject): return False

    if self.game.active:
        self.errors.append('%s is currently active' % self.game.active)
        return False

    if value.startswith('read'):
        # Ready
        maxpoise = max(max_influence(char, 'poise') for char
            in self.activechars if char.time == TIME_READY)
        if max_influence(self.char, 'poise') == maxpoise:
            self.game.active = self.char
            self.gameupdated = True
        else:
            self.errors.append('%s does not have the highest poise'
                % self.char.name)
            return False
    elif value.startswith('hold'):
        # Hold
        if (self.char.time == TIME_READY
        and self.char.key() not in self.game.hold):
            self.game.hold.append(self.char.key())
            self.gameupdated = True
            if all(char.key() in self.game.hold for char in self.activechars
                    if char.time == TIME_READY):
                self._tick()
        elif self.char.time != TIME_READY:
            self.warnings.append('%s is not ready to hold' % self.char.name)
    elif value.startswith('interrupt'):
        # Interrupt
        self.game.active = self.char
        self.gameupdated = True
    else:
        self.warnings.append('Unrecognized timing verb "%s"' % value)

def set(self, subject=None, object=None, time=None, **kwargs):
    if not self._char(subject): return False
    # Allow for character sets prior to an active character
    if self.game.active is not None:
        if not self._active(): return False

    object = self._object(object)
    if object is None: return

    if time is not None:
        if not time_range(time):
            self.errors.append("%s is out of range for a time." % time)
            return False
    else:
        # Time to guesstimate...
        if self.game.active is None:
            time = max_influence(object, 'poise')
        elif object.key() == self.char.key():
            time = my_effected_time(self.char, self.game.lastinfluence,
                self.game.curtiming)
        else:
            time, delta = other_effected_time(object.time, self.game.curtiming)
            if delta != 0:
                self.game.curtiming -= delta
                if self.game not in self.updated:
                    self.updated.append(self.game)
    
    if time == 0 or time == TIME_READY: # "Crit"
        self._crit()

    object.time = time

    if time == 0: # Set the recovery counter
        object.recovery = 0
        for char in self.activechars:
            if char.time != 0 and char.time != TIME_READY:
                object.recovery += 1

    if object == self.char:
        self._tick()

    if object.key() not in self.updated:
        self.updated.append(object.key())

# vim: ai et ts=4 sts=4 sw=4
