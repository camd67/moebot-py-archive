add_channel_query = '''
    INSERT INTO channels ( channel_id )
    VALUES (:channelId)
'''

get_command_id_query = '''
    SELECT id FROM channels
    WHERE command_id = :commandId
    COLLATE NOCASE
'''

add_user_query = '''
    INSERT INTO users ( user_id )
    VALUES ( :userId )
'''

insert_permitted_query = '''
    INSERT INTO channel_command_permissions
    ( channel_id, command, user_id )
    VALUES (:channelId, :commandId, :user)
'''

check_permitted_query = '''
    SELECT * FROM channel_command_permissions
    WHERE channel_id = :channelId COLLATE NOCASE
    AND command = :commandId COLLATE NOCASE
'''