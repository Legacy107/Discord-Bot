import os
import shelve

# Dir
data_dir = os.path.join('..', 'data', 'data')

# Global variables
history = []
deleted_msg = []
emoji = {'oo': '<:oo:697102602650779778>', 'clap': '👏', 'face_palm': '🤦‍♂', 'tongue': '😛', 'lol': '😄', ':O': '🤯', 'music': '🎵',
         'dice1': '<:dice1:714008777942237215>',
         'dice2': '<:dice2:714008777644572754>', 'dice3': '<:dice3:714008777849831427>',
         'dice4': '<:dice4:714008778701537430>', 'dice5': '<:dice5:714008778806394922>',
         'dice6': '<:dice6:714008778764320788>', 'a': '🇦', 'b': '🇧', 'c': '🇨', 'd': '🇩', 'e': '🇪', 'f': '🇫',
         'g': '🇬', 'h': '🇭', 'i': '🇮', 'j': '🇯', 'k': '🇰', 'l': '🇱', 'm': '🇲', 'n': '🇳', 'o': '🇴', 'p': '🇵',
         'q': '🇶', 'r': '🇷', 's': '🇸', 't': '🇹', 'u': '🇺', 'v': '🇻', 'w': '🇼', 'x': '🇽', 'y': '🇾', 'z': '🇿'}
max_height = 400
max_msg = 128

def set_up():
	data = shelve.open(data_dir)
	data.setdefault('msg_history', [])
	data.setdefault('deleted_msg', [])
	data.setdefault('image', {})
	data.close()


if __name__ == '__main__':
	set_up()
