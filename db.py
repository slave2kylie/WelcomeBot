mp={"0":"0"}

class KEYS:
    CMD_ROLE = 'cmd_role'
    EMBED_COLOR = 'embed_color'
    TEXT_MSG = 'txt_msg'
    EMBED = 'embed'
    EMBED_SET = 'embed_set'
    EMBED_CHANNEL = 'embed_channel'
    TEXT_CHANNEL = 'txt_channel'
    DM_TEXT_MSG = 'dm_txt_msg'
    DM_EMBED = 'dm_embed'
    DM_EMBED_SET = 'dm_embed_set'
    CAN_SEND_MSG = 'can_send_msg'
    CAN_SEND_DM_MSG = 'can_send_dm_msg'

class DB:
    def tst(self,s:str):
        print(s)
    def set(self,guild:str,key:str,value):
        global mp
        mp[guild+key]=value
    
    def get(self,guild:str,key:str):
        global mp
        return mp.get(guild+key)