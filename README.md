# Connecting

## First time connection
Send a json object containing 'name' and 'color', both as strings.
The color can be either a word, e.g. 'red', or a hex code, e.g. '#ff0000'.
You will receive a UUID after you have sent the data, or you will receive 
False if you could not connect properly.

Example: `{'name': __STRING__, 'color', __COLOR__}`

Returns: `{'status': __BOOL__, 'result': __STRING__, 'frame', __INT__}`

## Reconnection
Send a json object containing 'UUID' as a string, where the UUID is 
the one you were provided with when you first connected.
Returns True if successful, and False if unsuccessful.

Example: `{'UUID': __STRING__}`

Returns: `{'status': __BOOL__, 'result': __BOOL__, 'frame': __INT__}`


# Commands

## Changing course
Send an object where 'command' is 'angle' and 'value' is the angle you 
want to change to, in degrees. Accepts float values. Returns True if 
successful, otherwise False.
This costs 10 energy.

Example: `{'command': 'angle', 'value', __FLOAT__}`

Returns: `{'status': __BOOL__, 'result': __BOOL__, 'frame': __INT__}`

## Shielding yourself
Send an object where 'command' is 'shield' and 'value' either True or False.
The shield will protect you from one bullet, and costs 2 energy per frame. 
Returns True if successful, otherwise False.

Example: `{'command': 'shield', 'value', __BOOL__}`

Returns: `{'status': __BOOL__, 'result': __BOOL__, 'frame': __INT__}`

## Scanning for ships
Send an object where 'command' is 'scanShips'. This returns a list of all ships 
within a 150 pixel range from you, with positions relative to you.
This costs 5 energy.

Example: `{'command': 'scanShips'}`

Returns: `{'status': __BOOL__, 'result': __POSITION__, 'frame': __INT}`
`__POSITION__ = [{'x': __FLOAT__, 'y': __FLOAT__}, {'x': __FLOAT__, 'y': __FLOAT__}, ...]`

## Boosting away
Send an object where 'command' is 'boost'. This doubles your speed for 50 frames. 
Returns True if successful, otherwise False. This costs 25 energy.

Example: `{'command': 'boost'}`

Returns: `{'status': __BOOL__, 'result': __BOOL__, 'frame': __INT__}`

## Firing your cannons
Send an object where 'command' is 'fire'. This sends out a bullet with a speed 
of 10 pixels/second, going in the same angle as you're headed. This costs 20 energy.
Returns True if successful, otherwise False.

Example: `{'command': 'fire'}`

Returns: `{'status': __BOOL__, 'result': __BOOL__, 'frame': __INT__}`

## Checking your energy
Send an object where 'command' is 'getEnergy'.
Returns your ships energy. This costs 0 energy.

Example: `{'command': 'getEnergy'}`

Returns: `{'status': __BOOL__, 'result': __INT__, 'frame': __INT__}`

## Checking your health
Send an object where 'command' is 'getHealth'.
Returns your ships health. This costs 0 energy.

Example: `{'command': 'getHealth'}`

Returns: `{'status': __BOOL__, 'result': __INT__, 'frame': __INT__}`

## Checking your location
Send an object where 'command' is 'getPosition'.
Returns your ships position on the board. This costs 0 energy.

Example: `{'command': 'getPosition'}`

Returns: `{'status': __BOOL__, 'result': {'x': __FLOAT__, 'y': __FLOAT__}, 'frame': __INT__}`

## Getting your score
Send an object where 'command' is 'getScore'.
Returns your ships score. This costs 0 energy.

Example: `{'command': 'getScore'}`

Returns: `{'status': __BOOL__, 'result': __INT__, 'frame': __INT__}`

## Checking the top-list
Send an object where 'command' is 'top10'.Returns a sorted list 
with player names and scores of the top ten players, or all players 
if the number of players is less than or equal to ten. 
This costs 0 energy.

Example: `{'command': 'top10'}`

Returns: `{'status': __BOOL__, 'result': __LIST__, 'frame': __INT__}`


# Your ship

## Ship health
Your ship will suffer damage from bullets. The ship has a maximum health of 200, 
and will repair itself if it is out of battle. If your ship has not been hit for 
the last 50 frames, it will start regaining health at a rate of 1 health point 
per frame until its health is at 200 or the ship is hit again. 

## Ship energy
You can make your ship do many things, but in order to do so you have to use 
your energy. Different commands cost different amounts of energy. The maximum 
energy is 100, and your ship will always regain 1 energy point every frame 
until the energy is at 100.

## Ship cannons
Your ship has powerful cannons that are at your service. The projectiles travel 
straight forward, at a speed of 10 pixels per second, and will deal 80 damage 
if it hits another ship. A ship is hit if the projectile hits within 10 pixels 
from the center of the ship.

## Ship rockets
Your ship has a pair of rockets that are capable of propelling you forward at 
a speed of 4 pixels per frame. The ship also has a booster rocket, and when 
activated, the speed doubles, and becomes 8 pixels per frame.

## Ship shield
Your ship has a powerful shield that will protect you from harm. Once it is 
activated, it will protect you from one incoming projectile. Once you've been 
hit the shield will be deactivated, and you have to manually reactivate it.

## Ship destruction
If your ship is destroyed, by reaching zero health, it will disappear from the 
screen for 100 frames. After that time, the ship will respawn at a random 
location, and you will lose 200 points, or your score will drop to 0 if your 
score is less than 200 points.


# Sending messages

All commands are sent as json objects, and are ended with a null byte. 
Every command gets a json object in return, which has a 'status' key, 
a 'result' key and a 'frame' key. Only one command is allowed per frame, 
and if any more are sent, only the first command will be executed. 
